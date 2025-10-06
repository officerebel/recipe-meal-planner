#!/usr/bin/env python3
"""
Test script to verify shopping list name synchronization
"""

import os
import sys
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recipe_meal_planner.settings')
django.setup()

from django.contrib.auth.models import User
from meal_planning.models import MealPlan, ShoppingList
from meal_planning.services import ShoppingListService

def test_shopping_list_creation():
    """Test that shopping lists are created with the correct name"""
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    
    if created:
        print(f"Created test user: {user.username}")
    else:
        print(f"Using existing test user: {user.username}")
    
    # Create a test meal plan
    start_date = date.today()
    end_date = start_date + timedelta(days=6)
    
    meal_plan = MealPlan.objects.create(
        name=f"Test Meal Plan {start_date}",
        start_date=start_date,
        end_date=end_date,
        user=user
    )
    
    print(f"Created meal plan: {meal_plan.name}")
    
    # Test shopping list creation with custom name
    test_name = "My Custom Shopping List"
    
    service = ShoppingListService()
    shopping_list = service.generate_shopping_list(
        name=test_name,
        start_date=start_date,
        end_date=end_date,
        meal_plan_ids=[str(meal_plan.id)],
        user=user
    )
    
    print(f"Created shopping list with name: '{shopping_list.name}'")
    
    # Verify the name is correct
    assert shopping_list.name == test_name, f"Expected '{test_name}', got '{shopping_list.name}'"
    
    # Verify it's saved in the database correctly
    saved_list = ShoppingList.objects.get(id=shopping_list.id)
    assert saved_list.name == test_name, f"Database has '{saved_list.name}', expected '{test_name}'"
    
    print("✅ Shopping list name synchronization test PASSED!")
    
    # Clean up
    shopping_list.delete()
    meal_plan.delete()
    
    print("🧹 Cleaned up test data")

if __name__ == "__main__":
    try:
        test_shopping_list_creation()
        print("\n🎉 All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)