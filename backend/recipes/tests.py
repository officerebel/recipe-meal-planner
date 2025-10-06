from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Recipe, Ingredient, RecipeSource


class RecipeModelTest(TestCase):
    """Test Recipe model functionality"""
    
    def setUp(self):
        self.recipe = Recipe.objects.create(
            title="Test Recipe",
            description="A test recipe",
            prep_time=15,
            cook_time=30,
            servings=4,
            instructions=["Step 1", "Step 2"],
            categories=["dinner"],
            tags=["easy", "quick"],
            source=RecipeSource.MANUAL
        )
    
    def test_recipe_creation(self):
        """Test recipe is created correctly"""
        self.assertEqual(self.recipe.title, "Test Recipe")
        self.assertEqual(self.recipe.prep_time, 15)
        self.assertEqual(self.recipe.cook_time, 30)
        self.assertEqual(self.recipe.servings, 4)
        self.assertEqual(len(self.recipe.instructions), 2)
        self.assertEqual(len(self.recipe.categories), 1)
        self.assertEqual(len(self.recipe.tags), 2)
    
    def test_recipe_str(self):
        """Test recipe string representation"""
        self.assertEqual(str(self.recipe), "Test Recipe")
    
    def test_ingredient_count(self):
        """Test ingredient count property"""
        self.assertEqual(self.recipe.ingredient_count, 0)
        
        # Add an ingredient
        Ingredient.objects.create(
            recipe=self.recipe,
            name="Test Ingredient",
            amount="1 cup"
        )
        
        self.assertEqual(self.recipe.ingredient_count, 1)


class IngredientModelTest(TestCase):
    """Test Ingredient model functionality"""
    
    def setUp(self):
        self.recipe = Recipe.objects.create(
            title="Test Recipe",
            source=RecipeSource.MANUAL
        )
        self.ingredient = Ingredient.objects.create(
            recipe=self.recipe,
            name="Test Ingredient",
            amount="2 cups",
            unit="cups",
            notes="chopped"
        )
    
    def test_ingredient_creation(self):
        """Test ingredient is created correctly"""
        self.assertEqual(self.ingredient.name, "Test Ingredient")
        self.assertEqual(self.ingredient.amount, "2 cups")
        self.assertEqual(self.ingredient.unit, "cups")
        self.assertEqual(self.ingredient.notes, "chopped")
    
    def test_ingredient_str(self):
        """Test ingredient string representation"""
        self.assertEqual(str(self.ingredient), "2 cups Test Ingredient")
        
        # Test without amount
        ingredient_no_amount = Ingredient.objects.create(
            recipe=self.recipe,
            name="Salt"
        )
        self.assertEqual(str(ingredient_no_amount), "Salt")


class RecipeAPITest(APITestCase):
    """Test Recipe API endpoints"""
    
    def setUp(self):
        self.recipe = Recipe.objects.create(
            title="API Test Recipe",
            description="A recipe for API testing",
            prep_time=10,
            cook_time=20,
            servings=2,
            instructions=["Mix ingredients", "Cook for 20 minutes"],
            categories=["lunch"],
            tags=["healthy"],
            source=RecipeSource.MANUAL
        )
        
        Ingredient.objects.create(
            recipe=self.recipe,
            name="Test Ingredient",
            amount="1 tbsp"
        )
    
    def test_get_recipes_list(self):
        """Test GET /api/recipes/"""
        url = reverse('recipe-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], "API Test Recipe")
    
    def test_get_recipe_detail(self):
        """Test GET /api/recipes/{id}/"""
        url = reverse('recipe-detail', kwargs={'pk': self.recipe.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "API Test Recipe")
        self.assertEqual(len(response.data['ingredients']), 1)
    
    def test_create_recipe(self):
        """Test POST /api/recipes/"""
        url = reverse('recipe-list')
        data = {
            'title': 'New Recipe',
            'description': 'A new recipe',
            'prep_time': 5,
            'servings': 1,
            'instructions': ['Step 1'],
            'categories': ['snack'],
            'tags': ['quick'],
            'ingredients': [
                {
                    'name': 'New Ingredient',
                    'amount': '1 piece',
                    'order': 0
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Recipe')
        self.assertEqual(len(response.data['ingredients']), 1)
        
        # Verify recipe was created in database
        recipe = Recipe.objects.get(id=response.data['id'])
        self.assertEqual(recipe.title, 'New Recipe')
        self.assertEqual(recipe.ingredients.count(), 1)
    
    def test_update_recipe(self):
        """Test PUT /api/recipes/{id}/"""
        url = reverse('recipe-detail', kwargs={'pk': self.recipe.id})
        data = {
            'title': 'Updated Recipe',
            'description': 'Updated description',
            'prep_time': 15,
            'cook_time': 25,
            'servings': 3,
            'instructions': ['Updated step 1', 'Updated step 2'],
            'categories': ['dinner'],
            'tags': ['updated'],
            'ingredients': [
                {
                    'name': 'Updated Ingredient',
                    'amount': '2 cups',
                    'order': 0
                }
            ]
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Recipe')
        self.assertEqual(len(response.data['ingredients']), 1)
        self.assertEqual(response.data['ingredients'][0]['name'], 'Updated Ingredient')
    
    def test_delete_recipe(self):
        """Test DELETE /api/recipes/{id}/"""
        url = reverse('recipe-detail', kwargs={'pk': self.recipe.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify recipe was deleted
        self.assertFalse(Recipe.objects.filter(id=self.recipe.id).exists())
    
    def test_get_statistics(self):
        """Test GET /api/recipes/statistics/"""
        url = reverse('recipe-statistics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_recipes'], 1)
        self.assertEqual(response.data['manual_recipes'], 1)
        self.assertEqual(response.data['pdf_recipes'], 0)
    
    def test_get_categories(self):
        """Test GET /api/recipes/categories/"""
        url = reverse('recipe-categories')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('lunch', response.data)
    
    def test_get_tags(self):
        """Test GET /api/recipes/tags/"""
        url = reverse('recipe-tags')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('healthy', response.data)