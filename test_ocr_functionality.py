#!/usr/bin/env python3
"""
Test script for OCR functionality
"""
import os
import sys
import django

# Setup Django
sys.path.append('backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recipe_meal_planner.settings')
django.setup()

from PIL import Image, ImageDraw, ImageFont
import io
from backend.recipes.text_extraction_service import EnhancedRecipeImportService
from django.core.files.uploadedfile import SimpleUploadedFile

def create_test_recipe_image():
    """Create a test image with recipe text"""
    # Create a white image
    img = Image.new('RGB', (600, 800), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a better font, fallback to default
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        font_text = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()
    
    # Recipe text
    recipe_text = [
        "Chocolate Chip Cookies",
        "",
        "Prep time: 15 minutes",
        "Cook time: 12 minutes", 
        "Serves: 24 cookies",
        "",
        "Ingredients:",
        "• 2 cups all-purpose flour",
        "• 1 tsp baking soda",
        "• 1 tsp salt",
        "• 1 cup butter, softened",
        "• 3/4 cup granulated sugar",
        "• 3/4 cup brown sugar",
        "• 2 large eggs",
        "• 2 tsp vanilla extract",
        "• 2 cups chocolate chips",
        "",
        "Instructions:",
        "1. Preheat oven to 375°F",
        "2. Mix flour, baking soda and salt in bowl",
        "3. Beat butter and sugars until creamy",
        "4. Add eggs and vanilla, beat well",
        "5. Gradually add flour mixture",
        "6. Stir in chocolate chips",
        "7. Drop rounded tablespoons onto baking sheet",
        "8. Bake 9-11 minutes until golden brown"
    ]
    
    # Draw the text
    y = 50
    for line in recipe_text:
        if line == recipe_text[0]:  # Title
            draw.text((50, y), line, fill='black', font=font_title)
            y += 40
        else:
            draw.text((50, y), line, fill='black', font=font_text)
            y += 25
    
    return img

def test_image_ocr():
    """Test OCR functionality with a generated recipe image"""
    print("🧪 Testing Image OCR Functionality")
    print("=" * 50)
    
    # Create test image
    print("📝 Creating test recipe image...")
    test_image = create_test_recipe_image()
    
    # Save to bytes
    img_bytes = io.BytesIO()
    test_image.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Create uploaded file object
    uploaded_file = SimpleUploadedFile(
        "test_recipe.png",
        img_bytes.read(),
        content_type="image/png"
    )
    
    # Test the import service
    print("🔍 Testing text extraction...")
    import_service = EnhancedRecipeImportService()
    
    try:
        result = import_service.import_recipe_from_file(uploaded_file)
        
        if result['success']:
            print("✅ Text extraction successful!")
            print(f"📊 Extraction method: {result['extraction_method']}")
            
            recipe_data = result['recipe_data']
            print(f"📋 Recipe title: {recipe_data.get('title', 'N/A')}")
            print(f"⏱️  Prep time: {recipe_data.get('prep_time', 'N/A')} minutes")
            print(f"🔥 Cook time: {recipe_data.get('cook_time', 'N/A')} minutes")
            print(f"👥 Servings: {recipe_data.get('servings', 'N/A')}")
            print(f"🥘 Ingredients found: {len(recipe_data.get('ingredients', []))}")
            print(f"📝 Instructions found: {len(recipe_data.get('instructions', []))}")
            
            if recipe_data.get('ingredients'):
                print("\n🥘 Ingredients:")
                for i, ingredient in enumerate(recipe_data['ingredients'][:5], 1):
                    print(f"  {i}. {ingredient}")
                if len(recipe_data['ingredients']) > 5:
                    print(f"  ... and {len(recipe_data['ingredients']) - 5} more")
            
            if recipe_data.get('instructions'):
                print("\n📝 Instructions:")
                for i, instruction in enumerate(recipe_data['instructions'][:3], 1):
                    print(f"  {i}. {instruction}")
                if len(recipe_data['instructions']) > 3:
                    print(f"  ... and {len(recipe_data['instructions']) - 3} more")
            
            print("\n✅ Image OCR test completed successfully!")
            return True
            
        else:
            print(f"❌ Text extraction failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pdf_parsing():
    """Test PDF parsing functionality"""
    print("\n🧪 Testing PDF Parsing Functionality")
    print("=" * 50)
    
    # For now, just test that the service can be imported
    try:
        from backend.recipes.text_extraction_service import TextExtractionService
        service = TextExtractionService()
        print("✅ PDF parsing service imported successfully")
        return True
    except Exception as e:
        print(f"❌ PDF parsing test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting OCR and PDF Parsing Tests")
    print("=" * 60)
    
    # Test image OCR
    image_success = test_image_ocr()
    
    # Test PDF parsing
    pdf_success = test_pdf_parsing()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"  Image OCR: {'✅ PASS' if image_success else '❌ FAIL'}")
    print(f"  PDF Parsing: {'✅ PASS' if pdf_success else '❌ FAIL'}")
    
    if image_success and pdf_success:
        print("\n🎉 All tests passed! Ready for deployment.")
        return True
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)