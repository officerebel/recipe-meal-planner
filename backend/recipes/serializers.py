from rest_framework import serializers
from django.conf import settings
from .models import Recipe, Ingredient, SourceMetadata
from .image_utils import validate_image_file, get_image_url


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient model"""
    
    class Meta:
        model = Ingredient
        fields = [
            'id', 'name', 'amount', 'unit', 'notes', 
            'category', 'order'
        ]
        read_only_fields = ['id']


class SourceMetadataSerializer(serializers.ModelSerializer):
    """Serializer for SourceMetadata model"""
    
    class Meta:
        model = SourceMetadata
        fields = [
            'id', 'original_filename', 'file_size', 'page_count',
            'import_date', 'import_success', 'import_warnings', 
            'import_errors', 'raw_text'
        ]
        read_only_fields = ['id', 'import_date']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe model with enhanced image handling"""
    
    ingredients = IngredientSerializer(many=True, required=False)
    source_metadata = SourceMetadataSerializer(read_only=True)
    ingredient_count = serializers.ReadOnlyField()
    image_url = serializers.SerializerMethodField()
    
    def get_image_url(self, obj):
        """Get full URL for recipe image"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def validate_image(self, image):
        """Validate uploaded image"""
        if image:
            return validate_image_file(image)
        return image
    
    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'image', 'image_url', 'prep_time', 'cook_time', 
            'total_time', 'servings', 'instructions', 'categories', 
            'tags', 'source', 'created_at', 'updated_at', 
            'ingredients', 'source_metadata', 'ingredient_count',
            'calories', 'protein', 'carbohydrates', 'fat', 'fiber', 'sugar', 'sodium'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create a new recipe with ingredients"""
        ingredients_data = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        
        for ingredient_data in ingredients_data:
            Ingredient.objects.create(recipe=recipe, **ingredient_data)
        
        return recipe
    
    def update(self, instance, validated_data):
        """Update recipe and ingredients"""
        ingredients_data = validated_data.pop('ingredients', None)
        
        # Update recipe fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update ingredients if provided
        if ingredients_data is not None:
            # Delete existing ingredients
            instance.ingredients.all().delete()
            
            # Create new ingredients
            for ingredient_data in ingredients_data:
                Ingredient.objects.create(recipe=instance, **ingredient_data)
        
        return instance


class RecipeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for recipe lists"""
    
    ingredient_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'image', 'prep_time', 'cook_time',
            'total_time', 'servings', 'categories', 'tags', 'source',
            'created_at', 'updated_at', 'ingredient_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RecipeImportSerializer(serializers.Serializer):
    """Serializer for PDF recipe import"""
    
    file = serializers.FileField(
        help_text="PDF file containing the recipe"
    )
    
    def validate_file(self, value):
        """Validate the uploaded file"""
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("Only PDF files are allowed.")
        
        # Check file size (10MB limit)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB.")
        
        return value


class ImportValidationResultSerializer(serializers.Serializer):
    """Serializer for import validation results"""
    
    is_valid = serializers.BooleanField()
    errors = serializers.ListField(child=serializers.CharField())
    warnings = serializers.ListField(child=serializers.CharField())
    file_size_bytes = serializers.IntegerField()
    detected_content_type = serializers.CharField()
    page_count = serializers.IntegerField(required=False)


class RecipeStatisticsSerializer(serializers.Serializer):
    """Serializer for recipe statistics"""
    
    total_recipes = serializers.IntegerField()
    pdf_recipes = serializers.IntegerField()
    manual_recipes = serializers.IntegerField()
    database_recipes = serializers.IntegerField()
    total_categories = serializers.IntegerField()
    total_tags = serializers.IntegerField()
    last_import_date = serializers.DateTimeField(required=False, allow_null=True)
    most_popular_category = serializers.CharField(required=False, allow_null=True)
    most_popular_tag = serializers.CharField(required=False, allow_null=True)