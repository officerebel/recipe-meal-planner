#!/usr/bin/env python3
"""
Test shopping list generation locally to debug the issue
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recipe_meal_planner.settings')
django.setup()

from django.contrib.auth.models import User
from meal_planning.models import ShoppingList, MealPlan
from meal_planning.services import ShoppingListService
from families.models import Family

def test_shopping_list_generation():
    """Test shopping list generation locally"""
    print("🧪 Testing Shopping List Generation Locally...")
    
    try:
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        if created:
            user.set_password('testpass')
            user.save()
            print(f"✅ Created test user: {user.username}")
        else:
            print(f"✅ Using existing test user: {user.username}")
        
        # Get or create a test family
        family, created = Family.objects.get_or_create(
            name='Test Family'
        )
        if created:
            print(f"✅ Created test family: {family.name}")
        else:
            print(f"✅ Using existing test family: {family.name}")
        
        # Test the shopping list service
        service = ShoppingListService()
        
        print("📝 Testing shopping list generation with empty meal plans...")
        shopping_list = service.generate_shopping_list(
            name="Test Shopping List",
            start_date="2024-01-01",
            end_date="2024-01-07",
            meal_plan_ids=[],
            user=user
        )
        
        print(f"✅ Successfully created shopping list: {shopping_list.name}")
        print(f"📊 Shopping list ID: {shopping_list.id}")
        print(f"👤 User: {shopping_list.user.username}")
        print(f"📅 Date range: {shopping_list.start_date} to {shopping_list.end_date}")
        
        # Test with meal plans if any exist
        meal_plans = MealPlan.objects.filter(user=user)[:2]
        if meal_plans.exists():
            print(f"\n📝 Testing with {meal_plans.count()} meal plans...")
            shopping_list2 = service.generate_shopping_list(
                name="Test Shopping List with Meals",
                start_date="2024-01-08",
                end_date="2024-01-14",
                meal_plan_ids=[str(mp.id) for mp in meal_plans],
                user=user
            )
            print(f"✅ Successfully created shopping list with meals: {shopping_list2.name}")
        else:
            print("ℹ️ No meal plans found for testing")
        
        print("\n🎉 All tests passed! Shopping list generation works locally.")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_shopping_list_generation()
    if success:
        print("\n✅ Local testing successful - issue is likely on Railway deployment")
    else:
        print("\n❌ Local testing failed - need to fix the code first")