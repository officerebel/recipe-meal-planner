from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MealPlanViewSet, MealAssignmentViewSet, ShoppingListViewSet, ShoppingListItemViewSet

router = DefaultRouter()
router.register(r'meal-plans', MealPlanViewSet)
router.register(r'meal-assignments', MealAssignmentViewSet)
router.register(r'shopping-lists', ShoppingListViewSet)
router.register(r'shopping-list-items', ShoppingListItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]