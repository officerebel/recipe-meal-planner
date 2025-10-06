#!/usr/bin/env python3
"""
Test script to verify PDF parsing functionality
"""
import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recipe_meal_planner.settings')
django.setup()

def test_pdf_dependencies():
    """Test if PDF parsing dependencies are available"""
    print("🔍 Testing PDF parsing dependencies...")
    
    try:
        import PyPDF2
        print(f"✅ PyPDF2 version: {PyPDF2.__version__}")
    except ImportError as e:
        print(f"❌ PyPDF2 not available: {e}")
        return False
    
    try:
        from recipes.services import PDFTextExtractor, RecipeParser, RecipeImportService
        print("✅ Recipe parsing services imported successfully")
    except ImportError as e:
        print(f"❌ Recipe services not available: {e}")
        return False
    
    return True

def test_pdf_parsing_logic():
    """Test PDF parsing logic with sample text"""
    print("\n🧪 Testing PDF parsing logic...")
    
    try:
        from recipes.services import RecipeParser
        
        # Sample recipe text (Dutch)
        sample_text = """
        Klassieke Spaghetti Carbonara
        
        Voor 4 personen
        Bereidingstijd: 15 minuten
        
        Ingrediënten:
        • 400g spaghetti
        • 150g spek (guanciale of pancetta)
        • 4 eigelen
        • 100g parmezaanse kaas (geraspt)
        • Zwarte peper naar smaak
        • Zout naar smaak
        
        Bereidingswijze:
        1. Kook de spaghetti in ruim gezouten water volgens de verpakking.
        2. Snijd het spek in kleine blokjes en bak uit in een grote pan.
        3. Klop de eigelen met de geraspte kaas en peper in een kom.
        4. Giet de pasta af en bewaar een kopje kookvocht.
        5. Meng de warme pasta direct door het eimengsel.
        6. Serveer direct met extra kaas en peper.
        """
        
        parser = RecipeParser()
        recipe_data = parser.parse_recipe(sample_text)
        
        print(f"✅ Parsed recipe title: {recipe_data['title']}")
        print(f"✅ Found {len(recipe_data['ingredients'])} ingredients")
        print(f"✅ Found {len(recipe_data['instructions'])} instructions")
        print(f"✅ Prep time: {recipe_data['prep_time']} minutes")
        print(f"✅ Servings: {recipe_data['servings']}")
        
        # Print first few ingredients
        if recipe_data['ingredients']:
            print("\n📝 Sample ingredients:")
            for i, ingredient in enumerate(recipe_data['ingredients'][:3]):
                print(f"   {i+1}. {ingredient['amount']} {ingredient['name']}")
        
        # Print first instruction
        if recipe_data['instructions']:
            print(f"\n📋 First instruction: {recipe_data['instructions'][0][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ PDF parsing logic failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_recipe_model():
    """Test if recipe models are working"""
    print("\n📊 Testing recipe models...")
    
    try:
        from recipes.models import Recipe, RecipeSource
        from django.contrib.auth.models import User
        
        # Check if we can create a test user (don't save)
        print("✅ Recipe models imported successfully")
        print(f"✅ Available recipe sources: {[choice[0] for choice in RecipeSource.choices]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Recipe models test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting PDF parsing tests...\n")
    
    tests = [
        test_pdf_dependencies,
        test_pdf_parsing_logic,
        test_recipe_model,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print(f"\n📊 Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("🎉 All tests passed! PDF parsing should work.")
    else:
        print("⚠️  Some tests failed. PDF parsing may have issues.")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)