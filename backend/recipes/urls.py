from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet
from .views_media_test import test_media_upload, media_info

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('test-media-upload/', test_media_upload, name='test-media-upload'),
    path('media-info/', media_info, name='media-info'),
]