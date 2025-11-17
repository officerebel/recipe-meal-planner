#!/usr/bin/env python
"""
Demo script to show duplicate removal functionality with sample data
"""
import os
import sys
import django
from datetime import date, timedelta

# Add the backend directory to the Python path
sys.path.insert(0, 'backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recipe_meal_planner.settings')
django.setup()

from meal_planning.models import ShoppingList, ShoppingListItem
from meal_planning.services import ShoppingListService
from django.contrib.auth.models import User

def create_sample_shopping_list():
    """Create a sample shopping list with duplicates for testing"""
    
    print("🔧 Creating Sample Shopping List with Duplicates")
    print("=" * 50)
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        print("👤 Created test user")
    else:
        print("👤 Using existing test user")
    
    # Create a shopping list
    shopping_list = ShoppingList.objects.create(
        name="Test Shopping List with Duplicates",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=7),
        user=user
    )
    print(f"📝 Created shopping list: {shopping_list.name}")
    
    # Add items with duplicates
    sample_items = [
        ("Extra Vierge Olijfolie", "250ml", "dairy"),
        ("Aardbeien", "500g", "produce"),
        ("Extra Vierge Olijfolie", "As needed", "dairy"),  # Duplicate
        ("Bloemkoolrijst", "200g", "produce"),
        ("Aardbeien", "200g (from recipe A)", "produce"),  # Duplicate
        ("Eieren", "6 stuks", "dairy"),
        ("Extra Vierge Olijfolie", "1 tbsp", "dairy"),  # Another duplicate
    ]
    
    for name, amount, category in sample_items:
        ShoppingListItem.objects.create(
            shopping_list=shopping_list,
            ingredient_name=name,
            total_amount=amount,
            category=category
        )
    
    print(f"📦 Added {len(sample_items)} items (including duplicates)")
    
    return shopping_list

def demo_duplicate_removal():
    """Demonstrate the duplicate removal functionality"""
    
    print("\n🔍 Analyzing Shopping List")
    print("=" * 30)
    
    # Create sample data
    shopping_list = create_sample_shopping_list()
    
    # Show current items
    items = shopping_list.items.all().order_by('ingredient_name')
    print(f"\n📋 Current Items ({items.count()}):")
    for i, item in enumerate(items, 1):
        print(f"   {i}. {item.ingredient_name} - {item.total_amount}")
    
    # Group items to show duplicates
    from collections import defaultdict
    ingredient_groups = defaultdict(list)
    
    for item in items:
        normalized_name = item.ingredient_name.lower().strip()
        ingredient_groups[normalized_name].append(item)
    
    # Show duplicates
    print(f"\n🔄 Duplicate Analysis:")
    duplicates_found = 0
    for normalized_name, item_list in ingredient_groups.items():
        if len(item_list) > 1:
            duplicates_found += len(item_list) - 1
            print(f"   • '{item_list[0].ingredient_name}' appears {len(item_list)} times")
    
    print(f"   Total duplicates: {duplicates_found}")
    
    # Test the duplicate removal
    print(f"\n🧹 Removing Duplicates...")
    service = ShoppingListService()
    
    try:
        removed_count = service.remove_duplicates(str(shopping_list.id))
        print(f"   ✅ Successfully removed {removed_count} duplicate items")
        
        # Show updated items
        updated_items = shopping_list.items.all().order_by('ingredient_name')
        print(f"\n📋 Updated Items ({updated_items.count()}):")
        for i, item in enumerate(updated_items, 1):
            print(f"   {i}. {item.ingredient_name} - {item.total_amount}")
        
        print(f"\n📊 Summary:")
        print(f"   • Original items: {items.count()}")
        print(f"   • Duplicates removed: {removed_count}")
        print(f"   • Final items: {updated_items.count()}")
        
    except Exception as e:
        print(f"   ❌ Error removing duplicates: {str(e)}")
    
    # Clean up
    shopping_list.delete()
    print(f"\n🧹 Cleaned up test data")

if __name__ == "__main__":
    demo_duplicate_removal()