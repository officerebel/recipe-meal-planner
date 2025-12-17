"""
Test suite for PDF Recipe Parser

Tests the PDF parsing functionality including:
- Title extraction from Dutch and English recipes
- Ingredient parsing
- Time extraction (prep, cook, total)
- Servings extraction
- Instructions parsing
"""

from django.test import TestCase
from recipes.services import RecipeParser, PDFTextExtractor, PDFValidationService
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile


class RecipeParserTitleTest(TestCase):
    """Test title extraction from recipe text"""
    
    def setUp(self):
        self.parser = RecipeParser()
    
    def test_extract_simple_dutch_title(self):
        """Test extracting a simple Dutch recipe title"""
        text = """Bloemkoolcouscous salade met avocado
Voor 2 personen
Bereidingstijd: 25 minuten
Ingrediënten:
- 200 gram broccoli"""
        
        title = self.parser._extract_title(text)
        self.assertEqual(title, "Bloemkoolcouscous salade met avocado")
    
    def test_extract_title_with_inline_metadata(self):
        """Test extracting title when metadata is on same line"""
        text = """Pasta Carbonara voor 4 personen
Bereidingstijd: 30 minuten"""
        
        title = self.parser._extract_title(text)
        self.assertEqual(title, "Pasta Carbonara")
    
    def test_extract_english_title(self):
        """Test extracting English recipe title"""
        text = """Chicken Tikka Masala
Serves 4
Prep time: 20 minutes
Ingredients:
- 500g chicken"""
        
        title = self.parser._extract_title(text)
        self.assertEqual(title, "Chicken Tikka Masala")
    
    def test_skip_metadata_lines(self):
        """Test that metadata lines are skipped"""
        text = """Page 1
Ingrediënten
Bereidingstijd
Lasagne Bolognese
Voor 6 personen"""
        
        title = self.parser._extract_title(text)
        self.assertEqual(title, "Lasagne Bolognese")
    
    def test_skip_numbers_and_dates(self):
        """Test that lines with only numbers/dates are skipped"""
        text = """2024-11-17
15:30
Tomatensoep
Bereidingstijd: 20 minuten"""
        
        title = self.parser._extract_title(text)
        self.assertEqual(title, "Tomatensoep")
    
    def test_fallback_to_default(self):
        """Test fallback when no valid title found"""
        text = """123
456
:
"""
        
        title = self.parser._extract_title(text)
        self.assertEqual(title, "Geïmporteerd Recept")
    
    def test_title_with_special_characters(self):
        """Test title with special characters"""
        text = """Oma's Appeltaart
Voor 8 personen"""
        
        title = self.parser._extract_title(text)
        self.assertEqual(title, "Oma's Appeltaart")
    
    def test_title_normalization(self):
        """Test that whitespace is normalized"""
        text = """Kip    Kerrie    Salade
Voor 2 personen"""
        
        title = self.parser._extract_title(text)
        self.assertEqual(title, "Kip Kerrie Salade")


class RecipeParserTimeTest(TestCase):
    """Test time extraction from recipe text"""
    
    def setUp(self):
        self.parser = RecipeParser()
    
    def test_extract_prep_time_dutch(self):
        """Test extracting Dutch preparation time"""
        text = "Bereidingstijd: 25 minuten"
        prep_time = self.parser._extract_prep_time(text)
        self.assertEqual(prep_time, 25)
    
    def test_extract_prep_time_english(self):
        """Test extracting English preparation time"""
        text = "Prep time: 15 minutes"
        prep_time = self.parser._extract_prep_time(text)
        self.assertEqual(prep_time, 15)
    
    def test_extract_prep_time_short_format(self):
        """Test extracting prep time in short format"""
        text = "Prep: 10 min"
        prep_time = self.parser._extract_prep_time(text)
        self.assertEqual(prep_time, 10)
    
    def test_extract_cook_time(self):
        """Test extracting cooking time"""
        text = "Cook time: 45 minutes"
        cook_time = self.parser._extract_cook_time(text)
        self.assertEqual(cook_time, 45)
    
    def test_no_time_found(self):
        """Test when no time is found"""
        text = "Just some random text"
        prep_time = self.parser._extract_prep_time(text)
        self.assertIsNone(prep_time)


class RecipeParserServingsTest(TestCase):
    """Test servings extraction from recipe text"""
    
    def setUp(self):
        self.parser = RecipeParser()
    
    def test_extract_servings_dutch(self):
        """Test extracting Dutch servings"""
        text = "Voor 4 personen"
        servings = self.parser._extract_servings(text)
        self.assertEqual(servings, 4)
    
    def test_extract_servings_english(self):
        """Test extracting English servings"""
        text = "Serves 6"
        servings = self.parser._extract_servings(text)
        self.assertEqual(servings, 6)
    
    def test_extract_servings_yield(self):
        """Test extracting servings from yield"""
        text = "Yield: 8 portions"
        servings = self.parser._extract_servings(text)
        self.assertEqual(servings, 8)
    
    def test_no_servings_found(self):
        """Test when no servings found"""
        text = "Just some text"
        servings = self.parser._extract_servings(text)
        self.assertIsNone(servings)


class RecipeParserIngredientsTest(TestCase):
    """Test ingredient extraction from recipe text"""
    
    def setUp(self):
        self.parser = RecipeParser()
    
    def test_extract_dutch_ingredients(self):
        """Test extracting Dutch ingredients"""
        text = """Ingrediënten:
- 200 gram broccoli
- 1 el olijfolie
- 2 tl zout
- 400 ml water"""
        
        ingredients = self.parser._extract_ingredients(text)
        self.assertEqual(len(ingredients), 4)
        self.assertEqual(ingredients[0]['name'], 'broccoli')
        self.assertEqual(ingredients[0]['amount'], '200 gram')
    
    def test_extract_english_ingredients(self):
        """Test extracting English ingredients"""
        text = """Ingredients:
- 2 cups flour
- 1 tsp salt
- 3 eggs"""
        
        ingredients = self.parser._extract_ingredients(text)
        self.assertEqual(len(ingredients), 3)
        self.assertIn('flour', ingredients[0]['name'])
    
    def test_extract_ingredients_with_numbers(self):
        """Test extracting ingredients with numbered list"""
        text = """Ingrediënten:
1. 500 gram gehakt
2. 1 ui
3. 2 tenen knoflook"""
        
        ingredients = self.parser._extract_ingredients(text)
        self.assertGreaterEqual(len(ingredients), 3)


class RecipeParserInstructionsTest(TestCase):
    """Test instructions extraction from recipe text"""
    
    def setUp(self):
        self.parser = RecipeParser()
    
    def test_extract_dutch_instructions(self):
        """Test extracting Dutch instructions"""
        text = """Bereidingswijze:
1. Verwarm de oven voor op 180°C
2. Meng alle ingrediënten
3. Bak 30 minuten"""
        
        instructions = self.parser._extract_instructions(text)
        self.assertEqual(len(instructions), 3)
        self.assertIn('oven', instructions[0].lower())
    
    def test_extract_english_instructions(self):
        """Test extracting English instructions"""
        text = """Instructions:
1. Preheat oven to 350°F
2. Mix ingredients
3. Bake for 25 minutes"""
        
        instructions = self.parser._extract_instructions(text)
        self.assertEqual(len(instructions), 3)


class RecipeParserIntegrationTest(TestCase):
    """Integration tests for complete recipe parsing"""
    
    def setUp(self):
        self.parser = RecipeParser()
    
    def test_parse_complete_dutch_recipe(self):
        """Test parsing a complete Dutch recipe"""
        text = """Bloemkoolcouscous salade met avocado
Voor 2 personen
Bereidingstijd: 25 minuten

Ingrediënten:
- 200 gram broccoli
- 1 avocado
- 2 el olijfolie

Bereidingswijze:
1. Snijd de groenten
2. Meng alles
3. Serveer direct"""
        
        recipe_data = self.parser.parse_recipe(text)
        
        self.assertEqual(recipe_data['title'], 'Bloemkoolcouscous salade met avocado')
        self.assertEqual(recipe_data['servings'], 2)
        self.assertEqual(recipe_data['prep_time'], 25)
        self.assertGreaterEqual(len(recipe_data['ingredients']), 2)
        self.assertGreaterEqual(len(recipe_data['instructions']), 2)
    
    def test_parse_complete_english_recipe(self):
        """Test parsing a complete English recipe"""
        text = """Chicken Curry
Serves 4
Prep time: 15 minutes
Cook time: 30 minutes

Ingredients:
- 500g chicken breast
- 2 tbsp curry powder
- 1 can coconut milk

Instructions:
1. Cut chicken into pieces
2. Cook with curry powder
3. Add coconut milk and simmer"""
        
        recipe_data = self.parser.parse_recipe(text)
        
        self.assertEqual(recipe_data['title'], 'Chicken Curry')
        self.assertEqual(recipe_data['servings'], 4)
        self.assertEqual(recipe_data['prep_time'], 15)
        self.assertEqual(recipe_data['cook_time'], 30)
        self.assertEqual(recipe_data['total_time'], 45)


class PDFValidationServiceTest(TestCase):
    """Test PDF validation service"""
    
    def setUp(self):
        self.validator = PDFValidationService()
    
    def test_validate_non_pdf_file(self):
        """Test validation rejects non-PDF files"""
        file = SimpleUploadedFile("test.txt", b"content", content_type="text/plain")
        result = self.validator.validate_file(file)
        
        self.assertFalse(result['is_valid'])
        self.assertIn('PDF', result['errors'][0])
    
    def test_validate_empty_file(self):
        """Test validation rejects empty files"""
        file = SimpleUploadedFile("test.pdf", b"", content_type="application/pdf")
        result = self.validator.validate_file(file)
        
        self.assertFalse(result['is_valid'])
        self.assertIn('empty', result['errors'][0].lower())
    
    def test_validate_large_file(self):
        """Test validation rejects files over 10MB"""
        # Create a file larger than 10MB
        large_content = b"x" * (11 * 1024 * 1024)
        file = SimpleUploadedFile("test.pdf", large_content, content_type="application/pdf")
        result = self.validator.validate_file(file)
        
        self.assertFalse(result['is_valid'])
        self.assertIn('10MB', result['errors'][0])


class RecipeParserEdgeCasesTest(TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        self.parser = RecipeParser()
    
    def test_empty_text(self):
        """Test parsing empty text"""
        recipe_data = self.parser.parse_recipe("")
        self.assertEqual(recipe_data['title'], "Geïmporteerd Recept")
        self.assertEqual(len(recipe_data['ingredients']), 0)
    
    def test_text_with_only_whitespace(self):
        """Test parsing text with only whitespace"""
        recipe_data = self.parser.parse_recipe("   \n\n   \t\t   ")
        self.assertEqual(recipe_data['title'], "Geïmporteerd Recept")
    
    def test_malformed_ingredients(self):
        """Test handling malformed ingredient lists"""
        text = """Title
Ingredients:
random text without structure
more random text"""
        
        recipe_data = self.parser.parse_recipe(text)
        # Should not crash, may return empty list
        self.assertIsInstance(recipe_data['ingredients'], list)
    
    def test_unicode_characters(self):
        """Test handling unicode characters"""
        text = """Crème Brûlée
Ingrédients:
- 500 ml crème fraîche
- 100 g sucre"""
        
        recipe_data = self.parser.parse_recipe(text)
        self.assertIn('Crème', recipe_data['title'])
