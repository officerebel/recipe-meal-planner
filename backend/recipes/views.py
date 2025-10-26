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
            OpenApiParameter('scope', OpenApiTypes.STR, description='Filter by scope (personal, family)', enum=['personal', 'family']),
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
        """Filter queryset based on scope (personal vs family)"""
        scope = self.request.query_params.get('scope', 'personal')
        
        if scope == 'family':
            # Get shared recipes from family members
            from families.models import FamilyMember
            try:
                # Get user's family
                family_member = FamilyMember.objects.get(user=self.request.user)
                family = family_member.family
                
                # Get all family member user IDs
                family_user_ids = family.members.values_list('user_id', flat=True)
                
                # Filter recipes by family members that are shared with family
                queryset = Recipe.objects.filter(
                    user_id__in=family_user_ids,
                    is_shared_with_family=True
                ).prefetch_related('ingredients', 'source_metadata')
            except FamilyMember.DoesNotExist:
                # User not in any family, show empty queryset
                queryset = Recipe.objects.none()
        else:
            # Personal scope - only user's own recipes
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
    
    def get_object(self):
        """
        Override get_object to use the same family-aware filtering as get_queryset
        This ensures that recipe detail views respect family sharing permissions
        """
        # Get the recipe ID from URL
        recipe_id = self.kwargs.get('pk')
        
        # First try with the current scope (from query params)
        queryset = self.get_queryset()
        
        try:
            # Filter by ID within the allowed queryset
            obj = queryset.get(pk=recipe_id)
            return obj
        except Recipe.DoesNotExist:
            # If not found with current scope, try family scope for family members
            from families.models import FamilyMember
            try:
                family_member = FamilyMember.objects.get(user=self.request.user)
                
                # If user is a family member and can view all recipes, try family scope
                if family_member.can_view_all_recipes:
                    family = family_member.family
                    family_user_ids = family.members.values_list('user_id', flat=True)
                    family_queryset = Recipe.objects.filter(user_id__in=family_user_ids).prefetch_related('ingredients', 'source_metadata')
                    
                    try:
                        obj = family_queryset.get(pk=recipe_id)
                        return obj
                    except Recipe.DoesNotExist:
                        pass
                        
            except FamilyMember.DoesNotExist:
                pass
            
            # If still not found, raise the original error
            from rest_framework.exceptions import NotFound
            raise NotFound("Recipe not found. It may have been deleted or you may not have access to it.")
    
    @action(detail=True, methods=['post'], url_path='share-with-family')
    def share_with_family(self, request, pk=None):
        """Share or unshare recipe with family"""
        recipe = self.get_object()
        
        # Check if user owns this recipe
        if recipe.user != request.user:
            return Response(
                {'error': 'Je kunt alleen je eigen recepten delen'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if user is in a family
        from families.models import FamilyMember
        try:
            family_member = FamilyMember.objects.get(user=request.user)
        except FamilyMember.DoesNotExist:
            return Response(
                {'error': 'Je moet lid zijn van een familie om recepten te delen'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Toggle sharing status
        share = request.data.get('share', not recipe.is_shared_with_family)
        recipe.is_shared_with_family = share
        recipe.save()
        
        action = 'gedeeld met' if share else 'niet meer gedeeld met'
        logger.info(f"Recipe {recipe.id} {action} familie door {request.user.username}")
        
        return Response({
            'message': f'Recept {action} familie',
            'is_shared_with_family': recipe.is_shared_with_family
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        tags=['Recipes'],
        summary='Import recipe from PDF or image',
        description='Import a recipe by uploading a PDF or image file. The system will extract recipe information automatically using OCR for images.',
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'PDF or image file to import (max 10MB). Supported formats: PDF, PNG, JPG, JPEG, TIFF, BMP, WebP'
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
    def import_recipe(self, request):
        """
        Import a recipe from a PDF or image file
        """
        logger.info(f"=== IMPORT_RECIPE ENDPOINT CALLED ===")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request data keys: {list(request.data.keys())}")
        
        serializer = RecipeImportSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Serializer validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_file = serializer.validated_data['file']
        file_extension = uploaded_file.name.lower().split('.')[-1] if '.' in uploaded_file.name else ''
        
        # Check if this is a preview request
        is_preview = request.data.get('preview', '').lower() == 'true'
        
        try:
            logger.info(f"Starting recipe {'preview' if is_preview else 'import'} for file: {uploaded_file.name} (type: {file_extension})")
            logger.info(f"File size: {uploaded_file.size}, content_type: {uploaded_file.content_type}")
            
            # Use the enhanced import service
            from .text_extraction_service import EnhancedRecipeImportService
            import_service = EnhancedRecipeImportService()
            
            # Extract and parse recipe data
            import_result = import_service.import_recipe_from_file(uploaded_file)
            
            if not import_result['success']:
                logger.warning(f"Recipe import failed for {uploaded_file.name}: {import_result['error']}")
                return Response(
                    {
                        'error': 'Import failed',
                        'details': import_result['error'],
                        'stage': import_result.get('stage', 'unknown')
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create recipe from parsed data
            recipe_data = import_result['recipe_data']
            
            # Determine source type
            source = RecipeSource.IMAGE if file_extension in ['png', 'jpg', 'jpeg', 'tiff', 'bmp', 'webp'] else RecipeSource.PDF
            
            # If this is a preview request, return the parsed data without saving
            if is_preview:
                logger.info(f"Returning preview data for {uploaded_file.name}")
                return Response({
                    'title': recipe_data.get('title', 'Imported Recipe'),
                    'description': recipe_data.get('description', ''),
                    'prep_time': recipe_data.get('prep_time'),
                    'cook_time': recipe_data.get('cook_time'),
                    'servings': recipe_data.get('servings'),
                    'instructions': recipe_data.get('instructions', []),
                    'ingredients': [{'name': ing, 'amount': '', 'notes': ''} for ing in recipe_data.get('ingredients', [])],
                    'categories': [],
                    'tags': [],
                    'source_type': source,
                    'extraction_method': import_result.get('extraction_method'),
                    'raw_text_preview': import_result.get('raw_text_preview', '')[:500]
                }, status=status.HTTP_200_OK)
            
            # Create the recipe
            recipe = Recipe.objects.create(
                user=request.user,
                title=recipe_data.get('title', 'Imported Recipe'),
                description=recipe_data.get('description', ''),
                prep_time=recipe_data.get('prep_time'),
                cook_time=recipe_data.get('cook_time'),
                servings=recipe_data.get('servings'),
                instructions=recipe_data.get('instructions', []),
                source=source
            )
            
            # Create ingredients
            for i, ingredient_text in enumerate(recipe_data.get('ingredients', [])):
                Ingredient.objects.create(
                    recipe=recipe,
                    name=ingredient_text,
                    order=i + 1
                )
            
            # Create source metadata
            SourceMetadata.objects.create(
                recipe=recipe,
                original_filename=uploaded_file.name,
                file_size=uploaded_file.size,
                import_success=True,
                extraction_method=import_result.get('extraction_method', 'unknown'),
                raw_text_preview=import_result.get('raw_text_preview', '')[:1000]  # Limit to 1000 chars
            )
            
            logger.info(f"Successfully imported recipe {recipe.id} from {uploaded_file.name} using {import_result.get('extraction_method', 'unknown')}")
            
            # Return the created recipe
            recipe_serializer = RecipeSerializer(recipe)
            return Response({
                'recipe': recipe_serializer.data,
                'import_metadata': {
                    'extraction_method': import_result.get('extraction_method'),
                    'source_type': source,
                    'ingredients_found': len(recipe_data.get('ingredients', [])),
                    'instructions_found': len(recipe_data.get('instructions', []))
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error importing recipe from {uploaded_file.name}: {str(e)}")
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