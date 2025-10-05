import PyPDF2
import re
import logging
from typing import Dict, List, Any, Optional
from django.core.files.uploadedfile import UploadedFile
from .models import Recipe, Ingredient, SourceMetadata, RecipeSource

logger = logging.getLogger(__name__)


class PDFValidationService:
    """Service for validating PDF files before import"""
    
    def validate_file(self, file: UploadedFile) -> Dict[str, Any]:
        """
        Validate a PDF file for recipe import
        
        Args:
            file: Uploaded PDF file
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Check file extension
        if not file.name.lower().endswith('.pdf'):
            errors.append("File must be a PDF")
        
        # Check file size (10MB limit)
        if file.size > 10 * 1024 * 1024:
            errors.append("File size cannot exceed 10MB")
        
        # Check if file is empty
        if file.size == 0:
            errors.append("File is empty")
        
        # Try to read PDF content
        page_count = 0
        try:
            file.seek(0)  # Reset file pointer
            pdf_reader = PyPDF2.PdfReader(file)
            page_count = len(pdf_reader.pages)
            
            if page_count == 0:
                errors.append("PDF contains no pages")
            elif page_count > 10:
                warnings.append(f"PDF has {page_count} pages - only first few will be processed")
            
            # Try to extract some text to verify it's readable
            if page_count > 0:
                first_page = pdf_reader.pages[0]
                text = first_page.extract_text()
                if not text.strip():
                    warnings.append("PDF appears to contain no readable text")
                elif len(text.strip()) < 50:
                    warnings.append("PDF contains very little text")
                    
        except Exception as e:
            errors.append(f"Cannot read PDF file: {str(e)}")
        finally:
            file.seek(0)  # Reset file pointer
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'file_size_bytes': file.size,
            'detected_content_type': file.content_type or 'application/pdf',
            'page_count': page_count
        }


class PDFTextExtractor:
    """Service for extracting text from PDF files"""
    
    def extract_text(self, file: UploadedFile) -> str:
        """
        Extract text from a PDF file
        
        Args:
            file: Uploaded PDF file
            
        Returns:
            Extracted text content
        """
        try:
            file.seek(0)
            pdf_reader = PyPDF2.PdfReader(file)
            
            text_content = []
            # Process up to 5 pages to avoid processing very long documents
            max_pages = min(len(pdf_reader.pages), 5)
            
            for page_num in range(max_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text.strip():
                    text_content.append(text)
            
            return '\n'.join(text_content)
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
        finally:
            file.seek(0)


class RecipeParser:
    """Service for parsing recipe text into structured data"""
    
    def parse_recipe(self, text: str) -> Dict[str, Any]:
        """
        Parse recipe text into structured recipe data
        
        Args:
            text: Raw text extracted from PDF
            
        Returns:
            Dictionary with parsed recipe data
        """
        recipe_data = {
            'title': self._extract_title(text),
            'description': '',
            'prep_time': self._extract_prep_time(text),
            'cook_time': self._extract_cook_time(text),
            'servings': self._extract_servings(text),
            'ingredients': self._extract_ingredients(text),
            'instructions': self._extract_instructions(text),
            'categories': self._extract_categories(text),
            'tags': self._extract_tags(text),
        }
        
        # Calculate total time if both prep and cook times are available
        if recipe_data['prep_time'] and recipe_data['cook_time']:
            recipe_data['total_time'] = recipe_data['prep_time'] + recipe_data['cook_time']
        
        return recipe_data
    
    def _extract_title(self, text: str) -> str:
        """Extract recipe title from text"""
        lines = text.strip().split('\n')
        
        # Try to find a title in the first few lines
        for line in lines[:5]:
            line = line.strip()
            if line and len(line) > 3:
                # Skip lines that look like headers or metadata
                skip_keywords = [
                    'page', 'recipe', 'ingredients', 'instructions', 'serves', 'prep time',
                    'ingrediënten', 'bereidingswijze', 'voor', 'personen', 'bereidingstijd',
                    'minuten', 'preparation', 'cooking time'
                ]
                
                if not any(keyword in line.lower() for keyword in skip_keywords):
                    # Extract title before common patterns
                    title_end_patterns = [
                        r'\s+voor\s+\d+\s+personen?',  # "Voor 2 personen"
                        r'\s+bereidingstijd:?',         # "Bereidingstijd:"
                        r'\s+ingrediënten:?',          # "Ingrediënten:"
                        r'\s+serves?\s+\d+',           # "Serves 4"
                        r'\s+prep\s+time:?',           # "Prep time:"
                        r'\s+preparation\s+time:?',    # "Preparation time:"
                    ]
                    
                    for pattern in title_end_patterns:
                        match = re.search(pattern, line, re.IGNORECASE)
                        if match:
                            title = line[:match.start()].strip()
                            if title and len(title) > 3:
                                return title
                    
                    # If no pattern matches and line is reasonable length, use it
                    if len(line) < 100:
                        return line
        
        # Fallback to first non-empty line
        for line in lines:
            line = line.strip()
            if line:
                return line[:100]  # Limit title length
        
        return "Imported Recipe"
    
    def _extract_prep_time(self, text: str) -> Optional[int]:
        """Extract preparation time in minutes"""
        patterns = [
            r'prep(?:aration)?\s*time[:\s]*(\d+)\s*(?:min|minute|minutes)',
            r'prep[:\s]*(\d+)\s*(?:min|minute|minutes)',
            r'preparation[:\s]*(\d+)\s*(?:min|minute|minutes)',
            r'bereiding[:\s]*(\d+)\s*(?:min|minuten?)',
            r'voorbereidingstijd[:\s]*(\d+)\s*(?:min|minuten?)',
            r'préparation[:\s]*(\d+)\s*(?:min|minutes?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_cook_time(self, text: str) -> Optional[int]:
        """Extract cooking time in minutes"""
        patterns = [
            r'cook(?:ing)?\s*time[:\s]*(\d+)\s*(?:min|minute|minutes)',
            r'cook[:\s]*(\d+)\s*(?:min|minute|minutes)',
            r'bake[:\s]*(\d+)\s*(?:min|minute|minutes)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_servings(self, text: str) -> Optional[int]:
        """Extract number of servings"""
        patterns = [
            r'serves?[:\s]*(\d+)',
            r'servings?[:\s]*(\d+)',
            r'yield[:\s]*(\d+)',
            r'makes?[:\s]*(\d+)',
            r'voor[:\s]*(\d+)\s*(?:personen?|people)',
            r'(\d+)\s*(?:personen?|people)',
            r'portions?[:\s]*(\d+)',
            r'pour[:\s]*(\d+)\s*(?:personnes?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_ingredients(self, text: str) -> List[Dict[str, Any]]:
        """Extract ingredients list"""
        ingredients = []
        
        # Find ingredients section - support multiple languages with better patterns
        ingredients_patterns = [
            # English patterns
            r'ingredients?[:\s]*\n(.*?)(?=\n\s*(?:instructions?|method|directions?|preparation|bereidingswijze)\s*[:\n]|$)',
            # Dutch patterns - more specific
            r'ingrediënten[:\s]*\n(.*?)(?=\n\s*(?:bereidingswijze|instructies?|methode|dressing)\s*[:\n]|$)',
            r'ingrediënten[:\s]*(.*?)(?=bereidingswijze|instructies?|methode|dressing)',
            # French patterns
            r'ingrédients[:\s]*\n(.*?)(?=\n\s*(?:préparation|instructions?|méthode)\s*[:\n]|$)',
            # Fallback - look for bullet point sections before instructions
            r'((?:^\s*[●•*\-]\s*.+\n?)+)(?=.*(?:bereidingswijze|instructions?|method))',
        ]
        
        ingredients_match = None
        for pattern in ingredients_patterns:
            ingredients_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if ingredients_match:
                break
        
        if not ingredients_match:
            # Try alternative patterns - look for bullet points or numbered lists
            ingredients_match = re.search(
                r'((?:^\s*[●•*-]\s*.+\n?)+)',
                text,
                re.MULTILINE
            )
        
        if ingredients_match:
            ingredients_text = ingredients_match.group(1).strip()
            
            # Check if ingredients are separated by bullet points on a single line
            if '●' in ingredients_text or '•' in ingredients_text:
                # Split by bullet points using regex to preserve content
                ingredient_items = re.split(r'[●•]', ingredients_text)
                # Remove empty items and clean up
                ingredient_items = [item.strip() for item in ingredient_items if item.strip()]
                
                # Remove the first item if it's just the header (like "Ingrediënten:")
                if ingredient_items and any(keyword in ingredient_items[0].lower() for keyword in ['ingrediënten', 'ingredients', 'ingrédients']):
                    ingredient_items = ingredient_items[1:]
            else:
                # Normal line-by-line format
                lines = ingredients_text.split('\n')
                ingredient_items = []
                for line in lines:
                    line = line.strip()
                    if line and (line.startswith('-') or line.startswith('•') or line.startswith('*') or 
                               line.startswith('●') or re.match(r'^\d+\.?\s', line)):
                        # Clean up the line
                        ingredient_text = re.sub(r'^[●•*\-\d\.]\s*', '', line).strip()
                        if ingredient_text:
                            ingredient_items.append(ingredient_text)
            
            # Process each ingredient item
            order = 0
            for ingredient_text in ingredient_items:
                ingredient_text = ingredient_text.strip()
                if ingredient_text and self._is_valid_ingredient(ingredient_text):
                    # Try to parse amount and ingredient name - support metric units
                    amount_patterns = [
                        r'^(\d+(?:[.,]\d+)?\s*(?:gram|g|ml|l|el|tl|theelepel|eetlepel|handjes?))\s+(.+)',
                        r'^([\d\s/½¼¾]+(?:\s*(?:cups?|tbsp|tsp|oz|lb|g|kg|ml|l|gram|el|theelepel|eetlepel|handjes?))?)\s+(.+)',
                    ]
                    
                    amount = ''
                    name = ingredient_text
                    
                    for pattern in amount_patterns:
                        amount_match = re.match(pattern, ingredient_text, re.IGNORECASE)
                        if amount_match:
                            amount = amount_match.group(1).strip()
                            name = amount_match.group(2).strip()
                            break
                    
                    # Final validation of the ingredient name
                    if self._is_valid_ingredient_name(name):
                        ingredients.append({
                            'name': name,
                            'amount': amount,
                            'unit': '',
                            'notes': '',
                            'category': 'other',
                            'order': order
                        })
                        order += 1
        
        return ingredients
    
    def _extract_instructions(self, text: str) -> List[str]:
        """Extract cooking instructions"""
        instructions = []
        
        # Find instructions section - support multiple languages with better patterns
        instructions_patterns = [
            # English patterns
            r'(?:instructions?|method|directions?|preparation)[:\s]*\n(.*?)(?=\n\s*(?:notes?|tips?)\s*[:\n]|$)',
            # Dutch patterns - more specific
            r'bereidingswijze[:\s]*\n?(.*?)(?=\n\s*(?:opmerkingen?|tips?|dressing\s+ingrediënten)\s*[:\n]|$)',
            r'bereidingswijze[:\s]*(.*?)(?=dressing\s+ingrediënten|$)',
            # French patterns
            r'(?:préparation|instructions?|méthode)[:\s]*\n(.*?)(?=\n\s*(?:notes?|conseils?)\s*[:\n]|$)',
        ]
        
        instructions_match = None
        for pattern in instructions_patterns:
            instructions_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if instructions_match:
                break
        
        if instructions_match:
            instructions_text = instructions_match.group(1)
            
            # If it's a single paragraph, treat it as one instruction
            if '\n' not in instructions_text.strip() or len(instructions_text.strip().split('\n')) <= 2:
                instructions.append(instructions_text.strip())
            else:
                lines = instructions_text.strip().split('\n')
                
                current_step = []
                for line in lines:
                    line = line.strip()
                    if line:
                        if re.match(r'^\d+\.?\s', line):
                            # New numbered step
                            if current_step:
                                instructions.append(' '.join(current_step))
                            current_step = [re.sub(r'^\d+\.?\s*', '', line)]
                        elif line.startswith('-') or line.startswith('•') or line.startswith('●'):
                            # Bullet point step
                            if current_step:
                                instructions.append(' '.join(current_step))
                            current_step = [re.sub(r'^[●•\-]\s*', '', line)]
                        else:
                            # Continuation of current step
                            current_step.append(line)
                
                # Add the last step
                if current_step:
                    instructions.append(' '.join(current_step))
        
        return instructions
    
    def _extract_categories(self, text: str) -> List[str]:
        """Extract recipe categories"""
        categories = []
        
        # Look for common category keywords
        category_keywords = {
            'breakfast': ['breakfast', 'morning'],
            'lunch': ['lunch', 'midday'],
            'dinner': ['dinner', 'evening', 'supper'],
            'dessert': ['dessert', 'sweet', 'cake', 'cookie'],
            'appetizer': ['appetizer', 'starter', 'hors d\'oeuvre'],
            'main course': ['main', 'entree', 'entrée'],
            'side dish': ['side', 'accompaniment'],
            'soup': ['soup', 'broth', 'bisque'],
            'salad': ['salad', 'greens'],
        }
        
        text_lower = text.lower()
        for category, keywords in category_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                categories.append(category)
        
        return categories if categories else ['main course']
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract recipe tags"""
        tags = []
        
        # Look for common tag keywords
        tag_keywords = {
            'quick': ['quick', 'fast', '15 min', '20 min', '30 min'],
            'easy': ['easy', 'simple', 'basic'],
            'healthy': ['healthy', 'nutritious', 'low fat', 'low calorie'],
            'vegetarian': ['vegetarian', 'veggie'],
            'vegan': ['vegan'],
            'gluten-free': ['gluten free', 'gluten-free'],
            'dairy-free': ['dairy free', 'dairy-free'],
            'spicy': ['spicy', 'hot', 'chili', 'pepper'],
        }
        
        text_lower = text.lower()
        for tag, keywords in tag_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                tags.append(tag)
        
        return tags
    
    def _is_valid_ingredient(self, text: str) -> bool:
        """Check if text looks like a valid ingredient (not instructions)"""
        if not text or len(text.strip()) < 2:
            return False
            
        text_lower = text.lower().strip()
        
        # Skip if it contains obvious instruction keywords
        instruction_keywords = [
            'bereidingswijze', 'bereiding', 'snijd de', 'voeg de', 'haal de', 
            'doe de', 'meng de', 'bereid het', 'was en', 'verwijder',
            'pureer', 'giet', 'bewaar', 'serveer', 'maak de', 'bestrooi',
            'instructions', 'method', 'cook the', 'add the', 'mix the'
        ]
        
        if any(keyword in text_lower for keyword in instruction_keywords):
            return False
            
        # Skip if it's too long (likely instructions)
        if len(text) > 150:
            return False
            
        # Skip if it contains multiple sentences
        if text.count('.') > 1 and len(text) > 50:
            return False
            
        return True
    
    def _is_valid_ingredient_name(self, name: str) -> bool:
        """Validate that an ingredient name is reasonable"""
        if not name or len(name.strip()) < 2:
            return False
            
        name = name.strip()
        
        # Skip very long names (likely contain instructions)
        if len(name) > 100:
            return False
            
        # Skip names that are clearly instructions
        instruction_starters = [
            'bereid het', 'snijd de', 'voeg de', 'haal de', 'doe de',
            'meng de', 'was en', 'verwijder', 'pureer', 'giet',
            'cook the', 'add the', 'mix the', 'heat the'
        ]
        
        name_lower = name.lower()
        if any(name_lower.startswith(starter) for starter in instruction_starters):
            return False
            
        return True


class RecipeImportService:
    """Service for importing recipes from PDF files"""
    
    def __init__(self):
        self.text_extractor = PDFTextExtractor()
        self.parser = RecipeParser()
    
    def import_from_pdf(self, file: UploadedFile, user) -> Recipe:
        """
        Import a recipe from a PDF file and save to database
        
        Args:
            file: Uploaded PDF file
            user: User who owns this recipe
            
        Returns:
            Created Recipe instance
        """
        try:
            # Extract text from PDF
            text = self.text_extractor.extract_text(file)
            
            # Parse recipe data
            recipe_data = self.parser.parse_recipe(text)
            
            # Create recipe
            ingredients_data = recipe_data.pop('ingredients', [])
            recipe_data['source'] = RecipeSource.PDF
            recipe_data['user'] = user
            
            recipe = Recipe.objects.create(**recipe_data)
            
            # Create ingredients
            for ingredient_data in ingredients_data:
                Ingredient.objects.create(recipe=recipe, **ingredient_data)
            
            # Create source metadata
            SourceMetadata.objects.create(
                recipe=recipe,
                original_filename=file.name,
                file_size=file.size,
                raw_text=text,
                import_success=True
            )
            
            logger.info(f"Successfully imported recipe {recipe.id} from {file.name}")
            return recipe
            
        except Exception as e:
            logger.error(f"Error importing recipe from {file.name}: {str(e)}")
            raise
    
    def preview_from_pdf(self, file: UploadedFile) -> Dict[str, Any]:
        """
        Preview a recipe from a PDF file without saving to database
        
        Args:
            file: Uploaded PDF file
            
        Returns:
            Dictionary with parsed recipe data
        """
        try:
            # Extract text from PDF
            text = self.text_extractor.extract_text(file)
            
            # Parse recipe data
            recipe_data = self.parser.parse_recipe(text)
            recipe_data['source'] = RecipeSource.PDF
            
            logger.info(f"Successfully previewed recipe from {file.name}")
            return recipe_data
            
        except Exception as e:
            logger.error(f"Error previewing recipe from {file.name}: {str(e)}")
            raise