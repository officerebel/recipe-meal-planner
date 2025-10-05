from django.contrib import admin
from .models import Recipe, Ingredient, SourceMetadata


class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1
    fields = ['name', 'amount', 'unit', 'notes', 'category', 'order']
    ordering = ['order', 'name']


class SourceMetadataInline(admin.StackedInline):
    model = SourceMetadata
    extra = 0
    readonly_fields = ['import_date', 'file_size', 'page_count']
    fields = [
        'original_filename', 'file_size', 'page_count',
        'import_date', 'import_success', 'import_warnings', 'import_errors'
    ]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'source', 'prep_time', 'cook_time', 'servings', 'created_at']
    list_filter = ['source', 'created_at', 'categories', 'tags']
    search_fields = ['title', 'description', 'ingredients__name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'ingredient_count']
    inlines = [IngredientInline, SourceMetadataInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'title', 'description', 'source')
        }),
        ('Timing & Servings', {
            'fields': ('prep_time', 'cook_time', 'total_time', 'servings')
        }),
        ('Instructions & Organization', {
            'fields': ('instructions', 'categories', 'tags')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'ingredient_count'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('ingredients')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'unit', 'recipe', 'category', 'order']
    list_filter = ['category', 'recipe__source']
    search_fields = ['name', 'recipe__title']
    list_select_related = ['recipe']


@admin.register(SourceMetadata)
class SourceMetadataAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'original_filename', 'file_size', 'import_date', 'import_success']
    list_filter = ['import_success', 'import_date']
    search_fields = ['recipe__title', 'original_filename']
    readonly_fields = ['import_date']
    list_select_related = ['recipe']