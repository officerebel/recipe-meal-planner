from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from families.models import Family, FamilyMember
from django.db import transaction
import os

@csrf_exempt
def setup_data(request):
    """Simple setup endpoint that creates initial data"""
    
    # Only run on Railway
    if not os.environ.get('RAILWAY_ENVIRONMENT'):
        return JsonResponse({'error': 'Only available on Railway'}, status=403)
    
    try:
        with transaction.atomic():
            # Create admin user
            user, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@example.com',
                    'is_staff': True,
                    'is_superuser': True,
                }
            )
            
            if created:
                user.set_password('admin123')
                user.save()
            
            # Create family
            family, family_created = Family.objects.get_or_create(
                name='My Family',
                defaults={'description': 'Default family'}
            )
            
            # Add admin as family member
            member, member_created = FamilyMember.objects.get_or_create(
                family=family,
                user=user,
                defaults={
                    'role': 'admin',
                    'can_create_meal_plans': True,
                    'can_manage_recipes': True,
                    'can_manage_shopping_lists': True,
                    'can_invite_members': True
                }
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Setup completed!',
                'user_created': created,
                'family_created': family_created,
                'member_created': member_created,
                'login': {
                    'username': 'admin',
                    'password': 'admin123'
                }
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)