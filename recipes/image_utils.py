"""
Image utilities for recipe images
"""
import os
from PIL import Image
from django.core.exceptions import ValidationError
from django.conf import settings


def validate_image_file(image):
    """Validate uploaded image file"""
    # Check file size (5MB max)
    max_size = getattr(settings, 'MAX_IMAGE_SIZE', 5 * 1024 * 1024)
    if image.size > max_size:
        raise ValidationError(f'Image file too large. Maximum size is {max_size // (1024*1024)}MB.')
    
    # Check file extension
    allowed_extensions = getattr(settings, 'ALLOWED_IMAGE_EXTENSIONS', ['.jpg', '.jpeg', '.png', '.gif', '.webp'])
    ext = os.path.splitext(image.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(f'Invalid file type. Allowed types: {", ".join(allowed_extensions)}')
    
    return image


def process_recipe_image(image, max_width=800, max_height=600, quality=85):
    """
    Process and optimize recipe image
    - Resize if too large
    - Optimize quality
    - Convert to WebP for better compression
    """
    try:
        # Open image with PIL
        img = Image.open(image)
        
        # Convert RGBA to RGB if necessary (for JPEG compatibility)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Resize if image is too large
        if img.width > max_width or img.height > max_height:
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        return img
        
    except Exception as e:
        raise ValidationError(f'Error processing image: {str(e)}')


def get_image_url(recipe):
    """Get full URL for recipe image"""
    if recipe.image:
        if hasattr(recipe.image, 'url'):
            return recipe.image.url
        else:
            return f"{settings.MEDIA_URL}{recipe.image}"
    return None


def delete_recipe_image(recipe):
    """Safely delete recipe image file"""
    if recipe.image:
        try:
            if os.path.isfile(recipe.image.path):
                os.remove(recipe.image.path)
        except (ValueError, OSError):
            # File doesn't exist or path is invalid
            pass