from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from families.models import Family, FamilyMember
from django.db import transaction
import os


@csrf_exempt
@require_http_methods(["POST"])
def setup_initial_data(request):
    """API endpoint to set up initial data"""
    
    # Only allow this on Railway
    if not os.environ.get('RAILWAY_ENVIRONMENT'):
        return JsonResponse({
            'error': 'Setup only available on Railway',
            'status': 'failed'
        }, status=403)
    
    try:
        with transaction.atomic():
            # Create admin user
            username = 'admin'
            email = 'admin@example.com'
            password = 'admin123'
            family_name = 'My Family'
            
            # Create superuser if it doesn't exist
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'is_staff': True,
                    'is_superuser': True,
                }
            )
            
            if created:
                user.set_password(password)
                user.save()
                user_status = 'created'
            else:
                user_status = 'already_exists'

            # Create family
            family, family_created = Family.objects.get_or_create(
                name=family_name,
                defaults={
                    'description': 'Default family created automatically'
                }
            )
            
            family_status = 'created' if family_created else 'already_exists'

            # Add admin as family member
            family_member, member_created = FamilyMember.objects.get_or_create(
                family=family,
                user=user,
                defaults={
                    'role': 'admin',
                    'can_create_meal_plans': True,
                    'can_manage_recipes': True,
                    'can_manage_shopping_lists': True,
                    'can_invite_members': True,
                    'can_manage_family_settings': True
                }
            )
            
            member_status = 'created' if member_created else 'already_exists'

            return JsonResponse({
                'status': 'success',
                'message': 'Initial data setup completed successfully!',
                'data': {
                    'user': {
                        'username': username,
                        'email': email,
                        'status': user_status
                    },
                    'family': {
                        'name': family.name,
                        'status': family_status
                    },
                    'family_member': {
                        'role': family_member.role,
                        'status': member_status
                    }
                },
                'login_info': {
                    'username': username,
                    'password': password,
                    'frontend_url': 'https://mealplannerfrontend-production.up.railway.app'
                }
            })
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Setup failed: {str(e)}'
        }, status=500)