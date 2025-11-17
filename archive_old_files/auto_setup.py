#!/usr/bin/env python
"""
Auto-setup script that runs on Railway startup
This will automatically create the admin user and family data
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recipe_meal_planner.settings')
django.setup()

from django.contrib.auth.models import User
from families.models import Family, FamilyMember
from django.db import transaction

def auto_setup():
    """Automatically set up initial data on Railway"""
    print("🚀 Auto-setup starting...")
    
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
                print(f"✅ Created superuser: {username}")
            else:
                print(f"⚠️  Superuser {username} already exists")

            # Create family
            family, family_created = Family.objects.get_or_create(
                name=family_name,
                defaults={
                    'description': f'Default family created automatically'
                }
            )
            
            if family_created:
                print(f"✅ Created family: {family.name}")
            else:
                print(f"⚠️  Family '{family.name}' already exists")

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
            
            if member_created:
                print(f"✅ Added {username} as family admin")
            else:
                print(f"⚠️  {username} is already a family member")

            print("🎉 Auto-setup completed successfully!")
            print(f"🔐 Login: {username} / {password}")
            print("✅ Roles are now available in settings!")
            
    except Exception as e:
        print(f"❌ Auto-setup failed: {e}")
        # Don't crash the app if setup fails
        pass

if __name__ == '__main__':
    # Only run auto-setup on Railway (production)
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        auto_setup()
    else:
        print("Auto-setup skipped (not on Railway)")