from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import uuid


class RecipeSource(models.TextChoices):
    """Source of the recipe"""
    PDF = 'pdf', 'PDF Import'
    IMAGE = 'image', 'Image Import'
    MANUAL = 'manual', 'Manual Entry'
    DATABASE = 'database', 'Database Import'


class IngredientCategory(models.TextChoices):
    """Categories for ingredients"""
    PRODUCE = 'produce', 'Groenten & Fruit'
    MEAT = 'meat', 'Vlees & Vis'
    DAIRY = 'dairy', 'Zuivel & Eieren'
    PANTRY = 'pantry', 'Voorraadkast'
    FROZEN = 'frozen', 'Diepvries'
    BAKERY = 'bakery', 'Bakkerij'
    BEVERAGES = 'beverages', 'Dranken'
    CONDIMENTS = 'condiments', 'Kruiden & Sauzen'
    SPICES = 'spices', 'Specerijen & Kruiden'
    OTHER = 'other', 'Overig'


class MealType(models.TextChoices):
    """Types of meals"""
    BREAKFAST = 'breakfast', 'Ontbijt'
    LUNCH = 'lunch', 'Lunch'
    DINNER = 'dinner', 'Diner'
    SNACK = 'snack', 'Tussendoortje'
    DESSERT = 'dessert', 'Nagerecht'


class Recipe(models.Model):
    """Recipe model representing a cooking recipe"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        help_text="Owner of this recipe"
    )
    title = models.CharField(max_length=1000, help_text="Recipe title")
    description = models.TextField(blank=True, help_text="Recipe description")
    
    # Image with enhanced handling
    image = models.ImageField(
        upload_to='recipe_images/%Y/%m/',  # Organize by year/month
        null=True, blank=True,
        help_text="Recipe image (max 5MB, JPG/PNG/WebP)"
    )
    
    # Timing information
    prep_time = models.PositiveIntegerField(
        null=True, blank=True, 
        validators=[MinValueValidator(0)],
        help_text="Preparation time in minutes"
    )
    cook_time = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text="Cooking time in minutes"
    )
    total_time = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text="Total time in minutes"
    )
    
    # Serving information
    servings = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1)],
        help_text="Number of servings"
    )
    
    # Nutritional information (per serving)
    calories = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Calories per serving"
    )
    protein = models.DecimalField(
        max_digits=6, decimal_places=2,
        null=True, blank=True,
        help_text="Protein in grams per serving"
    )
    carbohydrates = models.DecimalField(
        max_digits=6, decimal_places=2,
        null=True, blank=True,
        help_text="Carbohydrates in grams per serving"
    )
    fat = models.DecimalField(
        max_digits=6, decimal_places=2,
        null=True, blank=True,
        help_text="Fat in grams per serving"
    )
    fiber = models.DecimalField(
        max_digits=6, decimal_places=2,
        null=True, blank=True,
        help_text="Fiber in grams per serving"
    )
    sugar = models.DecimalField(
        max_digits=6, decimal_places=2,
        null=True, blank=True,
        help_text="Sugar in grams per serving"
    )
    sodium = models.DecimalField(
        max_digits=8, decimal_places=2,
        null=True, blank=True,
        help_text="Sodium in milligrams per serving"
    )
    
    # Instructions as JSON field (list of strings)
    instructions = models.JSONField(
        default=list,
        help_text="List of cooking instructions"
    )
    
    # Categories and tags as JSON fields (lists of strings)
    categories = models.JSONField(
        default=list,
        help_text="Recipe categories"
    )
    tags = models.JSONField(
        default=list,
        help_text="Recipe tags"
    )
    
    # Source information
    source = models.CharField(
        max_length=20,
        choices=RecipeSource.choices,
        default=RecipeSource.MANUAL,
        help_text="Source of the recipe"
    )
    
    # Sharing settings
    is_shared_with_family = models.BooleanField(
        default=False,
        help_text="Whether this recipe is shared with family members"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'title']),
            models.Index(fields=['user', 'source']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['title']),
            models.Index(fields=['source']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def ingredient_count(self):
        """Return the number of ingredients"""
        return self.ingredients.count()


class Ingredient(models.Model):
    """Ingredient model representing a recipe ingredient"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipe = models.ForeignKey(
        Recipe, 
        on_delete=models.CASCADE, 
        related_name='ingredients'
    )
    
    name = models.CharField(max_length=1000, help_text="Ingredient name")
    amount = models.CharField(
        max_length=500, 
        blank=True,
        help_text="Amount (e.g., '2 cups', '1 tbsp')"
    )
    unit = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Unit of measurement"
    )
    notes = models.CharField(
        max_length=1000, 
        blank=True,
        help_text="Additional notes (e.g., 'chopped', 'optional')"
    )
    
    category = models.CharField(
        max_length=20,
        choices=IngredientCategory.choices,
        default=IngredientCategory.OTHER,
        help_text="Ingredient category for shopping list organization"
    )
    
    # Order within the recipe
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['recipe', 'order']),
            models.Index(fields=['name']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        if self.amount:
            return f"{self.amount} {self.name}"
        return self.name


class SourceMetadata(models.Model):
    """Metadata about the source of a recipe"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipe = models.OneToOneField(
        Recipe,
        on_delete=models.CASCADE,
        related_name='source_metadata'
    )
    
    # PDF-specific metadata
    original_filename = models.CharField(
        max_length=255, 
        blank=True,
        help_text="Original filename of imported file"
    )
    file_size = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="File size in bytes"
    )
    page_count = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Number of pages in PDF"
    )
    
    # Import metadata
    import_date = models.DateTimeField(auto_now_add=True)
    import_success = models.BooleanField(default=True)
    import_warnings = models.JSONField(
        default=list,
        help_text="List of warnings during import"
    )
    import_errors = models.JSONField(
        default=list,
        help_text="List of errors during import"
    )
    
    # Raw extracted text (for debugging/reprocessing)
    raw_text = models.TextField(
        blank=True,
        help_text="Raw text extracted from source"
    )
    
    class Meta:
        verbose_name = "Source Metadata"
        verbose_name_plural = "Source Metadata"
    
    def __str__(self):
        return f"Metadata for {self.recipe.title}"