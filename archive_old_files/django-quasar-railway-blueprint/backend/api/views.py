from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema

from .models import Task
from .serializers import TaskSerializer, TaskCreateSerializer, UserSerializer


@extend_schema(
    tags=['Health'],
    summary='API Health Check',
    description='Check if the API is running properly'
)
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """API health check endpoint"""
    return Response({
        'status': 'healthy',
        'message': 'Django + Quasar Blueprint API is running!',
        'version': '1.0.0'
    })


@extend_schema(
    tags=['Users'],
    summary='Get current user info',
    description='Get information about the currently authenticated user'
)
@api_view(['GET'])
def current_user(request):
    """Get current user information"""
    if request.user.is_authenticated:
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tasks
    """
    serializer_class = TaskSerializer
    
    def get_queryset(self):
        """Return tasks for the current user"""
        if self.request.user.is_authenticated:
            return Task.objects.filter(user=self.request.user)
        return Task.objects.none()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ['create', 'update', 'partial_update']:
            return TaskCreateSerializer
        return TaskSerializer
    
    def perform_create(self, serializer):
        """Set the user when creating a task"""
        serializer.save(user=self.request.user)
    
    @extend_schema(
        tags=['Tasks'],
        summary='List tasks',
        description='Get a list of tasks for the current user'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Tasks'],
        summary='Create task',
        description='Create a new task'
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Tasks'],
        summary='Get task',
        description='Get a specific task by ID'
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Tasks'],
        summary='Update task',
        description='Update a task'
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Tasks'],
        summary='Delete task',
        description='Delete a task'
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)