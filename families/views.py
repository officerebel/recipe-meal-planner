from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

from .models import Family, FamilyMember, FamilyInvitation
from .serializers import (
    FamilySerializer, FamilyListSerializer, FamilyMemberSerializer,
    FamilyInvitationSerializer, InviteMemberSerializer, AcceptInvitationSerializer
)

logger = logging.getLogger(__name__)


class FamilyViewSet(viewsets.ModelViewSet):
    """ViewSet for managing families"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FamilyListSerializer
        return FamilySerializer
    
    def get_queryset(self):
        """Return families where user is a member"""
        return Family.objects.filter(
            members__user=self.request.user
        ).distinct()
    
    def perform_create(self, serializer):
        """Create family and add creator as admin"""
        with transaction.atomic():
            family = serializer.save()
            
            # Add creator as admin
            FamilyMember.objects.create(
                family=family,
                user=self.request.user,
                role='admin',
                can_invite_members=True
            )
            
            logger.info(f"Family '{family.name}' created by {self.request.user.username}")
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get family members"""
        family = self.get_object()
        members = family.members.all()
        serializer = FamilyMemberSerializer(members, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def invite_member(self, request, pk=None):
        """Invite a new family member"""
        family = self.get_object()
        
        # Check if user has permission to invite
        try:
            member = family.members.get(user=request.user)
            if not member.has_permission('invite_members'):
                return Response(
                    {'error': 'Je hebt geen toestemming om leden uit te nodigen'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except FamilyMember.DoesNotExist:
            return Response(
                {'error': 'Je bent geen lid van deze familie'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = InviteMemberSerializer(
            data=request.data,
            context={'family': family}
        )
        
        if serializer.is_valid():
            # Create invitation
            invitation = FamilyInvitation.objects.create(
                family=family,
                invited_by=request.user,
                email=serializer.validated_data['email'],
                role=serializer.validated_data['role'],
                message=serializer.validated_data.get('message', ''),
                expires_at=timezone.now() + timedelta(days=7)
            )
            
            # Send invitation email
            try:
                self._send_invitation_email(invitation)
                logger.info(f"Invitation email sent to {invitation.email} for family {family.name}")
            except Exception as e:
                logger.error(f"Failed to send invitation email: {e}")
                # Don't fail the invitation creation if email fails
            
            return Response(
                FamilyInvitationSerializer(invitation).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def update_member(self, request, pk=None):
        """Update family member role/permissions"""
        family = self.get_object()
        member_id = request.data.get('member_id')
        
        if not member_id:
            return Response(
                {'error': 'member_id is verplicht'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is admin
        try:
            requesting_member = family.members.get(user=request.user)
            if requesting_member.role != 'admin':
                return Response(
                    {'error': 'Alleen beheerders kunnen leden bijwerken'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except FamilyMember.DoesNotExist:
            return Response(
                {'error': 'Je bent geen lid van deze familie'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get member to update
        try:
            member = family.members.get(id=member_id)
        except FamilyMember.DoesNotExist:
            return Response(
                {'error': 'Lid niet gevonden'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Prevent removing last admin
        if (member.role == 'admin' and 
            request.data.get('role') != 'admin' and 
            family.admin_count <= 1):
            return Response(
                {'error': 'Kan laatste beheerder niet degraderen'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = FamilyMemberSerializer(
            member, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def remove_member(self, request, pk=None):
        """Remove family member"""
        family = self.get_object()
        member_id = request.data.get('member_id')
        
        if not member_id:
            return Response(
                {'error': 'member_id is verplicht'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get member to remove
        try:
            member = family.members.get(id=member_id)
        except FamilyMember.DoesNotExist:
            return Response(
                {'error': 'Lid niet gevonden'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        requesting_member = family.members.get(user=request.user)
        
        # Users can remove themselves, admins can remove others
        if (member.user != request.user and 
            requesting_member.role != 'admin'):
            return Response(
                {'error': 'Geen toestemming om dit lid te verwijderen'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Prevent removing last admin
        if member.role == 'admin' and family.admin_count <= 1:
            return Response(
                {'error': 'Kan laatste beheerder niet verwijderen'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        member.delete()
        logger.info(f"Member {member.user.username} removed from family {family.name}")
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def invitations(self, request):
        """Get pending invitations for current user"""
        invitations = FamilyInvitation.objects.filter(
            email=request.user.email,
            status='pending'
        )
        
        serializer = FamilyInvitationSerializer(invitations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def accept_invitation(self, request):
        """Accept family invitation"""
        serializer = AcceptInvitationSerializer(data=request.data)
        
        if serializer.is_valid():
            invitation_id = serializer.validated_data['invitation_id']
            
            try:
                invitation = FamilyInvitation.objects.get(id=invitation_id)
                
                # Verify invitation is for current user
                if invitation.email != request.user.email:
                    return Response(
                        {'error': 'Deze uitnodiging is niet voor jou'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # Accept invitation
                if invitation.accept(request.user):
                    logger.info(f"User {request.user.username} accepted invitation to family {invitation.family.name}")
                    return Response(
                        {'message': 'Uitnodiging geaccepteerd!'},
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {'error': 'Kan uitnodiging niet accepteren'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
            except FamilyInvitation.DoesNotExist:
                return Response(
                    {'error': 'Uitnodiging niet gevonden'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def decline_invitation(self, request):
        """Decline family invitation"""
        invitation_id = request.data.get('invitation_id')
        
        if not invitation_id:
            return Response(
                {'error': 'invitation_id is verplicht'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            invitation = FamilyInvitation.objects.get(id=invitation_id)
            
            # Verify invitation is for current user
            if invitation.email != request.user.email:
                return Response(
                    {'error': 'Deze uitnodiging is niet voor jou'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Decline invitation
            if invitation.decline():
                logger.info(f"User {request.user.username} declined invitation to family {invitation.family.name}")
                return Response(
                    {'message': 'Uitnodiging afgewezen'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Kan uitnodiging niet afwijzen'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        except FamilyInvitation.DoesNotExist:
            return Response(
                {'error': 'Uitnodiging niet gevonden'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def create_member(self, request):
        """Create a new user and add them to a family"""
        from django.contrib.auth.models import User
        from django.contrib.auth.hashers import make_password
        
        # Get family ID from request or use user's current family
        family_id = request.data.get('family_id')
        if not family_id:
            # Get user's first family as default
            user_families = Family.objects.filter(members__user=request.user)
            if not user_families.exists():
                return Response(
                    {'error': 'Je bent geen lid van een familie'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            family = user_families.first()
        else:
            try:
                family = Family.objects.get(id=family_id)
            except Family.DoesNotExist:
                return Response(
                    {'error': 'Familie niet gevonden'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Check if user has permission to add members
        try:
            member = family.members.get(user=request.user)
            if not member.has_permission('invite_members'):
                return Response(
                    {'error': 'Je hebt geen toestemming om leden toe te voegen'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except FamilyMember.DoesNotExist:
            return Response(
                {'error': 'Je bent geen lid van deze familie'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate required fields
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        password = request.data.get('password')
        role = request.data.get('role', 'member')
        
        if not email or not first_name or not password:
            return Response(
                {'error': 'E-mail, voornaam en wachtwoord zijn verplicht'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Er bestaat al een account met dit e-mailadres'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Create new user
                user = User.objects.create(
                    username=email,  # Use email as username
                    email=email,
                    first_name=first_name,
                    last_name=request.data.get('last_name', ''),
                    password=make_password(password)
                )
                
                # Create family member
                family_member = FamilyMember.objects.create(
                    family=family,
                    user=user,
                    role=role,
                    age=request.data.get('age') if role == 'child' else None,
                    parental_controls_enabled=request.data.get('parental_controls', True) if role == 'child' else False,
                    can_invite_members=(role == 'admin'),
                    can_create_meal_plans=(role in ['admin', 'member']),
                    can_manage_recipes=(role in ['admin', 'member']),
                    can_manage_shopping_lists=(role in ['admin', 'member'])
                )
                
                logger.info(f"New family member created: {user.email} in family {family.name}")
                
                return Response({
                    'message': 'Familie lid succesvol aangemaakt',
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                    },
                    'family_member': {
                        'id': family_member.id,
                        'role': family_member.role,
                        'age': family_member.age,
                    }
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error(f"Error creating family member: {e}")
            return Response(
                {'error': 'Fout bij aanmaken familie lid'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _send_invitation_email(self, invitation):
        """Send invitation email to the invited user"""
        subject = settings.FAMILY_INVITATION_SUBJECT
        
        # Create invitation acceptance URL
        invitation_url = f"{settings.SITE_URL}/#/accept-invitation?token={invitation.id}"
        
        # Email content
        message = f"""
Hallo!

Je bent uitgenodigd om lid te worden van de familie "{invitation.family.name}" op Recipe Meal Planner!

Uitgenodigd door: {invitation.invited_by.get_full_name() or invitation.invited_by.username}
Rol: {invitation.get_role_display()}

{f'Persoonlijk bericht: {invitation.message}' if invitation.message else ''}

Klik op de onderstaande link om de uitnodiging te accepteren:
{invitation_url}

Deze uitnodiging verloopt op: {invitation.expires_at.strftime('%d-%m-%Y om %H:%M')}

Met vriendelijke groet,
Het Recipe Meal Planner Team
        """.strip()
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.FAMILY_INVITATION_FROM_EMAIL,
            recipient_list=[invitation.email],
            fail_silently=False,
        )