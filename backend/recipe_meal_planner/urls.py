"""
URL configuration for recipe_meal_planner project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.http import JsonResponse
from .setup_views import setup_initial_data
from setup_url import setup_data
from recipes.views_media_test import media_info, test_media_upload
from .media_views import serve_media
import os

def health_check(request):
    """Simple health check endpoint for Railway"""
    return JsonResponse({"status": "healthy", "service": "recipe-meal-planner"})

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Health check for Railway (with and without trailing slash)
    path('api/health/', health_check, name='health-check'),
    path('api/health', health_check, name='health-check-no-slash'),
    
    # Setup endpoints for initial data
    path('api/setup/', setup_initial_data, name='setup-initial-data'),
    path('setup-now/', setup_data, name='setup-now'),
    
    # Media test endpoints (public for testing)
    path('api/media-info/', media_info, name='media-info'),
    path('api/test-media-upload/', test_media_upload, name='test-media-upload'),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Endpoints
    path('api/auth/', include('authentication.urls')),
    path('api/', include('recipes.urls')),
    path('api/', include('meal_planning.urls')),
    path('', include('families.urls')),
]

# Serve media files during development and production
# Note: In production, consider using a CDN or cloud storage for better performance
if settings.DEBUG:
    # Use Django's static file serving in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
elif 'RAILWAY_ENVIRONMENT' in os.environ:
    # Use custom media serving view in production
    urlpatterns += [
        path('media/<path:path>', serve_media, name='serve-media'),
    ]
