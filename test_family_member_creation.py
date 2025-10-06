#!/usr/bin/env python3
"""
Test family member creation locally to debug the issue
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

def test_family_member_creation():
    """Test family member creation locally"""
    print("🧪 Testing Family Member Creation Locally...")
    
    try:
        # Get or create a test user (admin)
        admin_user, created = User.objects.get_or_create(
            username='admin_user',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User'
            }
        )
        if created:
            admin_user.set_password('adminpass')
            admin_user.save()
            print(f"✅ Created admin user: {admin_user.username}")
        else:
            print(f"✅ Using existing admin user: {admin_user.username}")
        
        # Get or create a test family
        family, created = Family.objects.get_or_create(
            name='Test Family for Member Creation'
        )
        if created:
            print(f"✅ Created test family: {family.name}")
        else:
            print(f"✅ Using existing test family: {family.name}")
        
        # Create admin family member if not exists
        admin_member, created = FamilyMember.objects.get_or_create(
            family=family,
            user=admin_user,
            defaults={
                'role': 'admin',
                'can_invite_members': True,
                'can_create_meal_plans': True,
                'can_manage_recipes': True,
                'can_manage_shopping_lists': True
            }
        )
        if created:
            print(f"✅ Created admin family member")
        else:
            print(f"✅ Admin is already a family member")
        
        # Test creating a new family member
        print("\n📝 Testing new family member creation...")
        
        # Check if test member already exists
        test_email = 'newmember@example.com'
        if User.objects.filter(email=test_email).exists():
            print(f"⚠️ User with email {test_email} already exists, deleting...")
            User.objects.filter(email=test_email).delete()
        
        with transaction.atomic():
            # Create new user
            new_user = User.objects.create(
                username=test_email,  # Use email as username
                email=test_email,
                first_name='New',
                last_name='Member'
            )
            new_user.set_password('memberpass')
            new_user.save()
            print(f"✅ Created new user: {new_user.email}")
            
            # Create family member
            new_member = FamilyMember.objects.create(
                family=family,
                user=new_user,
                role='member',
                parental_controls=False,  # Fixed field name
                can_invite_members=False,
                can_create_meal_plans=True,
                can_manage_recipes=True,
                can_manage_shopping_lists=True
            )
            print(f"✅ Created family member: {new_member.user.email} in {new_member.family.name}")
            print(f"📊 Member role: {new_member.role}")
            print(f"📊 Member permissions: invite={new_member.can_invite_members}, recipes={new_member.can_manage_recipes}")
        
        print("\n🎉 Family member creation test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Error during family member creation test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_family_member_creation()
    if success:
        print("\n✅ Local family member creation works - issue might be in frontend or API")
    else:
        print("\n❌ Local family member creation failed - backend issue confirmed")