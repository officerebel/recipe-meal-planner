#!/usr/bin/env python3
"""
Create a test recipe image for demonstrating the OCR import feature
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_recipe_image():
    # Create a white background image
    width, height = 800, 1000
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a system font, fallback to default
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 36)
        header_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        text_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 18)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    # Recipe content
    y_position = 50
    
    # Title
    draw.text((50, y_position), "Chocolate Chip Cookies", fill='black', font=title_font)
    y_position += 80
    
    # Description
    draw.text((50, y_position), "Delicious homemade chocolate chip cookies", fill='black', font=text_font)
    y_position += 60
    
    # Prep time and servings
    draw.text((50, y_position), "Prep Time: 15 minutes", fill='black', font=text_font)
    y_position += 30
    draw.text((50, y_position), "Cook Time: 12 minutes", fill='black', font=text_font)
    y_position += 30
    draw.text((50, y_position), "Servings: 24 cookies", fill='black', font=text_font)
    y_position += 60
    
    # Ingredients header
    draw.text((50, y_position), "INGREDIENTS:", fill='black', font=header_font)
    y_position += 40
    
    # Ingredients list
    ingredients = [
        "• 2 1/4 cups all-purpose flour",
        "• 1 tsp baking soda",
        "• 1 tsp salt",
        "• 1 cup butter, softened",
        "• 3/4 cup granulated sugar",
        "• 3/4 cup brown sugar",
        "• 2 large eggs",
        "• 2 tsp vanilla extract",
        "• 2 cups chocolate chips"
    ]
    
    for ingredient in ingredients:
        draw.text((70, y_position), ingredient, fill='black', font=text_font)
        y_position += 25
    
    y_position += 30
    
    # Instructions header
    draw.text((50, y_position), "INSTRUCTIONS:", fill='black', font=header_font)
    y_position += 40
    
    # Instructions
    instructions = [
        "1. Preheat oven to 375°F (190°C).",
        "2. Mix flour, baking soda, and salt in a bowl.",
        "3. Cream butter and sugars until fluffy.",
        "4. Beat in eggs and vanilla.",
        "5. Gradually mix in flour mixture.",
        "6. Stir in chocolate chips.",
        "7. Drop rounded tablespoons onto baking sheets.",
        "8. Bake 9-11 minutes until golden brown.",
        "9. Cool on baking sheet for 2 minutes.",
        "10. Transfer to wire rack to cool completely."
    ]
    
    for instruction in instructions:
        # Wrap long lines
        if len(instruction) > 60:
            words = instruction.split()
            line1 = ' '.join(words[:8])
            line2 = '    ' + ' '.join(words[8:])
            draw.text((70, y_position), line1, fill='black', font=text_font)
            y_position += 25
            draw.text((70, y_position), line2, fill='black', font=text_font)
        else:
            draw.text((70, y_position), instruction, fill='black', font=text_font)
        y_position += 25
    
    # Save the image
    image.save('test_recipe_image.png')
    print("✅ Test recipe image created: test_recipe_image.png")
    print("📁 You can now use this image to test the OCR import feature!")

if __name__ == "__main__":
    create_recipe_image()