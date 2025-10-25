#!/usr/bin/env python3
"""
Test the import endpoint directly
"""
import os
import sys
import django
from PIL import Image
import io

# Setup Django
sys.path.append('backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recipe_meal_planner.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from backend.recipes.views import RecipeViewSet

def test_import_endpoint():
    """Test the import endpoint directly"""
    
    # Create a test user
    user, created = User.objects.get_or_create(username='testuser', defaults={'email': 'test@example.com'})
    
    # Create a test image
    img = Image.new('RGB', (400, 300), color='white')
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    draw.text((50, 50), "Chocolate Cookies", fill='black', font=font)
    draw.text((50, 100), "Prep: 15 min", fill='black', font=font)
    draw.text((50, 130), "Ingredients:", fill='black', font=font)
    draw.text((50, 160), "• 2 cups flour", fill='black', font=font)
    draw.text((50, 190), "• 1 cup sugar", fill='black', font=font)
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Create uploaded file
    uploaded_file = SimpleUploadedFile(
        "test_recipe.png",
        img_bytes.read(),
        content_type="image/png"
    )
    
    # Create request
    factory = RequestFactory()
    request = factory.post('/api/recipes/import/', {'file': uploaded_file})
    request.user = user
    
    # Create viewset and call import method
    viewset = RecipeViewSet()
    viewset.request = request
    viewset.format_kwarg = None
    
    try:
        response = viewset.import_recipe(request)
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        return response.status_code == 201
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing Import Endpoint")
    print("=" * 40)
    
    success = test_import_endpoint()
    
    if success:
        print("\n✅ Import endpoint test passed!")
    else:
        print("\n❌ Import endpoint test failed!")
    
    sys.exit(0 if success else 1)