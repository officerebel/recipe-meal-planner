# Recipe PDF Parser Tests

Comprehensive test suite for the PDF recipe parsing functionality.

## Test Coverage

### 1. Title Extraction Tests (`RecipeParserTitleTest`)
Tests the extraction of recipe titles from various formats:
- ✅ Simple Dutch titles
- ✅ English titles
- ✅ Titles with inline metadata (e.g., "Pasta Carbonara voor 4 personen")
- ✅ Skipping metadata lines (Page numbers, "Ingrediënten", etc.)
- ✅ Skipping date/time lines
- ✅ Special characters (e.g., "Oma's Appeltaart")
- ✅ Whitespace normalization
- ✅ Fallback to default when no title found

### 2. Time Extraction Tests (`RecipeParserTimeTest`)
Tests extraction of preparation and cooking times:
- ✅ Dutch format: "Bereidingstijd: 25 minuten"
- ✅ English format: "Prep time: 15 minutes"
- ✅ Short format: "Prep: 10 min"
- ✅ Cook time extraction
- ✅ Handling missing time information

### 3. Servings Extraction Tests (`RecipeParserServingsTest`)
Tests extraction of serving sizes:
- ✅ Dutch: "Voor 4 personen"
- ✅ English: "Serves 6"
- ✅ Yield format: "Yield: 8 portions"
- ✅ Handling missing servings

### 4. Ingredients Extraction Tests (`RecipeParserIngredientsTest`)
Tests extraction of ingredient lists:
- ✅ Dutch ingredients with units (gram, el, tl)
- ✅ English ingredients (cups, tsp, tbsp)
- ✅ Bulleted lists (-)
- ✅ Numbered lists (1., 2., 3.)
- ✅ Amount and name separation

### 5. Instructions Extraction Tests (`RecipeParserInstructionsTest`)
Tests extraction of cooking instructions:
- ✅ Dutch: "Bereidingswijze:"
- ✅ English: "Instructions:"
- ✅ Numbered steps
- ✅ Multi-step recipes

### 6. Integration Tests (`RecipeParserIntegrationTest`)
Tests complete recipe parsing:
- ✅ Complete Dutch recipe (title, servings, time, ingredients, instructions)
- ✅ Complete English recipe
- ✅ Total time calculation (prep + cook)

### 7. Validation Tests (`PDFValidationServiceTest`)
Tests PDF file validation:
- ✅ Reject non-PDF files
- ✅ Reject empty files
- ✅ Reject files over 10MB
- ✅ File size reporting
- ✅ Page count detection

### 8. Edge Cases Tests (`RecipeParserEdgeCasesTest`)
Tests error handling and edge cases:
- ✅ Empty text
- ✅ Whitespace-only text
- ✅ Malformed ingredient lists
- ✅ Unicode characters (é, ü, ñ, etc.)

## Running the Tests

### Run all PDF parser tests:
```bash
python manage.py test recipes.test_pdf_parser
```

### Run specific test class:
```bash
python manage.py test recipes.test_pdf_parser.RecipeParserTitleTest
```

### Run specific test method:
```bash
python manage.py test recipes.test_pdf_parser.RecipeParserTitleTest.test_extract_simple_dutch_title
```

### Run with verbose output:
```bash
python manage.py test recipes.test_pdf_parser --verbosity=2
```

### Run with coverage:
```bash
coverage run --source='recipes' manage.py test recipes.test_pdf_parser
coverage report
coverage html  # Generate HTML report
```

## Test Results Interpretation

### Success Output:
```
Ran 35 tests in 0.123s

OK
```

### Failure Output:
```
FAIL: test_extract_simple_dutch_title (recipes.test_pdf_parser.RecipeParserTitleTest)
AssertionError: 'Imported Recipe' != 'Bloemkoolcouscous salade met avocado'
```

## Debugging Failed Tests

### 1. Check the logs:
```python
# In services.py, the parser logs extraction attempts:
logger.info(f"Extracted title: '{title}' from line {i}: '{line}'")
```

### 2. Run test with print statements:
```python
def test_extract_simple_dutch_title(self):
    text = "..."
    title = self.parser._extract_title(text)
    print(f"Extracted: {title}")  # Debug output
    self.assertEqual(title, "Expected Title")
```

### 3. Use Python debugger:
```bash
python -m pdb manage.py test recipes.test_pdf_parser.RecipeParserTitleTest.test_extract_simple_dutch_title
```

## Adding New Tests

### Template for new test:
```python
def test_your_new_test(self):
    """Test description"""
    # Arrange
    text = """Your test recipe text"""
    
    # Act
    result = self.parser._extract_title(text)
    
    # Assert
    self.assertEqual(result, "Expected Result")
```

## Common Issues

### Issue: Title extraction returns "Geïmporteerd Recept"
**Cause**: Parser couldn't find a valid title in the text
**Debug**: Check if title is being skipped by filters
**Fix**: Adjust skip_keywords or title_end_patterns

### Issue: Ingredients not extracted
**Cause**: Section header not recognized
**Debug**: Check if "Ingrediënten:" or "Ingredients:" is in text
**Fix**: Add more header patterns to the parser

### Issue: Time extraction returns None
**Cause**: Time format not recognized
**Debug**: Check the exact format in the PDF
**Fix**: Add new regex pattern to _extract_prep_time()

## Test Data

### Sample Dutch Recipe:
```
Bloemkoolcouscous salade met avocado
Voor 2 personen
Bereidingstijd: 25 minuten

Ingrediënten:
- 200 gram broccoli
- 1 el olijfolie

Bereidingswijze:
1. Snijd de groenten
2. Serveer direct
```

### Sample English Recipe:
```
Chicken Curry
Serves 4
Prep time: 15 minutes

Ingredients:
- 500g chicken breast
- 2 tbsp curry powder

Instructions:
1. Cut chicken
2. Cook with curry
```

## Continuous Integration

### GitHub Actions (example):
```yaml
- name: Run PDF Parser Tests
  run: |
    python manage.py test recipes.test_pdf_parser --verbosity=2
```

### Pre-commit Hook:
```bash
#!/bin/bash
python manage.py test recipes.test_pdf_parser
if [ $? -ne 0 ]; then
    echo "PDF parser tests failed. Commit aborted."
    exit 1
fi
```

## Coverage Goals

- **Target**: 90%+ code coverage for services.py
- **Current**: Run `coverage report` to check
- **Focus areas**: Edge cases, error handling, unicode support

## Related Documentation

- [Main README](../README.md)
- [12-Factor App README](../docs/12_FACTOR_APP.md)
- [API Documentation](../docs/API.md)
