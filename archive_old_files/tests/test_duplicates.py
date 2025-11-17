#!/usr/bin/env python
"""
Test script to demonstrate duplicate removal functionality
"""
import os
import sys
import django

# Add the backend directory to the Python path
sys.path.insert(0, 'backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recipe_meal_planner.settings')
django.setup()

from meal_planning.models import ShoppingList, ShoppingListItem
from meal_planning.services import ShoppingListService
from django.contrib.auth.models import User

def test_duplicate_removal():
    """Test the duplicate removal functionality"""
    
    print("🔍 Testing Duplicate Removal Functionality")
    print("=" * 50)
    
    # Get all shopping lists
    shopping_lists = ShoppingList.objects.all()
    print(f"📋 Found {shopping_lists.count()} shopping lists")
    
    if shopping_lists.count() == 0:
        print("❌ No shopping lists found. Create a shopping list first.")
        return
    
    # Show details for each shopping list
    for shopping_list in shopping_lists:
        print(f"\n📝 Shopping List: {shopping_list.name}")
        print(f"   📅 Date Range: {shopping_list.start_date} to {shopping_list.end_date}")
        print(f"   👤 Owner: {shopping_list.user.username}")
        
        # Get all items
        items = shopping_list.items.all().order_by('ingredient_name')
        print(f"   📦 Total Items: {items.count()}")
        
        # Group items by ingredient name to show duplicates
        from collections import defaultdict
        ingredient_groups = defaultdict(list)
        
        for item in items:
            normalized_name = item.ingredient_name.lower().strip()
            ingredient_groups[normalized_name].append(item)
        
        # Show duplicates
        duplicates_found = 0
        for normalized_name, item_list in ingredient_groups.items():
            if len(item_list) > 1:
                duplicates_found += len(item_list) - 1
                print(f"   🔄 DUPLICATE: '{item_list[0].ingredient_name}' appears {len(item_list)} times")
                for i, item in enumerate(item_list):
                    print(f"      {i+1}. Amount: {item.total_amount}")
        
        if duplicates_found == 0:
            print("   ✅ No duplicates found")
        else:
            print(f"   ⚠️  Found {duplicates_found} duplicate items")
            
            # Test the duplicate removal
            print(f"\n🧹 Testing duplicate removal for '{shopping_list.name}'...")
            service = ShoppingListService()
            
            try:
                removed_count = service.remove_duplicates(str(shopping_list.id))
                print(f"   ✅ Successfully removed {removed_count} duplicate items")
                
                # Show updated count
                updated_items = shopping_list.items.all()
                print(f"   📦 Updated Item Count: {updated_items.count()}")
                
            except Exception as e:
                print(f"   ❌ Error removing duplicates: {str(e)}")

if __name__ == "__main__":
    test_duplicate_removal()