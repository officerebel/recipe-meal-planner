from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.core.files.base import ContentFile
from recipes.models import Recipe
import os
import json
from PIL import Image
import io


@csrf_exempt
@require_http_methods(["POST"])
def test_media_upload(request):
    """Test endpoint for media upload functionality"""
    try:
        # Create a simple test image
        img = Image.new('RGB', (200, 150), color='lightgreen')
        
        # Add some text
        try:
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            draw.text((10, 70), "Test Upload", fill='darkgreen')
        except ImportError:
            pass
        
        # Save to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Find a recipe to test with
        recipe = Recipe.objects.first()
        if not recipe:
            return JsonResponse({
                'success': False,
                'error': 'No recipes found to test with'
            })
        
        # Save the test image
        old_image = recipe.image.name if recipe.image else None
        recipe.image.save(
            'test_upload.png',
            ContentFile(img_bytes.read()),
            save=True
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Test image uploaded successfully',
            'recipe_id': str(recipe.id),
            'recipe_title': recipe.title,
            'old_image': old_image,
            'new_image': recipe.image.name,
            'image_url': recipe.image.url,
            'media_root': settings.MEDIA_ROOT,
            'media_url': settings.MEDIA_URL,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'media_root': getattr(settings, 'MEDIA_ROOT', 'Not set'),
            'media_url': getattr(settings, 'MEDIA_URL', 'Not set'),
        })


@csrf_exempt
@require_http_methods(["GET"])
def media_info(request):
    """Get media configuration info"""
    try:
        media_root_exists = os.path.exists(settings.MEDIA_ROOT)
        media_root_writable = False
        
        if media_root_exists:
            try:
                test_file = os.path.join(settings.MEDIA_ROOT, '.write_test')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                media_root_writable = True
            except (OSError, PermissionError):
                pass
        
        # Count recipes with images
        from recipes.models import Recipe
        total_recipes = Recipe.objects.count()
        recipes_with_images = Recipe.objects.exclude(image='').exclude(image__isnull=True).count()
        
        return JsonResponse({
            'media_root': settings.MEDIA_ROOT,
            'media_url': settings.MEDIA_URL,
            'media_root_exists': media_root_exists,
            'media_root_writable': media_root_writable,
            'total_recipes': total_recipes,
            'recipes_with_images': recipes_with_images,
            'using_s3': hasattr(settings, 'AWS_STORAGE_BUCKET_NAME'),
            'railway_environment': 'RAILWAY_ENVIRONMENT' in os.environ,
            'railway_volume_mount_path': os.environ.get('RAILWAY_VOLUME_MOUNT_PATH'),
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        })