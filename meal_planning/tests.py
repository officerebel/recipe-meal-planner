from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, timedelta
from recipes.models import Recipe, Ingredient, RecipeSource
from .models import MealPlan, DailyMeals, MealAssignment, ShoppingList, ShoppingListItem, MealType
from .services import MealPlanningService, ShoppingListService


class MealPlanModelTest(TestCase):
    """Test MealPlan model functionality"""
    
    def setUp(self):
        self.meal_plan = MealPlan.objects.create(
            name="Weekly Plan",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 7)
        )
    
    def test_meal_plan_creation(self):
        """Test meal plan is created correctly"""
        self.assertEqual(self.meal_plan.name, "Weekly Plan")
        self.assertEqual(self.meal_plan.start_date, date(2024, 1, 1))
        self.assertEqual(self.meal_plan.end_date, date(2024, 1, 7))
    
    def test_meal_plan_str(self):
        """Test meal plan string representation"""
        expected = "Weekly Plan (2024-01-01 to 2024-01-07)"
        self.assertEqual(str(self.meal_plan), expected)


class MealAssignmentModelTest(TestCase):
    """Test MealAssignment model functionality"""
    
    def setUp(self):
        self.recipe = Recipe.objects.create(
            title="Test Recipe",
            servings=4,
            source=RecipeSource.MANUAL
        )
        
        self.meal_plan = MealPlan.objects.create(
            name="Test Plan",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 7)
        )
        
        self.daily_meals = DailyMeals.objects.create(
            meal_plan=self.meal_plan,
            date=date(2024, 1, 1)
        )
        
        self.assignment = MealAssignment.objects.create(
            daily_meals=self.daily_meals,
            recipe=self.recipe,
            meal_type=MealType.DINNER,
            servings_planned=6
        )
    
    def test_assignment_creation(self):
        """Test meal assignment is created correctly"""
        self.assertEqual(self.assignment.recipe, self.recipe)
        self.assertEqual(self.assignment.meal_type, MealType.DINNER)
        self.assertEqual(self.assignment.servings_planned, 6)
    
    def test_effective_servings(self):
        """Test effective servings calculation"""
        self.assertEqual(self.assignment.effective_servings, 6)
        
        # Test with no servings planned (should use recipe servings)
        assignment_no_planned = MealAssignment.objects.create(
            daily_meals=self.daily_meals,
            recipe=self.recipe,
            meal_type=MealType.LUNCH
        )
        self.assertEqual(assignment_no_planned.effective_servings, 4)
    
    def test_assignment_str(self):
        """Test meal assignment string representation"""
        expected = "Test Recipe for dinner on 2024-01-01"
        self.assertEqual(str(self.assignment), expected)


class MealPlanningServiceTest(TestCase):
    """Test MealPlanningService functionality"""
    
    def setUp(self):
        self.service = MealPlanningService()
        self.recipe = Recipe.objects.create(
            title="Service Test Recipe",
            servings=2,
            source=RecipeSource.MANUAL
        )
    
    def test_create_meal_plan(self):
        """Test meal plan creation with daily slots"""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 3)
        
        meal_plan = self.service.create_meal_plan(
            name="Service Test Plan",
            start_date=start_date,
            end_date=end_date
        )
        
        self.assertEqual(meal_plan.name, "Service Test Plan")
        self.assertEqual(meal_plan.start_date, start_date)
        self.assertEqual(meal_plan.end_date, end_date)
        
        # Check that daily meals were created
        daily_meals = meal_plan.daily_meals.all()
        self.assertEqual(daily_meals.count(), 3)  # 3 days
        
        dates = [dm.date for dm in daily_meals]
        self.assertIn(date(2024, 1, 1), dates)
        self.assertIn(date(2024, 1, 2), dates)
        self.assertIn(date(2024, 1, 3), dates)
    
    def test_create_meal_plan_invalid_dates(self):
        """Test meal plan creation with invalid dates"""
        with self.assertRaises(ValueError):
            self.service.create_meal_plan(
                name="Invalid Plan",
                start_date=date(2024, 1, 7),
                end_date=date(2024, 1, 1)  # End before start
            )
    
    def test_assign_meal(self):
        """Test meal assignment"""
        meal_plan = self.service.create_meal_plan(
            name="Assignment Test",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 1)
        )
        
        assignment = self.service.assign_meal(
            meal_plan_id=str(meal_plan.id),
            date=date(2024, 1, 1),
            recipe_id=str(self.recipe.id),
            meal_type=MealType.BREAKFAST,
            servings_planned=3,
            notes="Test notes"
        )
        
        self.assertEqual(assignment.recipe, self.recipe)
        self.assertEqual(assignment.meal_type, MealType.BREAKFAST)
        self.assertEqual(assignment.servings_planned, 3)
        self.assertEqual(assignment.notes, "Test notes")
    
    def test_assign_meal_outside_date_range(self):
        """Test meal assignment outside meal plan date range"""
        meal_plan = self.service.create_meal_plan(
            name="Range Test",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 1)
        )
        
        with self.assertRaises(ValueError):
            self.service.assign_meal(
                meal_plan_id=str(meal_plan.id),
                date=date(2024, 1, 2),  # Outside range
                recipe_id=str(self.recipe.id),
                meal_type=MealType.DINNER
            )
    
    def test_remove_meal_assignment(self):
        """Test meal assignment removal"""
        meal_plan = self.service.create_meal_plan(
            name="Removal Test",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 1)
        )
        
        assignment = self.service.assign_meal(
            meal_plan_id=str(meal_plan.id),
            date=date(2024, 1, 1),
            recipe_id=str(self.recipe.id),
            meal_type=MealType.LUNCH
        )
        
        # Remove the assignment
        removed = self.service.remove_meal_assignment(str(assignment.id))
        self.assertTrue(removed)
        
        # Verify it's gone
        self.assertFalse(MealAssignment.objects.filter(id=assignment.id).exists())
    
    def test_get_meal_plan_summary(self):
        """Test meal plan summary generation"""
        meal_plan = self.service.create_meal_plan(
            name="Summary Test",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 2)
        )
        
        # Add some assignments
        self.service.assign_meal(
            meal_plan_id=str(meal_plan.id),
            date=date(2024, 1, 1),
            recipe_id=str(self.recipe.id),
            meal_type=MealType.BREAKFAST
        )
        
        self.service.assign_meal(
            meal_plan_id=str(meal_plan.id),
            date=date(2024, 1, 1),
            recipe_id=str(self.recipe.id),
            meal_type=MealType.DINNER
        )
        
        summary = self.service.get_meal_plan_summary(str(meal_plan.id))
        
        self.assertEqual(summary['total_days'], 2)
        self.assertEqual(summary['total_assignments'], 2)
        self.assertEqual(summary['unique_recipes'], 1)
        self.assertEqual(summary['meal_type_counts']['breakfast'], 1)
        self.assertEqual(summary['meal_type_counts']['dinner'], 1)


class ShoppingListServiceTest(TestCase):
    """Test ShoppingListService functionality"""
    
    def setUp(self):
        self.service = ShoppingListService()
        
        # Create a recipe with ingredients
        self.recipe = Recipe.objects.create(
            title="Shopping Test Recipe",
            servings=4,
            source=RecipeSource.MANUAL
        )
        
        Ingredient.objects.create(
            recipe=self.recipe,
            name="Tomatoes",
            amount="2 cups",
            unit="cups",
            category="produce"
        )
        
        Ingredient.objects.create(
            recipe=self.recipe,
            name="Cheese",
            amount="1 cup",
            unit="cup",
            category="dairy"
        )
        
        # Create meal plan with assignment
        meal_planning_service = MealPlanningService()
        self.meal_plan = meal_planning_service.create_meal_plan(
            name="Shopping Test Plan",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 1)
        )
        
        meal_planning_service.assign_meal(
            meal_plan_id=str(self.meal_plan.id),
            date=date(2024, 1, 1),
            recipe_id=str(self.recipe.id),
            meal_type=MealType.DINNER
        )
    
    def test_generate_shopping_list(self):
        """Test shopping list generation"""
        shopping_list = self.service.generate_shopping_list(
            name="Test Shopping List",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 1),
            meal_plan_ids=[str(self.meal_plan.id)]
        )
        
        self.assertEqual(shopping_list.name, "Test Shopping List")
        self.assertEqual(shopping_list.items.count(), 2)  # Tomatoes and Cheese
        
        # Check that meal plan is linked
        self.assertIn(self.meal_plan, shopping_list.meal_plans.all())
        
        # Check ingredients are present
        ingredient_names = [item.ingredient_name for item in shopping_list.items.all()]
        self.assertIn("Tomatoes", ingredient_names)
        self.assertIn("Cheese", ingredient_names)
    
    def test_mark_item_purchased(self):
        """Test marking shopping list items as purchased"""
        shopping_list = self.service.generate_shopping_list(
            name="Purchase Test",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 1),
            meal_plan_ids=[str(self.meal_plan.id)]
        )
        
        item = shopping_list.items.first()
        self.assertFalse(item.purchased)
        
        # Mark as purchased
        updated = self.service.mark_item_purchased(str(item.id), True)
        self.assertTrue(updated)
        
        item.refresh_from_db()
        self.assertTrue(item.purchased)
        self.assertIsNotNone(item.purchased_at)
        
        # Mark as unpurchased
        updated = self.service.mark_item_purchased(str(item.id), False)
        self.assertTrue(updated)
        
        item.refresh_from_db()
        self.assertFalse(item.purchased)
        self.assertIsNone(item.purchased_at)


class MealPlanAPITest(APITestCase):
    """Test MealPlan API endpoints"""
    
    def setUp(self):
        self.recipe = Recipe.objects.create(
            title="API Test Recipe",
            servings=2,
            source=RecipeSource.MANUAL
        )
    
    def test_create_meal_plan(self):
        """Test POST /api/meal-plans/"""
        url = reverse('mealplan-list')
        data = {
            'name': 'API Test Plan',
            'start_date': '2024-01-01',
            'end_date': '2024-01-03'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'API Test Plan')
        
        # Verify meal plan was created in database
        meal_plan = MealPlan.objects.get(id=response.data['id'])
        self.assertEqual(meal_plan.name, 'API Test Plan')
        self.assertEqual(meal_plan.daily_meals.count(), 3)  # 3 days
    
    def test_assign_meal_to_plan(self):
        """Test POST /api/meal-plans/{id}/assign-meal/"""
        # Create meal plan first
        meal_plan = MealPlan.objects.create(
            name="Assignment Test",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 1)
        )
        
        url = reverse('mealplan-assign-meal', kwargs={'pk': meal_plan.id})
        data = {
            'date': '2024-01-01',
            'recipe_id': str(self.recipe.id),
            'meal_type': 'breakfast',
            'servings_planned': 3,
            'notes': 'API test notes'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['meal_type'], 'breakfast')
        self.assertEqual(response.data['servings_planned'], 3)
        self.assertEqual(response.data['notes'], 'API test notes')
    
    def test_get_meal_plan_summary(self):
        """Test GET /api/meal-plans/{id}/summary/"""
        meal_plan = MealPlan.objects.create(
            name="Summary Test",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 2)
        )
        
        url = reverse('mealplan-summary', kwargs={'pk': meal_plan.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Summary Test')
        self.assertEqual(response.data['total_days'], 2)
        self.assertEqual(response.data['total_assignments'], 0)


class ShoppingListAPITest(APITestCase):
    """Test ShoppingList API endpoints"""
    
    def setUp(self):
        # Create recipe with ingredients
        self.recipe = Recipe.objects.create(
            title="Shopping API Recipe",
            servings=4,
            source=RecipeSource.MANUAL
        )
        
        Ingredient.objects.create(
            recipe=self.recipe,
            name="Test Ingredient",
            amount="1 cup"
        )
        
        # Create meal plan
        self.meal_plan = MealPlan.objects.create(
            name="Shopping API Plan",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 1)
        )
    
    def test_generate_shopping_list(self):
        """Test POST /api/shopping-lists/"""
        url = reverse('shoppinglist-list')
        data = {
            'name': 'API Shopping List',
            'start_date': '2024-01-01',
            'end_date': '2024-01-01',
            'meal_plan_ids': [str(self.meal_plan.id)]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'API Shopping List')
        
        # Verify shopping list was created
        shopping_list = ShoppingList.objects.get(id=response.data['id'])
        self.assertEqual(shopping_list.name, 'API Shopping List')
    
    def test_get_shopping_list_by_category(self):
        """Test GET /api/shopping-lists/{id}/by-category/"""
        shopping_list = ShoppingList.objects.create(
            name="Category Test",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 1)
        )
        
        url = reverse('shoppinglist-by-category', kwargs={'pk': shopping_list.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)