from typing import List, Dict, Any
from datetime import date, timedelta
from collections import defaultdict
from django.db import transaction
from django.utils import timezone

from .models import MealPlan, DailyMeals, MealAssignment, ShoppingList, ShoppingListItem
from recipes.models import Recipe, Ingredient, IngredientCategory


class MealPlanningService:
    """Service for meal planning operations"""
    
    def create_meal_plan(self, name: str, start_date: date, end_date: date, user) -> MealPlan:
        """
        Create a new meal plan with daily meal slots
        
        Args:
            name: Name for the meal plan
            start_date: Start date of the meal plan
            end_date: End date of the meal plan
            user: User who owns this meal plan
            
        Returns:
            Created MealPlan instance
        """
        if start_date > end_date:
            raise ValueError("Start date must be before or equal to end date")
        
        with transaction.atomic():
            # Create the meal plan
            meal_plan = MealPlan.objects.create(
                name=name,
                start_date=start_date,
                end_date=end_date,
                user=user
            )
            
            # Create daily meal slots for each day
            current_date = start_date
            while current_date <= end_date:
                DailyMeals.objects.create(
                    meal_plan=meal_plan,
                    date=current_date
                )
                current_date += timedelta(days=1)
            
            return meal_plan
    
    def assign_meal(self, meal_plan_id: str, date: date, recipe_id: str, 
                   meal_type: str, servings_planned: int = None, notes: str = "") -> MealAssignment:
        """
        Assign a recipe to a specific meal slot
        
        Args:
            meal_plan_id: ID of the meal plan
            date: Date for the meal
            recipe_id: ID of the recipe to assign
            meal_type: Type of meal (breakfast, lunch, dinner, etc.)
            servings_planned: Number of servings planned (optional)
            notes: Additional notes (optional)
            
        Returns:
            Created MealAssignment instance
        """
        try:
            meal_plan = MealPlan.objects.get(id=meal_plan_id)
            recipe = Recipe.objects.get(id=recipe_id)
        except (MealPlan.DoesNotExist, Recipe.DoesNotExist) as e:
            raise ValueError(f"Invalid meal plan or recipe ID: {str(e)}")
        
        # Check if date is within meal plan range
        if not (meal_plan.start_date <= date <= meal_plan.end_date):
            raise ValueError("Date is outside the meal plan range")
        
        # Get or create daily meals for the date
        daily_meals, created = DailyMeals.objects.get_or_create(
            meal_plan=meal_plan,
            date=date
        )
        
        # Check if there's already a meal assigned for this slot
        existing_assignment = MealAssignment.objects.filter(
            daily_meals=daily_meals,
            meal_type=meal_type,
            recipe=recipe
        ).first()
        
        if existing_assignment:
            raise ValueError(f"Recipe already assigned to {meal_type} on {date}")
        
        # Create the meal assignment
        assignment = MealAssignment.objects.create(
            daily_meals=daily_meals,
            recipe=recipe,
            meal_type=meal_type,
            servings_planned=servings_planned,
            notes=notes
        )
        
        # Trigger shopping list updates for this meal plan
        try:
            self.trigger_shopping_list_updates(meal_plan_id)
        except Exception as e:
            # Log error but don't fail the meal assignment
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to update shopping lists for meal plan {meal_plan_id}: {str(e)}")
        
        return assignment
    
    def remove_meal_assignment(self, assignment_id: str) -> bool:
        """
        Remove a meal assignment
        
        Args:
            assignment_id: ID of the meal assignment to remove
            
        Returns:
            True if removed, False if not found
        """
        try:
            assignment = MealAssignment.objects.get(id=assignment_id)
            meal_plan_id = str(assignment.daily_meals.meal_plan.id)
            assignment.delete()
            
            # Trigger shopping list updates for this meal plan
            try:
                self.trigger_shopping_list_updates(meal_plan_id)
            except Exception as e:
                # Log error but don't fail the removal
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to update shopping lists for meal plan {meal_plan_id}: {str(e)}")
            
            return True
        except MealAssignment.DoesNotExist:
            return False
    
    def get_meal_plan_summary(self, meal_plan_id: str) -> Dict[str, Any]:
        """
        Get a summary of a meal plan with statistics
        
        Args:
            meal_plan_id: ID of the meal plan
            
        Returns:
            Dictionary with meal plan summary
        """
        try:
            meal_plan = MealPlan.objects.prefetch_related(
                'daily_meals__meal_assignments__recipe'
            ).get(id=meal_plan_id)
        except MealPlan.DoesNotExist:
            raise ValueError("Meal plan not found")
        
        # Calculate statistics
        total_days = (meal_plan.end_date - meal_plan.start_date).days + 1
        total_assignments = sum(
            daily.meal_assignments.count() 
            for daily in meal_plan.daily_meals.all()
        )
        
        # Count meals by type
        meal_type_counts = defaultdict(int)
        unique_recipes = set()
        
        for daily in meal_plan.daily_meals.all():
            for assignment in daily.meal_assignments.all():
                meal_type_counts[assignment.meal_type] += 1
                unique_recipes.add(assignment.recipe.id)
        
        return {
            'meal_plan': meal_plan,
            'total_days': total_days,
            'total_assignments': total_assignments,
            'unique_recipes': len(unique_recipes),
            'meal_type_counts': dict(meal_type_counts),
            'completion_percentage': (total_assignments / (total_days * 3)) * 100 if total_days > 0 else 0
        }
    
    def trigger_shopping_list_updates(self, meal_plan_id: str):
        """
        Trigger updates for all shopping lists that include the specified meal plan
        
        Args:
            meal_plan_id: ID of the meal plan that was changed
            
        Returns:
            List of updated shopping lists
        """
        shopping_service = ShoppingListService()
        return shopping_service.update_shopping_lists_for_meal_plan(meal_plan_id)


class ShoppingListService:
    """Service for shopping list generation and management"""
    
    def generate_shopping_list(self, name: str, start_date: date, end_date: date, 
                             meal_plan_ids: List[str], user) -> ShoppingList:
        """
        Generate a shopping list from meal plans
        
        Args:
            name: Name for the shopping list
            start_date: Start date for the shopping list
            end_date: End date for the shopping list
            meal_plan_ids: List of meal plan IDs to include
            user: User who owns this shopping list
            
        Returns:
            Generated ShoppingList instance
        """
        if start_date > end_date:
            raise ValueError("Start date must be before or equal to end date")
        
        # Get meal plans (only user's own meal plans)
        meal_plans = MealPlan.objects.filter(id__in=meal_plan_ids, user=user)
        if meal_plans.count() != len(meal_plan_ids):
            raise ValueError("One or more meal plans not found or not accessible")
        
        with transaction.atomic():
            # Create shopping list
            shopping_list = ShoppingList.objects.create(
                name=name,
                start_date=start_date,
                end_date=end_date,
                user=user
            )
            shopping_list.meal_plans.set(meal_plans)
            
            # Collect ingredients from all meal assignments in the date range
            ingredient_consolidation = defaultdict(lambda: {
                'total_amount': '',
                'unit': '',
                'category': IngredientCategory.OTHER,
                'recipes': set(),
                'notes': []
            })
            
            for meal_plan in meal_plans:
                # Get daily meals within the date range
                daily_meals = meal_plan.daily_meals.filter(
                    date__gte=start_date,
                    date__lte=end_date
                )
                
                for daily in daily_meals:
                    for assignment in daily.meal_assignments.select_related('recipe').all():
                        recipe = assignment.recipe
                        servings_multiplier = assignment.effective_servings / (recipe.servings or 1)
                        
                        # Add ingredients from this recipe
                        for ingredient in recipe.ingredients.all():
                            # Skip ingredients with obviously malformed names
                            if self._is_malformed_ingredient_name(ingredient.name):
                                continue
                                
                            key = ingredient.name.lower().strip()
                            consolidation = ingredient_consolidation[key]
                            
                            # Track which recipes use this ingredient
                            consolidation['recipes'].add(recipe)
                            
                            # Use the first category we encounter (could be improved)
                            if consolidation['category'] == IngredientCategory.OTHER:
                                consolidation['category'] = ingredient.category
                            
                            # For now, just collect amounts as text (proper consolidation would need unit parsing)
                            if ingredient.amount:
                                amount_text = f"{ingredient.amount} (from {recipe.title})"
                                if servings_multiplier != 1:
                                    amount_text += f" x{servings_multiplier:.1f}"
                                consolidation['notes'].append(amount_text)
                            
                            # Use the most common unit
                            if ingredient.unit and not consolidation['unit']:
                                consolidation['unit'] = ingredient.unit
            
            # Create shopping list items
            for ingredient_name, consolidation in ingredient_consolidation.items():
                # Create a consolidated amount description (max 100 chars)
                if consolidation['notes']:
                    total_amount = '; '.join(consolidation['notes'])
                    if len(total_amount) > 100:
                        total_amount = total_amount[:97] + "..."
                else:
                    total_amount = "As needed"
                
                item = ShoppingListItem.objects.create(
                    shopping_list=shopping_list,
                    ingredient_name=ingredient_name.title(),
                    total_amount=total_amount,
                    unit=consolidation['unit'] or '',
                    category=consolidation['category'] or 'other'
                )
                
                # Link to source recipes
                item.source_recipes.set(consolidation['recipes'])
            
            return shopping_list
    
    def mark_item_purchased(self, item_id: str, purchased: bool = True) -> bool:
        """
        Mark a shopping list item as purchased or unpurchased
        
        Args:
            item_id: ID of the shopping list item
            purchased: Whether the item is purchased
            
        Returns:
            True if updated, False if not found
        """
        try:
            item = ShoppingListItem.objects.get(id=item_id)
            item.purchased = purchased
            if purchased:
                item.purchased_at = timezone.now()
            else:
                item.purchased_at = None
            item.save()
            return True
        except ShoppingListItem.DoesNotExist:
            return False
    
    def get_shopping_list_by_category(self, shopping_list_id: str) -> Dict[str, List[Dict]]:
        """
        Get shopping list items organized by category
        
        Args:
            shopping_list_id: ID of the shopping list
            
        Returns:
            Dictionary with items organized by category
        """
        try:
            shopping_list = ShoppingList.objects.get(id=shopping_list_id)
        except ShoppingList.DoesNotExist:
            raise ValueError("Shopping list not found")
        
        # Group items by category
        categorized_items = defaultdict(list)
        
        for item in shopping_list.items.all().order_by('ingredient_name'):
            categorized_items[item.get_category_display()].append({
                'id': str(item.id),
                'ingredient_name': item.ingredient_name,
                'total_amount': item.total_amount,
                'unit': item.unit,
                'purchased': item.purchased,
                'purchased_at': item.purchased_at,
                'notes': item.notes
            })
        
        return dict(categorized_items)
    
    def _is_malformed_ingredient_name(self, name: str) -> bool:
        """
        Check if an ingredient name appears to be malformed from poor PDF parsing
        
        Args:
            name: The ingredient name to check
            
        Returns:
            True if the name appears to be malformed
        """
        if not name or not name.strip():
            return True
            
        name = name.strip()
        
        # Very short names that are likely parsing errors
        if len(name) <= 2:
            return True
            
        # Names that are only numbers
        if name.isdigit():
            return True
            
        # Names that are only numbers, spaces, and punctuation
        if not any(c.isalpha() for c in name):
            return True
            
        # Names that contain obvious instruction text (common Dutch/English cooking terms)
        instruction_indicators = [
            'bereidingswijze', 'bereiding', 'instructie', 'stap', 'minuten', 'graden',
            'instructions', 'directions', 'step', 'minutes', 'degrees', 'method',
            'snijd', 'voeg toe', 'meng', 'bak', 'kook', 'roer', 'haal', 'doe',
            'cut', 'add', 'mix', 'fry', 'cook', 'stir', 'heat', 'serve',
            'bereid het', 'snijd de', 'voeg de', 'haal de', 'doe de', 'meng de',
            'was en', 'breek ze', 'stoom de', 'pureer met', 'giet een',
            'verwijder de', 'ondersteboven', 'wasbak', 'kloppen', 'sprinkel',
            'bewaar de', 'eventueel', 'tot een', 'zoals gewenst'
        ]
        
        name_lower = name.lower()
        if any(indicator in name_lower for indicator in instruction_indicators):
            return True
            
        # Names that are suspiciously long (likely contain instructions)
        if len(name) > 100:
            return True
            
        # Names that contain multiple sentences (likely instructions)
        if '. ' in name and len(name) > 50:
            return True
            
        # Names that start with instruction-like phrases
        instruction_starters = [
            'bereid het', 'snijd de', 'voeg de', 'haal de', 'doe de', 'meng de',
            'was en', 'verwijder', 'pureer', 'giet', 'bewaar', 'serveer'
        ]
        
        if any(name_lower.startswith(starter) for starter in instruction_starters):
            return True
            
        return False
    
    def update_shopping_lists_for_meal_plan(self, meal_plan_id):
        """
        Update all shopping lists that include the specified meal plan
        
        Args:
            meal_plan_id: ID of the meal plan that was changed
            
        Returns:
            List of updated shopping lists
        """
        from .models import ShoppingList, ShoppingListItem
        
        # Find all shopping lists that include this meal plan
        affected_shopping_lists = ShoppingList.objects.filter(
            meal_plans__id=meal_plan_id
        ).distinct()
        
        updated_lists = []
        
        for shopping_list in affected_shopping_lists:
            try:
                # Get the meal plan IDs for regeneration
                meal_plan_ids = list(shopping_list.meal_plans.values_list('id', flat=True))
                
                # Clear existing items
                shopping_list.items.all().delete()
                
                # Regenerate the shopping list with updated meal plan data
                updated_shopping_list = self.generate_shopping_list(
                    name=shopping_list.name,
                    start_date=shopping_list.start_date,
                    end_date=shopping_list.end_date,
                    meal_plan_ids=[str(mp_id) for mp_id in meal_plan_ids],
                    user=shopping_list.user
                )
                
                # Update the existing shopping list instead of creating a new one
                shopping_list.items.set(updated_shopping_list.items.all())
                shopping_list.save()
                
                updated_lists.append(shopping_list)
                
            except Exception as e:
                # Log error but continue with other shopping lists
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to update shopping list {shopping_list.id}: {str(e)}")
        
        return updated_lists
    
    def remove_duplicates(self, shopping_list_id: str) -> int:
        """
        Remove duplicate items from a shopping list based on ingredient name
        
        Args:
            shopping_list_id: ID of the shopping list to clean up
            
        Returns:
            Number of duplicate items removed
        """
        try:
            shopping_list = ShoppingList.objects.get(id=shopping_list_id)
        except ShoppingList.DoesNotExist:
            raise ValueError("Shopping list not found")
        
        # Get all items for this shopping list
        items = shopping_list.items.all().order_by('ingredient_name', 'id')
        
        # Group items by normalized ingredient name
        ingredient_groups = defaultdict(list)
        for item in items:
            # Normalize ingredient name for comparison (lowercase, stripped)
            normalized_name = item.ingredient_name.lower().strip()
            ingredient_groups[normalized_name].append(item)
        
        duplicates_removed = 0
        
        with transaction.atomic():
            for normalized_name, item_list in ingredient_groups.items():
                if len(item_list) > 1:
                    # Keep the first item (oldest) and merge information from duplicates
                    primary_item = item_list[0]
                    duplicate_items = item_list[1:]
                    
                    # Collect amounts and notes from duplicates
                    all_amounts = [primary_item.total_amount] if primary_item.total_amount else []
                    all_notes = [primary_item.notes] if primary_item.notes else []
                    all_recipes = set(primary_item.source_recipes.all())
                    
                    for duplicate in duplicate_items:
                        if duplicate.total_amount and duplicate.total_amount not in all_amounts:
                            all_amounts.append(duplicate.total_amount)
                        if duplicate.notes and duplicate.notes not in all_notes:
                            all_notes.append(duplicate.notes)
                        all_recipes.update(duplicate.source_recipes.all())
                    
                    # Update primary item with consolidated information
                    if len(all_amounts) > 1:
                        primary_item.total_amount = '; '.join(all_amounts)
                        # Truncate if too long
                        if len(primary_item.total_amount) > 200:
                            primary_item.total_amount = primary_item.total_amount[:197] + "..."
                    
                    if len(all_notes) > 1:
                        primary_item.notes = '; '.join(all_notes)
                        # Truncate if too long
                        if len(primary_item.notes) > 500:
                            primary_item.notes = primary_item.notes[:497] + "..."
                    
                    primary_item.save()
                    
                    # Update source recipes
                    primary_item.source_recipes.set(all_recipes)
                    
                    # Delete duplicate items
                    for duplicate in duplicate_items:
                        duplicate.delete()
                        duplicates_removed += 1
        
        return duplicates_removed