from django.core.management.base import BaseCommand
from django.conf import settings
from recipes.models import Recipe
import os


class Command(BaseCommand):
    help = 'Fix broken recipe image references by removing references to non-existent files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write('🔍 Checking for broken recipe image references...')
        
        recipes_with_images = Recipe.objects.exclude(image='').exclude(image__isnull=True)
        broken_count = 0
        fixed_count = 0
        
        for recipe in recipes_with_images:
            image_path = recipe.image.path if recipe.image else None
            
            if image_path and not os.path.exists(image_path):
                broken_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'❌ Broken image: {recipe.title[:40]}... -> {recipe.image}'
                    )
                )
                
                if not dry_run:
                    recipe.image = None
                    recipe.save()
                    fixed_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'   ✅ Fixed: Removed broken image reference')
                    )
        
        if broken_count == 0:
            self.stdout.write(self.style.SUCCESS('✅ No broken image references found!'))
        else:
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f'📊 Found {broken_count} broken image references. '
                        f'Run without --dry-run to fix them.'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'📊 Fixed {fixed_count} broken image references!'
                    )
                )