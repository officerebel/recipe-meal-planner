from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Family, FamilyMember, FamilyInvitation


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'display_name']
        read_only_fields = ['id', 'username']
    
    def get_display_name(self, obj):
        return obj.get_full_name() or obj.username


class FamilyMemberSerializer(serializers.ModelSerializer):
    """Serializer for FamilyMember model"""
    
    user = UserSerializer(read_only=True)
    display_name = serializers.ReadOnlyField()
    
    class Meta:
        model = FamilyMember
        fields = [
            'id', 'user', 'role', 'display_name',
            'can_create_meal_plans', 'can_manage_recipes', 
            'can_manage_shopping_lists', 'can_invite_members',
            'dietary_restrictions', 'favorite_cuisines',
            'joined_at', 'updated_at'
        ]
        read_only_fields = ['id', 'joined_at', 'updated_at']


class FamilySerializer(serializers.ModelSerializer):
    """Serializer for Family model"""
    
    members = FamilyMemberSerializer(many=True, read_only=True)
    member_count = serializers.ReadOnlyField()
    admin_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Family
        fields = [
            'id', 'name', 'description', 'default_servings',
            'meal_planning_start_day', 'shopping_day',
            'members', 'member_count', 'admin_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FamilyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for family lists"""
    
    member_count = serializers.ReadOnlyField()
    user_role = serializers.SerializerMethodField()
    
    class Meta:
        model = Family
        fields = [
            'id', 'name', 'description', 'member_count', 
            'user_role', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_user_role(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                member = obj.members.get(user=request.user)
                return member.role
            except FamilyMember.DoesNotExist:
                return None
        return None


class FamilyInvitationSerializer(serializers.ModelSerializer):
    """Serializer for FamilyInvitation model"""
    
    family_name = serializers.CharField(source='family.name', read_only=True)
    invited_by_name = serializers.CharField(source='invited_by.get_full_name', read_only=True)
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = FamilyInvitation
        fields = [
            'id', 'family', 'family_name', 'invited_by', 'invited_by_name',
            'email', 'role', 'status', 'message', 'is_expired',
            'created_at', 'expires_at', 'responded_at'
        ]
        read_only_fields = [
            'id', 'invited_by', 'status', 'responded_at', 'created_at'
        ]


class InviteMemberSerializer(serializers.Serializer):
    """Serializer for inviting family members"""
    
    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=FamilyMember.ROLE_CHOICES,
        default='member'
    )
    message = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500
    )
    
    def validate_email(self, value):
        """Validate email is not already a family member"""
        family = self.context.get('family')
        if family:
            # Check if user with this email is already a member
            try:
                user = User.objects.get(email=value)
                if family.members.filter(user=user).exists():
                    raise serializers.ValidationError(
                        "Deze gebruiker is al lid van de familie."
                    )
            except User.DoesNotExist:
                pass
            
            # Check if there's already a pending invitation
            if family.invitations.filter(
                email=value, 
                status='pending'
            ).exists():
                raise serializers.ValidationError(
                    "Er is al een uitnodiging verstuurd naar dit e-mailadres."
                )
        
        return value


class AcceptInvitationSerializer(serializers.Serializer):
    """Serializer for accepting family invitations"""
    
    invitation_id = serializers.UUIDField()
    
    def validate_invitation_id(self, value):
        """Validate invitation exists and is valid"""
        try:
            invitation = FamilyInvitation.objects.get(id=value)
            
            if invitation.status != 'pending':
                raise serializers.ValidationError(
                    "Deze uitnodiging is niet meer geldig."
                )
            
            if invitation.is_expired:
                raise serializers.ValidationError(
                    "Deze uitnodiging is verlopen."
                )
            
            return value
            
        except FamilyInvitation.DoesNotExist:
            raise serializers.ValidationError(
                "Uitnodiging niet gevonden."
            )