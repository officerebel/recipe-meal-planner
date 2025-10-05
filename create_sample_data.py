#!/usr/bin/env python
"""
Create sample data for the Recipe Meal Planner
"""
import os
import sys
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recipe_meal_planner.settings')
django.setup()

from django.contrib.auth.models import User
from recipes.models import Recipe, Ingredient, IngredientCategory
from meal_planning.models import MealPlan, DailyMeals, MealAssignment

def create_sample_data():
    print("Creating sample data...")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"Created user: {user.username}")
    
    # Create sample recipes
    recipes_data = [
        {
            'title': 'Roodfruit Smoothie Bowl',
            'description': 'Een heerlijke en voedzame smoothie bowl met rood fruit',
            'prep_time': 10,
            'cook_time': 0,
            'servings': 2,
            'categories': ['Ontbijt', 'Drank'],
            'ingredients': [
                {'name': 'Bevroren aardbeien', 'amount': '150g', 'category': IngredientCategory.PRODUCE},
                {'name': 'Bevroren frambozen', 'amount': '100g', 'category': IngredientCategory.PRODUCE},
                {'name': 'Banaan', 'amount': '1 stuk', 'category': IngredientCategory.PRODUCE},
                {'name': 'Pindakaas', 'amount': '2 eetlepels', 'category': IngredientCategory.PANTRY},
            ],
            'instructions': [
                'Mix de bevroren aardbeien, frambozen en banaan in een blender',
                'Voeg de amandelmelk toe en blend tot een dikke consistentie',
                'Giet in een kom en garneer met pindakaas'
            ]
        },
        {
            'title': 'Spaghetti Carbonara',
            'description': 'Classic Italian pasta dish',
            'prep_time': 15,
            'cook_time': 20,
            'servings': 4,
            'categories': ['Hoofdgerecht', 'Pasta'],
            'ingredients': [
                {'name': 'Spaghetti', 'amount': '400g', 'category': IngredientCategory.PANTRY},
                {'name': 'Bacon', 'amount': '200g', 'category': IngredientCategory.MEAT},
                {'name': 'Eggs', 'amount': '3 pieces', 'category': IngredientCategory.DAIRY},
                {'name': 'Parmesan cheese', 'amount': '100g', 'category': IngredientCategory.DAIRY},
            ],
            'instructions': [
                'Cook spaghetti according to package instructions',
                'Fry bacon until crispy',
                'Mix eggs with parmesan cheese',
                'Combine hot pasta with bacon and egg mixture'
            ]
        },
        {
            'title': 'Greek Salad',
            'description': 'Fresh Mediterranean salad',
            'prep_time': 15,
            'cook_time': 0,
            'servings': 2,
            'categories': ['Salade', 'Lunch'],
            'ingredients': [
                {'name': 'Tomatoes', 'amount': '3 pieces', 'category': IngredientCategory.PRODUCE},
                {'name': 'Cucumber', 'amount': '1 piece', 'category': IngredientCategory.PRODUCE},
                {'name': 'Feta cheese', 'amount': '150g', 'category': IngredientCategory.DAIRY},
                {'name': 'Olives', 'amount': '100g', 'category': IngredientCategory.PANTRY},
            ],
            'instructions': [
                'Chop tomatoes and cucumber',
                'Add feta cheese and olives',
                'Dress with olive oil and herbs'
            ]
        }
    ]
    
    created_recipes = []
    for recipe_data in recipes_data:
        recipe, created = Recipe.objects.get_or_create(
            title=recipe_data['title'],
            user=user,
            defaults={
                'description': recipe_data['description'],
                'prep_time': recipe_data['prep_time'],
                'cook_time': recipe_data['cook_time'],
                'servings': recipe_data['servings'],
                'categories': recipe_data['categories'],
                'instructions': recipe_data['instructions']
            }
        )
        
        if created:
            print(f"Created recipe: {recipe.title}")
            
            # Add ingredients
            for ing_data in recipe_data['ingredients']:
                ingredient = Ingredient.objects.create(
                    recipe=recipe,
                    name=ing_data['name'],
                    amount=ing_data['amount'],
                    category=ing_data['category']
                )
        
        created_recipes.append(recipe)
    
    # Create sample meal plans
    today = date.today()
    next_week = today + timedelta(days=7)
    
    meal_plans_data = [
        {
            'name': 'Weekly Meal Plan',
            'start_date': today,
            'end_date': next_week,
        },
        {
            'name': 'Healthy January',
            'start_date': date(2025, 1, 1),
            'end_date': date(2025, 1, 31),
        }
    ]
    
    for mp_data in meal_plans_data:
        meal_plan, created = MealPlan.objects.get_or_create(
            name=mp_data['name'],
            user=user,
            defaults={
                'start_date': mp_data['start_date'],
                'end_date': mp_data['end_date']
            }
        )
        
        if created:
            print(f"Created meal plan: {meal_plan.name}")
            
            # Create daily meals for the first few days
            current_date = mp_data['start_date']
            for i in range(min(3, (mp_data['end_date'] - mp_data['start_date']).days + 1)):
                daily_meals, _ = DailyMeals.objects.get_or_create(
                    meal_plan=meal_plan,
                    date=current_date
                )
                
                # Add some meal assignments
                if i < len(created_recipes):
                    MealAssignment.objects.get_or_create(
                        daily_meals=daily_meals,
                        recipe=created_recipes[i],
                        meal_type='breakfast',
                        defaults={'servings_planned': 2}
                    )
                
                current_date += timedelta(days=1)
    
    print("Sample data created successfully!")

if __name__ == '__main__':
    create_sample_data()