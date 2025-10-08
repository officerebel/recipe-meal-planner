from django.contrib import admin
from .models import MealPlan, DailyMeals, MealAssignment, ShoppingList, ShoppingListItem


class DailyMealsInline(admin.TabularInline):
    model = DailyMeals
    extra = 0
    readonly_fields = ['created_at', 'updated_at']
    fields = ['date', 'created_at', 'updated_at']


class MealAssignmentInline(admin.TabularInline):
    model = MealAssignment
    extra = 1
    fields = ['recipe', 'meal_type', 'servings_planned', 'notes']
    autocomplete_fields = ['recipe']


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'total_days', 'created_at']
    list_filter = ['start_date', 'end_date', 'created_at']
    search_fields = ['name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'total_days']
    inlines = [DailyMealsInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'start_date', 'end_date')
        }),
        ('Metadata', {
            'fields': ('total_days', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_days(self, obj):
        """Calculate total days in the meal plan"""
        return (obj.end_date - obj.start_date).days + 1
    total_days.short_description = 'Total Days'


@admin.register(DailyMeals)
class DailyMealsAdmin(admin.ModelAdmin):
    list_display = ['meal_plan', 'date', 'meal_count', 'created_at']
    list_filter = ['date', 'meal_plan', 'created_at']
    search_fields = ['meal_plan__name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'meal_count']
    inlines = [MealAssignmentInline]
    list_select_related = ['meal_plan']
    
    def meal_count(self, obj):
        """Count of meal assignments for this day"""
        return obj.meal_assignments.count()
    meal_count.short_description = 'Meals Assigned'


@admin.register(MealAssignment)
class MealAssignmentAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'meal_plan_name', 'date', 'meal_type', 'servings_planned', 'created_at']
    list_filter = ['meal_type', 'daily_meals__date', 'created_at']
    search_fields = ['recipe__title', 'daily_meals__meal_plan__name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'effective_servings']
    autocomplete_fields = ['recipe']
    list_select_related = ['recipe', 'daily_meals__meal_plan']
    
    fieldsets = (
        ('Assignment Details', {
            'fields': ('daily_meals', 'recipe', 'meal_type')
        }),
        ('Serving Information', {
            'fields': ('servings_planned', 'effective_servings', 'notes')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def meal_plan_name(self, obj):
        """Get meal plan name"""
        return obj.daily_meals.meal_plan.name
    meal_plan_name.short_description = 'Meal Plan'
    
    def date(self, obj):
        """Get date"""
        return obj.daily_meals.date
    date.short_description = 'Date'


class ShoppingListItemInline(admin.TabularInline):
    model = ShoppingListItem
    extra = 0
    fields = ['ingredient_name', 'total_amount', 'unit', 'category', 'purchased']
    readonly_fields = ['purchased_at']


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'total_items', 'purchased_items', 'generated_at']
    list_filter = ['start_date', 'end_date', 'generated_at']
    search_fields = ['name']
    readonly_fields = ['id', 'generated_at', 'total_items', 'purchased_items']
    filter_horizontal = ['meal_plans']
    inlines = [ShoppingListItemInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'start_date', 'end_date')
        }),
        ('Meal Plans', {
            'fields': ('meal_plans',)
        }),
        ('Statistics', {
            'fields': ('total_items', 'purchased_items', 'generated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_items(self, obj):
        """Total number of items"""
        return obj.items.count()
    total_items.short_description = 'Total Items'
    
    def purchased_items(self, obj):
        """Number of purchased items"""
        return obj.items.filter(purchased=True).count()
    purchased_items.short_description = 'Purchased Items'


@admin.register(ShoppingListItem)
class ShoppingListItemAdmin(admin.ModelAdmin):
    list_display = ['ingredient_name', 'shopping_list', 'category', 'purchased', 'purchased_at']
    list_filter = ['category', 'purchased', 'purchased_at', 'shopping_list']
    search_fields = ['ingredient_name', 'shopping_list__name']
    readonly_fields = ['id', 'purchased_at']
    filter_horizontal = ['source_recipes']
    list_select_related = ['shopping_list']
    
    fieldsets = (
        ('Item Details', {
            'fields': ('shopping_list', 'ingredient_name', 'total_amount', 'unit', 'category')
        }),
        ('Purchase Status', {
            'fields': ('purchased', 'purchased_at', 'notes')
        }),
        ('Source Information', {
            'fields': ('source_recipes',),
            'classes': ('collapse',)
        }),
    )