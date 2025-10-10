#!/usr/bin/env python
"""
Demo script to show recipe sharing functionality
"""
import os
import sys
import django

# Add the backend directory to the Python path
sys.path.insert(0, 'backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recipe_meal_planner.settings')
django.setup()

from recipes.models import Recipe
from django.contrib.auth.models import User
from families.models import FamilyMember

def demo_recipe_sharing():
    """Demonstrate recipe sharing functionality"""
    
    print("🔗 Recipe Sharing Demo")
    print("=" * 30)
    
    # Get the recipe
    recipe_id = '9c8c1589-bbaf-4faa-b585-c4307e7b500d'
    try:
        recipe = Recipe.objects.get(id=recipe_id)
        print(f"📝 Recipe: {recipe.title[:50]}...")
        print(f"👤 Owner: {recipe.user.username}")
        print(f"🔗 Currently shared: {recipe.is_shared_with_family}")
        
        # Check if owner is in a family
        try:
            family_member = FamilyMember.objects.get(user=recipe.user)
            print(f"👨‍👩‍👧‍👦 Family: {family_member.family.name}")
            print(f"🎭 Role: {family_member.role}")
            
            # Show current family recipes count
            family_user_ids = family_member.family.members.values_list('user_id', flat=True)
            
            personal_recipes = Recipe.objects.filter(user=recipe.user)
            family_recipes = Recipe.objects.filter(
                user_id__in=family_user_ids,
                is_shared_with_family=True
            )
            
            print(f"\n📊 Current Status:")
            print(f"   Personal recipes: {personal_recipes.count()}")
            print(f"   Shared family recipes: {family_recipes.count()}")
            
            # Demo 1: Share the recipe
            print(f"\n🔗 Sharing recipe with family...")
            recipe.is_shared_with_family = True
            recipe.save()
            print(f"   ✅ Recipe shared!")
            
            # Check updated counts
            family_recipes = Recipe.objects.filter(
                user_id__in=family_user_ids,
                is_shared_with_family=True
            )
            print(f"   📊 Shared family recipes now: {family_recipes.count()}")
            
            # Demo 2: Show what family members would see
            print(f"\n👨‍👩‍👧‍👦 What family members see:")
            for member in family_member.family.members.all():
                print(f"   - {member.user.username} ({member.role})")
                
                # Personal recipes for this member
                member_personal = Recipe.objects.filter(user=member.user)
                print(f"     Personal recipes: {member_personal.count()}")
                
                # Family recipes this member can see
                member_family = Recipe.objects.filter(
                    user_id__in=family_user_ids,
                    is_shared_with_family=True
                )
                print(f"     Family recipes: {member_family.count()}")
            
            # Demo 3: Unshare the recipe
            print(f"\n🔓 Unsharing recipe...")
            recipe.is_shared_with_family = False
            recipe.save()
            print(f"   ✅ Recipe unshared!")
            
            # Check final counts
            family_recipes = Recipe.objects.filter(
                user_id__in=family_user_ids,
                is_shared_with_family=True
            )
            print(f"   📊 Shared family recipes now: {family_recipes.count()}")
            
        except FamilyMember.DoesNotExist:
            print("❌ Recipe owner is not in a family")
            
    except Recipe.DoesNotExist:
        print(f"❌ Recipe {recipe_id} not found")

if __name__ == "__main__":
    demo_recipe_sharing()