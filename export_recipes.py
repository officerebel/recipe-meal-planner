#!/usr/bin/env python3
"""
Export recipes from local database to JSON file
"""
import os
import sys
import json
sys.path.append('backend')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recipe_meal_planner.settings')
import django
django.setup()

from recipes.models import Recipe, Ingredient
from django.contrib.auth.models import User

def export_recipes():
    """Export all recipes to JSON format"""
    print("Exporting recipes from local database...")
    
    recipes_data = []
    
    for recipe in Recipe.objects.all():
        # Get ingredients
        ingredients = []
        for ingredient in recipe.ingredients.all().order_by('order'):
            ingredients.append({
                'text': ingredient.text,
                'order': ingredient.order
            })
        
        # Get instructions (stored as JSONField)
        instructions = recipe.instructions if recipe.instructions else []
        
        recipe_data = {
            'id': str(recipe.id),
            'title': recipe.title,
            'description': recipe.description,
            'prep_time': recipe.prep_time,
            'cook_time': recipe.cook_time,
            'servings': recipe.servings,
            'categories': recipe.categories,
            'tags': recipe.tags,
            'user_email': recipe.user.email if recipe.user else None,
            'ingredients': ingredients,
            'instructions': instructions,
            'created_at': recipe.created_at.isoformat() if recipe.created_at else None,
            'updated_at': recipe.updated_at.isoformat() if recipe.updated_at else None
        }
        
        recipes_data.append(recipe_data)
        print(f"Exported: {recipe.title}")
    
    # Also export users
    users_data = []
    for user in User.objects.all():
        users_data.append({
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active
        })
    
    export_data = {
        'users': users_data,
        'recipes': recipes_data,
        'export_date': django.utils.timezone.now().isoformat()
    }
    
    # Save to JSON file
    with open('recipes_export.json', 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Exported {len(recipes_data)} recipes and {len(users_data)} users")
    print("📁 Saved to: recipes_export.json")
    
    return export_data

if __name__ == "__main__":
    export_recipes()