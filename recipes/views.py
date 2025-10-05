from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import logging

from .models import Recipe, RecipeSource
from .serializers import (
    RecipeSerializer, RecipeListSerializer, RecipeImportSerializer,
    ImportValidationResultSerializer, RecipeStatisticsSerializer
)
from .services import RecipeImportService, PDFValidationService

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(
        tags=['Recipes'],
        summary='List recipes',
        description='Get a paginated list of user\'s recipes with filtering and search capabilities',
        parameters=[
            OpenApiParameter('search', OpenApiTypes.STR, description='Search in title, description, and ingredients'),
            OpenApiParameter('category', OpenApiTypes.STR, description='Filter by category'),
            OpenApiParameter('tag', OpenApiTypes.STR, description='Filter by tag'),
            OpenApiParameter('source', OpenApiTypes.STR, description='Filter by source (pdf, manual, database)'),
        ]
    ),
    create=extend_schema(
        tags=['Recipes'],
        summary='Create recipe',
        description='Create a new recipe'
    ),
    retrieve=extend_schema(
        tags=['Recipes'],
        summary='Get recipe',
        description='Get detailed information about a specific recipe'
    ),
    update=extend_schema(
        tags=['Recipes'],
        summary='Update recipe',
        description='Update an existing recipe'
    ),
    partial_update=extend_schema(
        tags=['Recipes'],
        summary='Partially update recipe',
        description='Partially update an existing recipe'
    ),
    destroy=extend_schema(
        tags=['Recipes'],
        summary='Delete recipe',
        description='Delete a recipe'
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Recipe CRUD operations and PDF import
    """
    queryset = Recipe.objects.all()  # Base queryset for DRF router
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['source']
    search_fields = ['title', 'description', 'ingredients__name']
    ordering_fields = ['title', 'created_at', 'updated_at', 'prep_time', 'cook_time']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return RecipeListSerializer
        elif self.action in ['import_pdf', 'preview_pdf']:
            return RecipeImportSerializer
        return RecipeSerializer
    
    def perform_create(self, serializer):
        """Set the user when creating a recipe"""
        serializer.save(user=self.request.user)
    
    def get_queryset(self):
        """Filter queryset to only show current user's recipes"""
        queryset = Recipe.objects.filter(user=self.request.user).prefetch_related('ingredients', 'source_metadata')
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(categories__contains=[category])
        
        # Filter by tag
        tag = self.request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(tags__contains=[tag])
        
        # Filter by source
        source = self.request.query_params.get('source')
        if source:
            queryset = queryset.filter(source=source)
        
        return queryset
    
    @extend_schema(
        tags=['Recipes'],
        summary='Import recipe from PDF',
        description='Import a recipe by uploading a PDF file. The system will extract recipe information automatically.',
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'PDF file to import (max 10MB)'
                    }
                }
            }
        },
        responses={
            201: RecipeSerializer,
            400: {'description': 'Invalid file or extraction failed'}
        }
    )
    @action(
        detail=False, 
        methods=['post'], 
        parser_classes=[MultiPartParser, FormParser],
        url_path='import'
    )
    def import_pdf(self, request):
        """
        Import a recipe from a PDF file
        """
        serializer = RecipeImportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        pdf_file = serializer.validated_data['file']
        
        try:
            logger.info(f"Starting PDF import for file: {pdf_file.name}")
            
            # Validate the PDF file first
            validation_service = PDFValidationService()
            validation_result = validation_service.validate_file(pdf_file)
            
            if not validation_result['is_valid']:
                logger.warning(f"PDF validation failed for {pdf_file.name}: {validation_result['errors']}")
                return Response(
                    {
                        'error': 'File validation failed',
                        'details': validation_result['errors']
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Log warnings if any
            if validation_result['warnings']:
                logger.warning(f"PDF validation warnings for {pdf_file.name}: {validation_result['warnings']}")
            
            # Import the recipe
            import_service = RecipeImportService()
            recipe = import_service.import_from_pdf(pdf_file, request.user)
            
            logger.info(f"Successfully imported recipe {recipe.id} from {pdf_file.name}")
            
            # Return the created recipe
            recipe_serializer = RecipeSerializer(recipe)
            return Response(recipe_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error importing PDF {pdf_file.name}: {str(e)}")
            return Response(
                {
                    'error': 'Import failed',
                    'details': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        tags=['Recipes'],
        summary='Preview recipe from PDF',
        description='Preview recipe extraction from PDF without saving to database',
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'PDF file to preview (max 10MB)'
                    }
                }
            }
        },
        responses={
            200: {'description': 'Recipe preview data'},
            400: {'description': 'Invalid file or extraction failed'}
        }
    )
    @action(
        detail=False, 
        methods=['post'], 
        parser_classes=[MultiPartParser, FormParser],
        url_path='preview'
    )
    def preview_pdf(self, request):
        """
        Preview a recipe from a PDF file without saving it
        """
        serializer = RecipeImportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        pdf_file = serializer.validated_data['file']
        
        try:
            logger.info(f"Starting PDF preview for file: {pdf_file.name}")
            
            # Validate the PDF file first
            validation_service = PDFValidationService()
            validation_result = validation_service.validate_file(pdf_file)
            
            if not validation_result['is_valid']:
                logger.warning(f"PDF validation failed for preview {pdf_file.name}: {validation_result['errors']}")
                return Response(
                    {
                        'error': 'File validation failed',
                        'details': validation_result['errors']
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Preview the recipe (don't save to database)
            import_service = RecipeImportService()
            recipe_data = import_service.preview_from_pdf(pdf_file)
            
            logger.info(f"Successfully previewed recipe from {pdf_file.name}")
            
            return Response(recipe_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error previewing PDF {pdf_file.name}: {str(e)}")
            return Response(
                {
                    'error': 'Preview failed',
                    'details': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(
        detail=False, 
        methods=['post'], 
        parser_classes=[MultiPartParser, FormParser],
        url_path='validate'
    )
    def validate_pdf(self, request):
        """
        Validate a PDF file for recipe import
        """
        serializer = RecipeImportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        pdf_file = serializer.validated_data['file']
        
        try:
            logger.info(f"Validating PDF file: {pdf_file.name}")
            
            validation_service = PDFValidationService()
            validation_result = validation_service.validate_file(pdf_file)
            
            logger.info(f"PDF validation completed for {pdf_file.name}: "
                       f"Valid={validation_result['is_valid']}, "
                       f"Errors={len(validation_result['errors'])}, "
                       f"Warnings={len(validation_result['warnings'])}")
            
            serializer = ImportValidationResultSerializer(validation_result)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error validating PDF {pdf_file.name}: {str(e)}")
            return Response(
                {
                    'error': 'Validation failed',
                    'details': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """
        Get recipe collection statistics
        """
        try:
            logger.info("Retrieving recipe statistics")
            
            # Calculate statistics for current user only
            user_recipes = Recipe.objects.filter(user=request.user)
            total_recipes = user_recipes.count()
            pdf_recipes = user_recipes.filter(source=RecipeSource.PDF).count()
            manual_recipes = user_recipes.filter(source=RecipeSource.MANUAL).count()
            database_recipes = user_recipes.filter(source=RecipeSource.DATABASE).count()
            
            # Get unique categories and tags for current user
            all_categories = []
            all_tags = []
            for recipe in user_recipes:
                all_categories.extend(recipe.categories)
                all_tags.extend(recipe.tags)
            
            unique_categories = list(set(all_categories))
            unique_tags = list(set(all_tags))
            
            # Get most popular category and tag
            category_counts = {}
            tag_counts = {}
            
            for category in all_categories:
                category_counts[category] = category_counts.get(category, 0) + 1
            
            for tag in all_tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            most_popular_category = max(category_counts.keys(), key=category_counts.get) if category_counts else None
            most_popular_tag = max(tag_counts.keys(), key=tag_counts.get) if tag_counts else None
            
            # Get last import date for current user
            last_import = user_recipes.filter(source=RecipeSource.PDF).order_by('-created_at').first()
            last_import_date = last_import.created_at if last_import else None
            
            statistics = {
                'total_recipes': total_recipes,
                'pdf_recipes': pdf_recipes,
                'manual_recipes': manual_recipes,
                'database_recipes': database_recipes,
                'total_categories': len(unique_categories),
                'total_tags': len(unique_tags),
                'last_import_date': last_import_date,
                'most_popular_category': most_popular_category,
                'most_popular_tag': most_popular_tag,
            }
            
            logger.info(f"Retrieved recipe statistics: {total_recipes} total recipes")
            
            serializer = RecipeStatisticsSerializer(statistics)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving recipe statistics: {str(e)}")
            return Response(
                {
                    'error': 'Failed to retrieve statistics',
                    'details': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='categories')
    def categories(self, request):
        """
        Get all unique categories
        """
        try:
            all_categories = []
            for recipe in Recipe.objects.filter(user=request.user):
                all_categories.extend(recipe.categories)
            
            unique_categories = sorted(list(set(all_categories)))
            logger.debug(f"Retrieved {len(unique_categories)} categories")
            
            return Response(unique_categories, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving categories: {str(e)}")
            return Response(
                {
                    'error': 'Failed to retrieve categories',
                    'details': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='tags')
    def tags(self, request):
        """
        Get all unique tags
        """
        try:
            all_tags = []
            for recipe in Recipe.objects.filter(user=request.user):
                all_tags.extend(recipe.tags)
            
            unique_tags = sorted(list(set(all_tags)))
            logger.debug(f"Retrieved {len(unique_tags)} tags")
            
            return Response(unique_tags, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving tags: {str(e)}")
            return Response(
                {
                    'error': 'Failed to retrieve tags',
                    'details': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='ingredient-categories')
    def ingredient_categories(self, request):
        """
        Get all available ingredient categories with Dutch names
        """
        try:
            from .models import IngredientCategory
            
            categories = [
                {
                    'value': choice[0],
                    'label': choice[1]
                }
                for choice in IngredientCategory.choices
            ]
            
            logger.debug(f"Retrieved {len(categories)} ingredient categories")
            return Response(categories, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving ingredient categories: {str(e)}")
            return Response(
                {
                    'error': 'Failed to retrieve ingredient categories',
                    'details': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )