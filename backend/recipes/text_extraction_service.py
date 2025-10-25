"""
Enhanced text extraction service for recipes from PDFs and images
"""
import os
import re
import logging
from typing import Dict, List, Any, Optional, Union
from django.core.files.uploadedfile import UploadedFile
from PIL import Image
import PyPDF2

logger = logging.getLogger(__name__)

# Try to import OCR libraries
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("pytesseract not available - image OCR will be disabled")

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    logger.warning("easyocr not available - advanced image OCR will be disabled")

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    logger.warning("opencv not available - image preprocessing will be limited")


class TextExtractionService:
    """Service for extracting text from PDFs and images"""
    
    def __init__(self):
        self.easyocr_reader = None
        if EASYOCR_AVAILABLE:
            try:
                # Initialize EasyOCR reader for English and Dutch
                self.easyocr_reader = easyocr.Reader(['en', 'nl'])
            except Exception as e:
                logger.warning(f"Failed to initialize EasyOCR: {e}")
                self.easyocr_reader = None
    
    def extract_text_from_file(self, file: UploadedFile) -> Dict[str, Any]:
        """
        Extract text from uploaded file (PDF or image)
        
        Args:
            file: Uploaded file
            
        Returns:
            Dictionary with extracted text and metadata
        """
        file_extension = file.name.lower().split('.')[-1] if '.' in file.name else ''
        
        if file_extension == 'pdf':
            return self.extract_text_from_pdf(file)
        elif file_extension in ['png', 'jpg', 'jpeg', 'tiff', 'bmp', 'webp']:
            return self.extract_text_from_image(file)
        else:
            return {
                'success': False,
                'error': f'Unsupported file type: {file_extension}',
                'text': '',
                'method': 'none'
            }
    
    def extract_text_from_pdf(self, file: UploadedFile) -> Dict[str, Any]:
        """Extract text from PDF file"""
        try:
            file.seek(0)
            pdf_reader = PyPDF2.PdfReader(file)
            
            text_content = []
            page_count = len(pdf_reader.pages)
            
            # Extract text from first 5 pages (to avoid processing huge documents)
            max_pages = min(page_count, 5)
            
            for page_num in range(max_pages):
                try:
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text.strip():
                        text_content.append(text)
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
            
            full_text = '\n'.join(text_content)
            
            return {
                'success': True,
                'text': full_text,
                'method': 'pdf_extraction',
                'pages_processed': max_pages,
                'total_pages': page_count,
                'character_count': len(full_text)
            }
            
        except Exception as e:
            logger.error(f"PDF text extraction failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'method': 'pdf_extraction'
            }
    
    def extract_text_from_image(self, file: UploadedFile) -> Dict[str, Any]:
        """Extract text from image file using OCR"""
        try:
            file.seek(0)
            logger.info(f"Opening image file: {file.name}, size: {file.size}, content_type: {file.content_type}")
            
            # Validate file size and type
            if file.size == 0:
                raise ValueError("Image file is empty")
            
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                raise ValueError("Image file too large (max 10MB)")
            
            image = Image.open(file)
            logger.info(f"Image opened successfully: {image.size}, mode: {image.mode}")
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Try multiple OCR methods
            results = []
            
            # Method 1: EasyOCR (best for recipe text)
            if self.easyocr_reader:
                try:
                    import numpy as np
                    img_array = np.array(image)
                    ocr_results = self.easyocr_reader.readtext(img_array)
                    
                    # Extract text from EasyOCR results
                    easyocr_text = ' '.join([result[1] for result in ocr_results if result[2] > 0.5])
                    
                    if easyocr_text.strip():
                        results.append({
                            'method': 'easyocr',
                            'text': easyocr_text,
                            'confidence': 'high'
                        })
                except Exception as e:
                    logger.warning(f"EasyOCR failed: {e}")
            
            # Method 2: Tesseract OCR
            if TESSERACT_AVAILABLE:
                try:
                    # Preprocess image for better OCR
                    processed_image = self._preprocess_image_for_ocr(image)
                    
                    # Extract text with Tesseract
                    tesseract_text = pytesseract.image_to_string(processed_image, lang='eng+nld')
                    
                    if tesseract_text.strip():
                        results.append({
                            'method': 'tesseract',
                            'text': tesseract_text,
                            'confidence': 'medium'
                        })
                except Exception as e:
                    logger.warning(f"Tesseract OCR failed: {e}")
            
            # Choose the best result
            if results:
                # Prefer EasyOCR if available, otherwise use Tesseract
                best_result = results[0]
                for result in results:
                    if result['method'] == 'easyocr':
                        best_result = result
                        break
                
                return {
                    'success': True,
                    'text': best_result['text'],
                    'method': best_result['method'],
                    'confidence': best_result['confidence'],
                    'image_size': image.size,
                    'available_methods': [r['method'] for r in results]
                }
            else:
                return {
                    'success': False,
                    'error': 'No OCR methods available or all methods failed',
                    'text': '',
                    'method': 'none',
                    'tesseract_available': TESSERACT_AVAILABLE,
                    'easyocr_available': EASYOCR_AVAILABLE
                }
                
        except Exception as e:
            logger.error(f"Image text extraction failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'method': 'image_ocr'
            }
    
    def _preprocess_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """Preprocess image to improve OCR accuracy"""
        try:
            if not OPENCV_AVAILABLE:
                # Basic preprocessing without OpenCV
                # Convert to grayscale
                if image.mode != 'L':
                    image = image.convert('L')
                
                # Enhance contrast
                from PIL import ImageEnhance
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(2.0)
                
                return image
            
            # Advanced preprocessing with OpenCV
            import numpy as np
            
            # Convert PIL to OpenCV format
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Apply image processing techniques
            # 1. Noise reduction
            img_array = cv2.medianBlur(img_array, 3)
            
            # 2. Threshold to get better contrast
            _, img_array = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 3. Morphological operations to clean up
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            img_array = cv2.morphologyEx(img_array, cv2.MORPH_CLOSE, kernel)
            
            # Convert back to PIL
            return Image.fromarray(img_array)
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}")
            return image


class RecipeTextParser:
    """Parse extracted text to identify recipe components"""
    
    def parse_recipe_text(self, text: str) -> Dict[str, Any]:
        """
        Parse extracted text to identify recipe components
        
        Args:
            text: Raw extracted text
            
        Returns:
            Dictionary with parsed recipe components
        """
        if not text or not text.strip():
            return {
                'success': False,
                'error': 'No text to parse',
                'recipe_data': {}
            }
        
        try:
            recipe_data = {
                'title': self._extract_title(text),
                'ingredients': self._extract_ingredients(text),
                'instructions': self._extract_instructions(text),
                'prep_time': self._extract_prep_time(text),
                'cook_time': self._extract_cook_time(text),
                'servings': self._extract_servings(text),
                'description': self._extract_description(text)
            }
            
            return {
                'success': True,
                'recipe_data': recipe_data,
                'raw_text': text[:500] + '...' if len(text) > 500 else text
            }
            
        except Exception as e:
            logger.error(f"Recipe text parsing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'recipe_data': {},
                'raw_text': text[:500] + '...' if len(text) > 500 else text
            }
    
    def _extract_title(self, text: str) -> str:
        """Extract recipe title from text"""
        lines = text.split('\n')
        
        # Look for title patterns
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if len(line) > 5 and len(line) < 100:
                # Skip lines that look like ingredients or instructions
                if not re.search(r'^\d+\s*(cups?|tbsp|tsp|ml|gram|kg)', line.lower()):
                    if not line.lower().startswith(('step', 'instruction', 'method')):
                        return line
        
        return "Imported Recipe"
    
    def _extract_ingredients(self, text: str) -> List[str]:
        """Extract ingredients list from text"""
        ingredients = []
        lines = text.split('\n')
        
        # Look for ingredient patterns
        ingredient_patterns = [
            r'^\s*[-•*]\s*(.+)',  # Bullet points
            r'^\s*\d+\s*(cups?|tbsp|tsp|ml|gram|kg|oz|lb)\s*(.+)',  # Measurements
            r'^\s*\d+\s*(.+)',  # Numbered items
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            for pattern in ingredient_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    ingredient = match.group(1) if len(match.groups()) == 1 else match.group(2)
                    if ingredient and len(ingredient) > 2:
                        ingredients.append(ingredient.strip())
                    break
        
        return ingredients[:20]  # Limit to 20 ingredients
    
    def _extract_instructions(self, text: str) -> List[str]:
        """Extract cooking instructions from text"""
        instructions = []
        lines = text.split('\n')
        
        # Look for instruction patterns
        instruction_patterns = [
            r'^\s*\d+\.\s*(.+)',  # Numbered steps
            r'^\s*(step\s*\d+:?\s*)?(.+)',  # Step indicators
        ]
        
        in_instructions_section = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if we're entering instructions section
            if re.search(r'(instructions?|method|directions?|steps?)', line.lower()):
                in_instructions_section = True
                continue
            
            if in_instructions_section or len(instructions) > 0:
                for pattern in instruction_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        instruction = match.group(1) if len(match.groups()) == 1 else match.group(2)
                        if instruction and len(instruction) > 10:
                            instructions.append(instruction.strip())
                        break
                else:
                    # If line is long enough and looks like an instruction
                    if len(line) > 20 and not re.search(r'^\d+\s*(cups?|tbsp|tsp)', line.lower()):
                        instructions.append(line)
        
        return instructions[:15]  # Limit to 15 steps
    
    def _extract_prep_time(self, text: str) -> Optional[int]:
        """Extract preparation time in minutes"""
        patterns = [
            r'prep(?:aration)?\s*time:?\s*(\d+)\s*(?:min|minutes?)',
            r'prep:?\s*(\d+)\s*(?:min|minutes?)',
            r'preparation:?\s*(\d+)\s*(?:min|minutes?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_cook_time(self, text: str) -> Optional[int]:
        """Extract cooking time in minutes"""
        patterns = [
            r'cook(?:ing)?\s*time:?\s*(\d+)\s*(?:min|minutes?)',
            r'cook:?\s*(\d+)\s*(?:min|minutes?)',
            r'bake:?\s*(\d+)\s*(?:min|minutes?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_servings(self, text: str) -> Optional[int]:
        """Extract number of servings"""
        patterns = [
            r'serves?:?\s*(\d+)',
            r'servings?:?\s*(\d+)',
            r'portions?:?\s*(\d+)',
            r'for\s*(\d+)\s*people',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_description(self, text: str) -> str:
        """Extract recipe description"""
        lines = text.split('\n')
        
        # Look for description in first few lines
        for line in lines[:3]:
            line = line.strip()
            if len(line) > 20 and len(line) < 200:
                # Skip title-like lines and ingredient lines
                if not re.search(r'^\d+\s*(cups?|tbsp|tsp)', line.lower()):
                    if not line.isupper():  # Skip all-caps titles
                        return line
        
        return ""


# Combined service for easy use
class EnhancedRecipeImportService:
    """Combined service for importing recipes from PDFs and images"""
    
    def __init__(self):
        self.text_extractor = TextExtractionService()
        self.recipe_parser = RecipeTextParser()
    
    def import_recipe_from_file(self, file: UploadedFile) -> Dict[str, Any]:
        """
        Import recipe from uploaded file (PDF or image)
        
        Args:
            file: Uploaded file
            
        Returns:
            Dictionary with import results and parsed recipe data
        """
        # Step 1: Extract text
        extraction_result = self.text_extractor.extract_text_from_file(file)
        
        if not extraction_result['success']:
            return {
                'success': False,
                'error': extraction_result['error'],
                'stage': 'text_extraction'
            }
        
        # Step 2: Parse recipe components
        parsing_result = self.recipe_parser.parse_recipe_text(extraction_result['text'])
        
        if not parsing_result['success']:
            return {
                'success': False,
                'error': parsing_result['error'],
                'stage': 'recipe_parsing',
                'extraction_result': extraction_result
            }
        
        return {
            'success': True,
            'recipe_data': parsing_result['recipe_data'],
            'extraction_method': extraction_result.get('method', 'unknown'),
            'extraction_metadata': {
                k: v for k, v in extraction_result.items() 
                if k not in ['success', 'text', 'error']
            },
            'raw_text_preview': parsing_result.get('raw_text', '')
        }