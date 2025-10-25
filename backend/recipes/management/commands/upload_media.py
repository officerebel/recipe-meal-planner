from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from recipes.models import Recipe
import os
import requests
from urllib.parse import urljoin


class Command(BaseCommand):
    help = 'Upload local media files to production or fix missing media files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix-missing',
            action='store_true',
            help='Fix recipes with missing image files by clearing the image field',
        )
        parser.add_argument(
            '--upload-sample',
            action='store_true',
            help='Upload a sample image for testing',
        )

    def handle(self, *args, **options):
        if options['fix_missing']:
            self.fix_missing_images()
        elif options['upload_sample']:
            self.upload_sample_image()
        else:
            self.stdout.write('Use --fix-missing or --upload-sample')

    def fix_missing_images(self):
        """Clear image fields for recipes where the image file doesn't exist"""
        recipes_with_images = Recipe.objects.exclude(image='').exclude(image__isnull=True)
        fixed_count = 0
        
        for recipe in recipes_with_images:
            image_path = os.path.join(settings.MEDIA_ROOT, str(recipe.image))
            if not os.path.exists(image_path):
                self.stdout.write(f'Fixing missing image for recipe: {recipe.title}')
                recipe.image = None
                recipe.save()
                fixed_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Fixed {fixed_count} recipes with missing images')
        )

    def upload_sample_image(self):
        """Upload a sample image for testing"""
        # Create a simple test image
        from PIL import Image
        import io
        
        # Create a simple colored rectangle
        img = Image.new('RGB', (300, 200), color='lightblue')
        
        # Add some text (if PIL supports it)
        try:
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            draw.text((50, 80), "Sample Recipe Image", fill='darkblue')
        except ImportError:
            pass  # Skip text if ImageFont not available
        
        # Save to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Find a recipe without an image
        recipe = Recipe.objects.filter(image__isnull=True).first() or Recipe.objects.filter(image='').first()
        
        if recipe:
            # Save the image to the recipe
            recipe.image.save(
                'sample_recipe_image.png',
                ContentFile(img_bytes.read()),
                save=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'Uploaded sample image to recipe: {recipe.title}')
            )
            self.stdout.write(f'Image URL: {recipe.image.url}')
        else:
            self.stdout.write(self.style.WARNING('No recipes found to add sample image'))