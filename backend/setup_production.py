#!/usr/bin/env python3
"""
Setup production database with sample data
"""
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recipe_meal_planner.settings')
django.setup()

from django.contrib.auth.models import User
from recipes.models import Recipe, Ingredient, Instruction
from families.models import Family, FamilyMember

def create_demo_user():
    """Create demo user"""
    try:
        user, created = User.objects.get_or_create(
            email='demo@example.com',
            defaults={
                'username': 'demo_user',
                'first_name': 'Demo',
                'last_name': 'User',
                'is_active': True
            }
        )
        user.set_password('demo123')
        user.save()
        print(f"Demo user {'created' if created else 'updated'}: {user.email}")
        return user
    except Exception as e:
        print(f"Error creating demo user: {e}")
        return None

def create_sample_recipes(user):
    """Create sample recipes"""
    recipes_data = [
        {
            'title': 'Chocolate Chip Cookies',
            'description': 'Delicious homemade chocolate chip cookies',
            'prep_time': 15,
            'cook_time': 12,
            'servings': 24,
            'categories': ['Dessert', 'Baking'],
            'ingredients': [
                '2 1/4 cups all-purpose flour',
                '1 tsp baking soda',
                '1 tsp salt',
                '1 cup butter, softened',
                '3/4 cup granulated sugar',
                '3/4 cup brown sugar',
                '2 large eggs',
                '2 tsp vanilla extract',
                '2 cups chocolate chips'
            ],
            'instructions': [
                'Preheat oven to 375°F (190°C).',
                'Mix flour, baking soda, and salt in a bowl.',
                'Cream butter and sugars until fluffy.',
                'Beat in eggs and vanilla.',
                'Gradually mix in flour mixture.',
                'Stir in chocolate chips.',
                'Drop rounded tablespoons on ungreased cookie sheets.',
                'Bake 9-11 minutes until golden brown.',
                'Cool on baking sheet for 2 minutes.',
                'Transfer to wire rack to cool completely.'
            ]
        },
        {
            'title': 'Spaghetti Carbonara',
            'description': 'Classic Italian pasta dish with eggs, cheese, and pancetta',
            'prep_time': 10,
            'cook_time': 15,
            'servings': 4,
            'categories': ['Italian', 'Pasta', 'Dinner'],
            'ingredients': [
                '400g spaghetti',
                '200g pancetta or guanciale, diced',
                '4 large eggs',
                '100g Pecorino Romano cheese, grated',
                '50g Parmesan cheese, grated',
                'Black pepper to taste',
                'Salt for pasta water'
            ],
            'instructions': [
                'Bring a large pot of salted water to boil.',
                'Cook spaghetti according to package directions.',
                'Meanwhile, cook pancetta in a large skillet until crispy.',
                'In a bowl, whisk eggs with grated cheeses and black pepper.',
                'Reserve 1 cup pasta cooking water, then drain pasta.',
                'Add hot pasta to the skillet with pancetta.',
                'Remove from heat and quickly stir in egg mixture.',
                'Add pasta water gradually until creamy.',
                'Serve immediately with extra cheese and pepper.'
            ]
        },
        {
            'title': 'Chicken Stir Fry',
            'description': 'Quick and healthy chicken stir fry with vegetables',
            'prep_time': 20,
            'cook_time': 10,
            'servings': 4,
            'categories': ['Asian', 'Healthy', 'Quick'],
            'ingredients': [
                '500g chicken breast, sliced thin',
                '2 tbsp vegetable oil',
                '1 bell pepper, sliced',
                '1 onion, sliced',
                '2 carrots, julienned',
                '200g broccoli florets',
                '3 cloves garlic, minced',
                '2 tbsp soy sauce',
                '1 tbsp oyster sauce',
                '1 tsp sesame oil',
                'Rice for serving'
            ],
            'instructions': [
                'Heat oil in a large wok or skillet over high heat.',
                'Add chicken and cook until no longer pink.',
                'Add garlic and cook for 30 seconds.',
                'Add vegetables and stir-fry for 3-4 minutes.',
                'Mix soy sauce, oyster sauce, and sesame oil.',
                'Add sauce to the wok and toss everything together.',
                'Cook for another 1-2 minutes until vegetables are tender-crisp.',
                'Serve over steamed rice.'
            ]
        }
    ]
    
    created_count = 0
    for recipe_data in recipes_data:
        try:
            recipe, created = Recipe.objects.get_or_create(
                title=recipe_data['title'],
                user=user,
                defaults={
                    'description': recipe_data['description'],
                    'prep_time': recipe_data['prep_time'],
                    'cook_time': recipe_data['cook_time'],
                    'servings': recipe_data['servings'],
                    'categories': recipe_data['categories']
                }
            )
            
            if created:
                # Add ingredients
                for i, ingredient_text in enumerate(recipe_data['ingredients']):
                    Ingredient.objects.create(
                        recipe=recipe,
                        text=ingredient_text,
                        order=i + 1
                    )
                
                # Add instructions
                for i, instruction_text in enumerate(recipe_data['instructions']):
                    Instruction.objects.create(
                        recipe=recipe,
                        text=instruction_text,
                        order=i + 1
                    )
                
                created_count += 1
                print(f"Created recipe: {recipe.title}")
            else:
                print(f"Recipe already exists: {recipe.title}")
                
        except Exception as e:
            print(f"Error creating recipe {recipe_data['title']}: {e}")
    
    print(f"Created {created_count} new recipes")

def main():
    print("Setting up production database...")
    
    # Create demo user
    user = create_demo_user()
    if not user:
        print("Failed to create demo user")
        return
    
    # Create sample recipes
    create_sample_recipes(user)
    
    print("Production setup complete!")

if __name__ == "__main__":
    main()