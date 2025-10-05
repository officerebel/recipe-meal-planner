from rest_framework import serializers
from django.db import models
from .models import MealPlan, DailyMeals, MealAssignment, ShoppingList, ShoppingListItem
from recipes.serializers import RecipeListSerializer


class MealAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for MealAssignment model"""
    
    recipe = RecipeListSerializer(read_only=True)
    recipe_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = MealAssignment
        fields = [
            'id', 'recipe', 'recipe_id', 'meal_type', 'servings_planned', 
            'notes', 'created_at', 'updated_at', 'effective_servings'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'effective_servings']


class DailyMealsSerializer(serializers.ModelSerializer):
    """Serializer for DailyMeals model"""
    
    meal_assignments = MealAssignmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = DailyMeals
        fields = [
            'id', 'date', 'meal_assignments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MealPlanSerializer(serializers.ModelSerializer):
    """Serializer for MealPlan model"""
    
    daily_meals = DailyMealsSerializer(many=True, read_only=True)
    total_days = serializers.SerializerMethodField()
    total_meals = serializers.SerializerMethodField()
    
    class Meta:
        model = MealPlan
        fields = [
            'id', 'name', 'start_date', 'end_date', 'daily_meals',
            'total_days', 'total_meals', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_days(self, obj):
        """Calculate total days in the meal plan"""
        return (obj.end_date - obj.start_date).days + 1
    
    def get_total_meals(self, obj):
        """Calculate total number of meals assigned"""
        return sum(daily.meal_assignments.count() for daily in obj.daily_meals.all())


class MealPlanListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for meal plan lists"""
    
    total_days = serializers.SerializerMethodField()
    total_meals = serializers.SerializerMethodField()
    
    class Meta:
        model = MealPlan
        fields = [
            'id', 'name', 'start_date', 'end_date', 'total_days', 
            'total_meals', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_days(self, obj):
        """Calculate total days in the meal plan"""
        return (obj.end_date - obj.start_date).days + 1
    
    def get_total_meals(self, obj):
        """Calculate total number of meals assigned"""
        return obj.daily_meals.aggregate(
            total=models.Count('meal_assignments')
        )['total'] or 0


class MealAssignmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating meal assignments"""
    
    class Meta:
        model = MealAssignment
        fields = [
            'recipe_id', 'meal_type', 'servings_planned', 'notes'
        ]
    
    def validate_recipe_id(self, value):
        """Validate that the recipe exists"""
        from recipes.models import Recipe
        if not Recipe.objects.filter(id=value).exists():
            raise serializers.ValidationError("Recipe does not exist.")
        return value


class ShoppingListItemSerializer(serializers.ModelSerializer):
    """Serializer for ShoppingListItem model"""
    
    source_recipes = RecipeListSerializer(many=True, read_only=True)
    
    class Meta:
        model = ShoppingListItem
        fields = [
            'id', 'ingredient_name', 'total_amount', 'unit', 'category',
            'purchased', 'purchased_at', 'notes', 'source_recipes'
        ]
        read_only_fields = ['id', 'purchased_at']


class ShoppingListSerializer(serializers.ModelSerializer):
    """Serializer for ShoppingList model"""
    
    items = ShoppingListItemSerializer(many=True, read_only=True)
    meal_plans = MealPlanListSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    purchased_items = serializers.SerializerMethodField()
    
    class Meta:
        model = ShoppingList
        fields = [
            'id', 'name', 'start_date', 'end_date', 'generated_at',
            'items', 'meal_plans', 'total_items', 'purchased_items'
        ]
        read_only_fields = ['id', 'generated_at']
    
    def get_total_items(self, obj):
        """Get total number of items in the shopping list"""
        return obj.items.count()
    
    def get_purchased_items(self, obj):
        """Get number of purchased items"""
        return obj.items.filter(purchased=True).count()


class ShoppingListCreateSerializer(serializers.Serializer):
    """Serializer for creating shopping lists from meal plans"""
    
    name = serializers.CharField(max_length=200)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    meal_plan_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
        help_text="List of meal plan IDs to include in the shopping list"
    )
    
    def validate(self, data):
        """Validate the shopping list creation data"""
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Start date must be before end date.")
        
        # Validate that all meal plans exist
        meal_plan_ids = data['meal_plan_ids']
        existing_count = MealPlan.objects.filter(id__in=meal_plan_ids).count()
        if existing_count != len(meal_plan_ids):
            raise serializers.ValidationError("One or more meal plans do not exist.")
        
        return data