from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from recipes.models import Recipe, MealType, IngredientCategory
import uuid


class MealPlan(models.Model):
    """Weekly meal plan"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='meal_plans',
        help_text="Owner of this meal plan"
    )
    family = models.ForeignKey(
        'families.Family',
        on_delete=models.CASCADE,
        related_name='meal_plans',
        null=True, blank=True,
        help_text="Family this meal plan belongs to (optional)"
    )
    name = models.CharField(
        max_length=200,
        help_text="Name for this meal plan (e.g., 'Week of Jan 15')"
    )
    start_date = models.DateField(help_text="Start date of the meal plan")
    end_date = models.DateField(help_text="End date of the meal plan")
    
    # Family sharing settings
    is_shared = models.BooleanField(
        default=False,
        help_text="Whether this meal plan is shared with family members"
    )
    shared_with_family = models.BooleanField(
        default=True,
        help_text="Share with all family members (when is_shared=True)"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['user', 'start_date']),
            models.Index(fields=['user', 'end_date']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"


class DailyMeals(models.Model):
    """Meals planned for a specific day"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meal_plan = models.ForeignKey(
        MealPlan,
        on_delete=models.CASCADE,
        related_name='daily_meals'
    )
    date = models.DateField(help_text="Date for these meals")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date']
        unique_together = ['meal_plan', 'date']
        indexes = [
            models.Index(fields=['meal_plan', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"Meals for {self.date}"


class MealAssignment(models.Model):
    """Assignment of a recipe to a specific meal slot"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    daily_meals = models.ForeignKey(
        DailyMeals,
        on_delete=models.CASCADE,
        related_name='meal_assignments'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='meal_assignments'
    )
    meal_type = models.CharField(
        max_length=20,
        choices=MealType.choices,
        help_text="Type of meal (breakfast, lunch, dinner, etc.)"
    )
    
    # Optional customization
    servings_planned = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1)],
        help_text="Number of servings planned (overrides recipe default)"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes for this meal assignment"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['daily_meals__date', 'meal_type']
        unique_together = ['daily_meals', 'meal_type', 'recipe']
        indexes = [
            models.Index(fields=['daily_meals', 'meal_type']),
            models.Index(fields=['recipe']),
        ]
    
    def __str__(self):
        return f"{self.recipe.title} for {self.meal_type} on {self.daily_meals.date}"
    
    @property
    def effective_servings(self):
        """Return the effective number of servings for this assignment"""
        return self.servings_planned or self.recipe.servings or 1


class ShoppingList(models.Model):
    """Shopping list generated from meal plans"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_lists',
        help_text="Owner of this shopping list"
    )
    family = models.ForeignKey(
        'families.Family',
        on_delete=models.CASCADE,
        related_name='shopping_lists',
        null=True, blank=True,
        help_text="Family this shopping list belongs to (optional)"
    )
    name = models.CharField(
        max_length=200,
        help_text="Name for this shopping list"
    )
    
    # Family sharing settings
    is_shared = models.BooleanField(
        default=False,
        help_text="Whether this shopping list is shared with family members"
    )
    
    # Date range for the shopping list
    start_date = models.DateField(help_text="Start date for meal plans to include")
    end_date = models.DateField(help_text="End date for meal plans to include")
    
    # Generation metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    meal_plans = models.ManyToManyField(
        MealPlan,
        related_name='shopping_lists',
        help_text="Meal plans included in this shopping list"
    )
    
    class Meta:
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['user', 'start_date']),
            models.Index(fields=['user', 'end_date']),
            models.Index(fields=['user', 'generated_at']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
            models.Index(fields=['generated_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"


class ShoppingListItem(models.Model):
    """Individual item in a shopping list"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shopping_list = models.ForeignKey(
        ShoppingList,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    # Ingredient information (consolidated from multiple recipes)
    ingredient_name = models.CharField(max_length=200)
    total_amount = models.CharField(
        max_length=100,
        help_text="Consolidated amount needed"
    )
    unit = models.CharField(max_length=50, blank=True)
    category = models.CharField(
        max_length=20,
        choices=IngredientCategory.choices,
        default=IngredientCategory.OTHER
    )
    
    # Shopping status
    purchased = models.BooleanField(default=False)
    purchased_at = models.DateTimeField(null=True, blank=True)
    
    # Notes and source tracking
    notes = models.TextField(blank=True)
    source_recipes = models.ManyToManyField(
        Recipe,
        related_name='shopping_list_items',
        help_text="Recipes that contributed to this shopping list item"
    )
    
    class Meta:
        ordering = ['category', 'ingredient_name']
        indexes = [
            models.Index(fields=['shopping_list', 'category']),
            models.Index(fields=['shopping_list', 'purchased']),
            models.Index(fields=['ingredient_name']),
        ]
    
    def __str__(self):
        return f"{self.ingredient_name} - {self.total_amount}"


class MealPrepSession(models.Model):
    """Meal prep session for batch cooking"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='meal_prep_sessions',
        help_text="Owner of this meal prep session"
    )
    family = models.ForeignKey(
        'families.Family',
        on_delete=models.CASCADE,
        related_name='meal_prep_sessions',
        null=True, blank=True,
        help_text="Family this meal prep session belongs to (optional)"
    )
    name = models.CharField(
        max_length=200,
        help_text="Name for this meal prep session"
    )
    
    # Family sharing settings
    is_shared = models.BooleanField(
        default=False,
        help_text="Whether this meal prep session is shared with family members"
    )
    
    # Scheduling
    scheduled_date = models.DateField(help_text="Date when meal prep is scheduled")
    estimated_duration = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Estimated duration in minutes"
    )
    
    # Status
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned'
    )
    
    # Completion tracking
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    actual_duration = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Actual duration in minutes"
    )
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'scheduled_date']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.scheduled_date}"


class MealPrepTask(models.Model):
    """Individual task within a meal prep session"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meal_prep_session = models.ForeignKey(
        MealPrepSession,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='meal_prep_tasks'
    )
    
    # Task details
    task_name = models.CharField(
        max_length=200,
        help_text="Name of the specific task (e.g., 'Chop vegetables', 'Cook rice')"
    )
    estimated_time = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Estimated time in minutes"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Order of execution within the session"
    )
    
    # Completion tracking
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    actual_time = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Actual time taken in minutes"
    )
    
    # Notes
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['order', 'id']
        indexes = [
            models.Index(fields=['meal_prep_session', 'order']),
            models.Index(fields=['meal_prep_session', 'completed']),
            models.Index(fields=['recipe']),
        ]
    
    def __str__(self):
        return f"{self.task_name} ({self.recipe.title})"