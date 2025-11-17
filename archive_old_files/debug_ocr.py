#!/usr/bin/env python3
"""
Debug OCR functionality with the uploaded image
"""
import os
import sys
sys.path.append('backend')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recipe_meal_planner.settings')
import django
django.setup()

from backend.recipes.text_extraction_service import EnhancedRecipeImportService
from PIL import Image
import io

def test_ocr_with_image(image_path):
    """Test OCR with a specific image file"""
    print(f"Testing OCR with image: {image_path}")
    
    # Create a mock uploaded file
    class MockUploadedFile:
        def __init__(self, file_path):
            self.name = os.path.basename(file_path)
            self.size = os.path.getsize(file_path)
            self.content_type = 'image/png'
            self._file = open(file_path, 'rb')
        
        def read(self, size=-1):
            return self._file.read(size)
        
        def seek(self, pos, whence=0):
            return self._file.seek(pos, whence)
        
        def tell(self):
            return self._file.tell()
        
        def close(self):
            self._file.close()
    
    try:
        # Test the import service
        import_service = EnhancedRecipeImportService()
        mock_file = MockUploadedFile(image_path)
        
        print("Starting OCR extraction...")
        result = import_service.import_recipe_from_file(mock_file)
        
        print("\n=== OCR RESULTS ===")
        print(f"Success: {result['success']}")
        
        if result['success']:
            recipe_data = result['recipe_data']
            print(f"Title: {recipe_data.get('title', 'N/A')}")
            print(f"Description: {recipe_data.get('description', 'N/A')}")
            print(f"Prep time: {recipe_data.get('prep_time', 'N/A')}")
            print(f"Cook time: {recipe_data.get('cook_time', 'N/A')}")
            print(f"Servings: {recipe_data.get('servings', 'N/A')}")
            
            print("\nIngredients:")
            for i, ingredient in enumerate(recipe_data.get('ingredients', []), 1):
                print(f"  {i}. {ingredient}")
            
            print("\nInstructions:")
            for i, instruction in enumerate(recipe_data.get('instructions', []), 1):
                print(f"  {i}. {instruction}")
                
            print(f"\nFull raw text:")
            print("=" * 50)
            print(result.get('raw_text_preview', 'N/A'))
            print("=" * 50)
        else:
            print(f"Error: {result['error']}")
            
        mock_file.close()
        
    except Exception as e:
        print(f"Error during OCR test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test with the created test image
    test_image_path = "test_recipe_image.png"
    if os.path.exists(test_image_path):
        test_ocr_with_image(test_image_path)
    else:
        print(f"Test image not found: {test_image_path}")
        print("Please create a test image first with: python create_test_recipe_image.py")