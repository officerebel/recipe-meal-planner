from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from recipes.models import Recipe, Ingredient, IngredientCategory
from families.models import Family, FamilyMember
import uuid


class Command(BaseCommand):
    help = 'Create sample data for the Recipe Meal Planner'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-if-exists',
            action='store_true',
            help='Skip creation if data already exists',
        )

    def handle(self, *args, **options):
        if options['skip_if_exists'] and Recipe.objects.exists():
            self.stdout.write(
                self.style.WARNING('Sample data already exists. Skipping creation.')
            )
            return

        self.stdout.write('Creating sample data...')

        # Create sample user
        user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={
                'email': 'demo@example.com',
                'first_name': 'Demo',
                'last_name': 'User'
            }
        )

        if created:
            user.set_password('demo123')
            user.save()
            self.stdout.write(f'Created demo user: {user.username}')

        # Create sample family
        family, created = Family.objects.get_or_create(
            name='Demo Familie',
            defaults={
                'description': 'Demo familie voor het testen van de app',
                'default_servings': 4
            }
        )

        if created:
            FamilyMember.objects.create(
                family=family,
                user=user,
                role='admin',
                can_invite_members=True
            )
            self.stdout.write(f'Created demo family: {family.name}')

        # Sample recipes data
        sample_recipes = [
            {
                'title': 'Spaghetti Carbonara',
                'description': 'Klassieke Italiaanse pasta met spek en ei',
                'prep_time': 15,
                'cook_time': 20,
                'servings': 4,
                'categories': ['Hoofdgerecht', 'Pasta', 'Italiaans'],
                'tags': ['Snel', 'Makkelijk', 'Comfort Food'],
                'ingredients': [
                    {'name': 'Spaghetti', 'amount': '400g', 'category': IngredientCategory.PANTRY},
                    {'name': 'Spek (guanciale)', 'amount': '150g', 'category': IngredientCategory.MEAT},
                    {'name': 'Eieren', 'amount': '4 stuks', 'category': IngredientCategory.DAIRY},
                    {'name': 'Parmezaanse kaas', 'amount': '100g', 'category': IngredientCategory.DAIRY},
                    {'name': 'Zwarte peper', 'amount': 'naar smaak', 'category': IngredientCategory.SPICES},
                ],
                'instructions': [
                    'Kook de spaghetti volgens de verpakking',
                    'Bak het spek knapperig in een grote pan',
                    'Klop de eieren met geraspte parmezaan',
                    'Meng de warme pasta met het spek',
                    'Voeg het eimengsel toe en roer snel door',
                    'Serveer direct met extra parmezaan en peper'
                ]
            },
            {
                'title': 'Griekse Salade',
                'description': 'Frisse Mediterrane salade met feta',
                'prep_time': 15,
                'cook_time': 0,
                'servings': 2,
                'categories': ['Salade', 'Lunch', 'Grieks'],
                'tags': ['Gezond', 'Vegetarisch', 'Fris', 'Snel'],
                'ingredients': [
                    {'name': 'Tomaten', 'amount': '3 grote', 'category': IngredientCategory.PRODUCE},
                    {'name': 'Komkommer', 'amount': '1 stuk', 'category': IngredientCategory.PRODUCE},
                    {'name': 'Rode ui', 'amount': '1/2 stuk', 'category': IngredientCategory.PRODUCE},
                    {'name': 'Feta kaas', 'amount': '200g', 'category': IngredientCategory.DAIRY},
                    {'name': 'Olijven', 'amount': '100g', 'category': IngredientCategory.PANTRY},
                    {'name': 'Olijfolie', 'amount': '3 eetlepels', 'category': IngredientCategory.PANTRY},
                ],
                'instructions': [
                    'Snijd tomaten en komkommer in blokjes',
                    'Snijd de rode ui in dunne ringen',
                    'Meng alle groenten in een grote kom',
                    'Voeg de feta en olijven toe',
                    'Besprenkel met olijfolie en kruiden',
                    'Laat 10 minuten marineren voor serveren'
                ]
            },
            {
                'title': 'Pannenkoeken',
                'description': 'Nederlandse pannenkoeken voor het hele gezin',
                'prep_time': 10,
                'cook_time': 20,
                'servings': 4,
                'categories': ['Ontbijt', 'Dessert', 'Nederlands'],
                'tags': ['Familie', 'Weekend', 'Zoet', 'Kinderen'],
                'ingredients': [
                    {'name': 'Bloem', 'amount': '250g', 'category': IngredientCategory.PANTRY},
                    {'name': 'Melk', 'amount': '500ml', 'category': IngredientCategory.DAIRY},
                    {'name': 'Eieren', 'amount': '2 stuks', 'category': IngredientCategory.DAIRY},
                    {'name': 'Zout', 'amount': 'snufje', 'category': IngredientCategory.SPICES},
                    {'name': 'Boter', 'amount': 'voor bakken', 'category': IngredientCategory.DAIRY},
                ],
                'instructions': [
                    'Meng bloem en zout in een kom',
                    'Voeg geleidelijk melk toe terwijl je roert',
                    'Klop de eieren erdoor tot een glad beslag',
                    'Laat het beslag 30 minuten rusten',
                    'Bak dunne pannenkoeken in boter',
                    'Serveer met stroop, suiker of fruit'
                ]
            }
        ]

        # Create sample recipes
        for recipe_data in sample_recipes:
            recipe, created = Recipe.objects.get_or_create(
                title=recipe_data['title'],
                user=user,
                defaults={
                    'description': recipe_data['description'],
                    'prep_time': recipe_data['prep_time'],
                    'cook_time': recipe_data['cook_time'],
                    'servings': recipe_data['servings'],
                    'categories': recipe_data['categories'],
                    'tags': recipe_data['tags'],
                    'instructions': recipe_data['instructions']
                }
            )

            if created:
                # Add ingredients
                for i, ingredient_data in enumerate(recipe_data['ingredients']):
                    Ingredient.objects.create(
                        recipe=recipe,
                        name=ingredient_data['name'],
                        amount=ingredient_data['amount'],
                        category=ingredient_data['category'],
                        order=i
                    )

                self.stdout.write(f'Created recipe: {recipe.title}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Demo user credentials: demo_user / demo123')
        )