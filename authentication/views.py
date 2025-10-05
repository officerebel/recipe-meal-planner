from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema
import logging

from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer

logger = logging.getLogger(__name__)


@extend_schema(
    tags=['Authentication'],
    summary='Register a new user',
    description='Create a new user account and return authentication token',
    request=UserRegistrationSerializer,
    responses={
        201: {'description': 'User registered successfully'},
        400: {'description': 'Validation errors'}
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user"""
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            user = serializer.save()
            
            # Create or get token for the user
            token, created = Token.objects.get_or_create(user=user)
            
            # Log the user in
            login(request, user)
            
            logger.info(f"New user registered: {user.email}")
            
            return Response({
                'message': 'User registered successfully',
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error during user registration: {str(e)}")
            return Response({
                'error': 'Registration failed. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Authentication'],
    summary='Login user',
    description='Authenticate user and return authentication token',
    request=UserLoginSerializer,
    responses={
        200: {'description': 'Login successful'},
        400: {'description': 'Invalid credentials'}
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Login user"""
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Create or get token for the user
        token, created = Token.objects.get_or_create(user=user)
        
        # Log the user in
        login(request, user)
        
        logger.info(f"User logged in: {user.email}")
        
        return Response({
            'message': 'Login successful',
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Authentication'],
    summary='Logout user',
    description='Logout current user and invalidate authentication token',
    responses={
        200: {'description': 'Logout successful'},
        401: {'description': 'Authentication required'}
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """Logout user"""
    try:
        # Find and delete the token used for this request
        token_key = request.auth.key if request.auth else None
        if token_key:
            Token.objects.filter(key=token_key).delete()
        
        logger.info(f"User logged out: {request.user.email}")
        
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        return Response({
            'error': f'Logout failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=['Authentication'],
    summary='User profile',
    description='Get or update current authenticated user profile information',
    request=UserSerializer,
    responses={
        200: UserSerializer,
        400: {'description': 'Validation errors'},
        401: {'description': 'Authentication required'}
    }
)
@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get or update current user profile"""
    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method in ['PUT', 'PATCH']:
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            logger.info(f"User profile updated: {request.user.email}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)