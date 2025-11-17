#!/usr/bin/env python3
"""Quick test of recipe parser"""

text = '''recept Bloemkoolcouscous salade met avocado, amandel en kikkererwten
voor 2 personen
Bereidingstijd: 25 minuten
Ingrediënten:
• 200 gram broccoli in roosjes
Bereidingswijze:
Breek de broccoli in roosjes en kook ongeveer 5 minuten tot ze beetgaar gaan.
Snij de ui en knoflook fijn. Bak in wat olijfolie de ui en knoflook tot deze glazig kijk.
Voeg daarna de bloemkoolrijst toe en bak kort mee.
'''

import sys
sys.path.insert(0, '.')
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recipe_meal_planner.settings')

import django
django.setup()

from recipes.services import RecipeImportService

parser = RecipeImportService().parser
result = parser.parse_recipe(text)

print('=' * 60)
print('TITLE:', result['title'])
print('=' * 60)
print('INSTRUCTIONS:')
for i, instruction in enumerate(result['instructions'], 1):
    print(f"{i}. {instruction}")
print('=' * 60)
