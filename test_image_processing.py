#!/usr/bin/env python3
"""
Test script for image processing
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

from django.core.files.uploadedfile import SimpleUploadedFile
from backend.recipes.text_extraction_service import TextExtractionService

def test_with_real_image():
    """Test with a real image file if available"""
    
    # Create a simple test image
    print("Creating test image...")
    img = Image.new('RGB', (400, 300), color='white')
    
    # Add some text
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    draw.text((50, 50), "Test Recipe", fill='black', font=font)
    draw.text((50, 100), "Ingredients:", fill='black', font=font)
    draw.text((50, 130), "• 2 cups flour", fill='black', font=font)
    draw.text((50, 160), "• 1 cup sugar", fill='black', font=font)
    
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
    
    print(f"Created test file: {uploaded_file.name}, size: {uploaded_file.size}")
    
    # Test extraction
    extractor = TextExtractionService()
    result = extractor.extract_text_from_image(uploaded_file)
    
    print("Extraction result:")
    print(f"  Success: {result['success']}")
    if result['success']:
        print(f"  Method: {result['method']}")
        print(f"  Text: {result['text'][:200]}...")
    else:
        print(f"  Error: {result['error']}")
    
    return result['success']

if __name__ == "__main__":
    print("🧪 Testing Image Processing")
    print("=" * 40)
    
    success = test_with_real_image()
    
    if success:
        print("\n✅ Image processing test passed!")
    else:
        print("\n❌ Image processing test failed!")
    
    sys.exit(0 if success else 1)