from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FamilyViewSet

router = DefaultRouter()
router.register(r'families', FamilyViewSet, basename='family')

urlpatterns = [
    path('api/', include(router.urls)),
]