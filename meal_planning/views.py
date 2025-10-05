from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import datetime
import logging

from .models import MealPlan, DailyMeals, MealAssignment, ShoppingList, ShoppingListItem
from .serializers import (
    MealPlanSerializer, MealPlanListSerializer, DailyMealsSerializer,
    MealAssignmentSerializer, MealAssignmentCreateSerializer,
    ShoppingListSerializer, ShoppingListCreateSerializer, ShoppingListItemSerializer
)
from .services import MealPlanningService, ShoppingListService

logger = logging.getLogger(__name__)


class MealPlanViewSet(viewsets.ModelViewSet):
    """
    ViewSet for MealPlan CRUD operations
    """
    queryset = MealPlan.objects.all()  # Base queryset for DRF router
    serializer_class = MealPlanSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'start_date', 'end_date', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter queryset to only show current user's meal plans"""
        return MealPlan.objects.filter(user=self.request.user).prefetch_related('daily_meals__meal_assignments__recipe')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return MealPlanListSerializer
        return MealPlanSerializer
    
    def perform_create(self, serializer):
        """Set the user when creating a meal plan"""
        serializer.save(user=self.request.user)
    
    def create(self, request):
        """Create a new meal plan with daily meal slots"""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            service = MealPlanningService()
            meal_plan = service.create_meal_plan(
                name=serializer.validated_data['name'],
                start_date=serializer.validated_data['start_date'],
                end_date=serializer.validated_data['end_date'],
                user=request.user
            )
            
            logger.info(f"Created meal plan {meal_plan.id}: {meal_plan.name}")
            
            response_serializer = MealPlanSerializer(meal_plan)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            logger.warning(f"Error creating meal plan: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error creating meal plan: {str(e)}")
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='assign-meal')
    def assign_meal(self, request, pk=None):
        """
        Assign a recipe to a specific meal slot
        """
        meal_plan = self.get_object()
        serializer = MealAssignmentCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Get date from request
        date_str = request.data.get('date')
        if not date_str:
            return Response(
                {'error': 'Date is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            meal_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            service = MealPlanningService()
            assignment = service.assign_meal(
                meal_plan_id=str(meal_plan.id),
                date=meal_date,
                recipe_id=str(request.data.get('recipe_id')),
                meal_type=request.data.get('meal_type'),
                servings_planned=request.data.get('servings_planned'),
                notes=request.data.get('notes', '')
            )
            
            logger.info(f"Assigned meal {assignment.id} to meal plan {meal_plan.id}")
            
            response_serializer = MealAssignmentSerializer(assignment)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            logger.warning(f"Error assigning meal: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error assigning meal: {str(e)}")
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], url_path='summary')
    def summary(self, request, pk=None):
        """
        Get meal plan summary with statistics
        """
        meal_plan = self.get_object()
        
        try:
            service = MealPlanningService()
            summary = service.get_meal_plan_summary(str(meal_plan.id))
            
            return Response({
                'meal_plan_id': str(meal_plan.id),
                'name': meal_plan.name,
                'start_date': meal_plan.start_date,
                'end_date': meal_plan.end_date,
                'total_days': summary['total_days'],
                'total_assignments': summary['total_assignments'],
                'unique_recipes': summary['unique_recipes'],
                'meal_type_counts': summary['meal_type_counts'],
                'completion_percentage': round(summary['completion_percentage'], 1)
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.warning(f"Error getting meal plan summary: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error getting meal plan summary: {str(e)}")
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MealAssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for MealAssignment operations
    """
    queryset = MealAssignment.objects.all()  # Base queryset for DRF router
    serializer_class = MealAssignmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['meal_type', 'daily_meals__meal_plan']
    ordering_fields = ['daily_meals__date', 'meal_type', 'created_at']
    ordering = ['daily_meals__date', 'meal_type']
    
    def get_queryset(self):
        """Filter queryset to only show current user's meal assignments"""
        return MealAssignment.objects.filter(daily_meals__meal_plan__user=self.request.user).select_related('recipe', 'daily_meals__meal_plan')
    
    def destroy(self, request, *args, **kwargs):
        """Delete a meal assignment"""
        assignment = self.get_object()
        
        try:
            service = MealPlanningService()
            deleted = service.remove_meal_assignment(str(assignment.id))
            
            if deleted:
                logger.info(f"Removed meal assignment {assignment.id}")
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'error': 'Assignment not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
        except Exception as e:
            logger.error(f"Error removing meal assignment: {str(e)}")
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ShoppingListViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ShoppingList operations
    """
    queryset = ShoppingList.objects.all()  # Base queryset for DRF router
    serializer_class = ShoppingListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'start_date', 'end_date', 'generated_at']
    ordering = ['-generated_at']
    
    def get_queryset(self):
        """Filter queryset to only show current user's shopping lists"""
        return ShoppingList.objects.filter(user=self.request.user).prefetch_related('items', 'meal_plans')
    
    def perform_create(self, serializer):
        """Set the user when creating a shopping list"""
        serializer.save(user=self.request.user)
    
    def create(self, request):
        """Generate a new shopping list from meal plans"""
        serializer = ShoppingListCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            service = ShoppingListService()
            shopping_list = service.generate_shopping_list(
                name=serializer.validated_data['name'],
                start_date=serializer.validated_data['start_date'],
                end_date=serializer.validated_data['end_date'],
                meal_plan_ids=[str(id) for id in serializer.validated_data['meal_plan_ids']],
                user=request.user
            )
            
            logger.info(f"Generated shopping list {shopping_list.id}: {shopping_list.name}")
            
            response_serializer = ShoppingListSerializer(shopping_list)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            logger.warning(f"Error generating shopping list: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'], url_path='generate')
    def generate(self, request):
        """Generate a new shopping list from meal plans (alternative endpoint)"""
        return self.create(request)
        except Exception as e:
            logger.error(f"Unexpected error generating shopping list: {str(e)}")
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], url_path='by-category')
    def by_category(self, request, pk=None):
        """
        Get shopping list items organized by category
        """
        shopping_list = self.get_object()
        
        try:
            service = ShoppingListService()
            categorized_items = service.get_shopping_list_by_category(str(shopping_list.id))
            
            return Response(categorized_items, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.warning(f"Error getting categorized shopping list: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error getting categorized shopping list: {str(e)}")
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ShoppingListItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ShoppingListItem operations
    """
    queryset = ShoppingListItem.objects.all()  # Base queryset for DRF router
    serializer_class = ShoppingListItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'purchased', 'shopping_list']
    search_fields = ['ingredient_name']
    ordering_fields = ['ingredient_name', 'category', 'purchased_at']
    ordering = ['category', 'ingredient_name']
    
    def get_queryset(self):
        """Filter queryset to only show current user's shopping list items"""
        return ShoppingListItem.objects.filter(shopping_list__user=self.request.user).select_related('shopping_list')
    
    @action(detail=True, methods=['patch'], url_path='toggle-purchased')
    def toggle_purchased(self, request, pk=None):
        """
        Toggle the purchased status of a shopping list item
        """
        item = self.get_object()
        purchased = request.data.get('purchased', not item.purchased)
        
        try:
            service = ShoppingListService()
            updated = service.mark_item_purchased(str(item.id), purchased)
            
            if updated:
                # Refresh from database
                item.refresh_from_db()
                serializer = self.get_serializer(item)
                
                logger.info(f"Marked shopping list item {item.id} as {'purchased' if purchased else 'unpurchased'}")
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Item not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
        except Exception as e:
            logger.error(f"Error toggling item purchased status: {str(e)}")
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )