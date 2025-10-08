from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from families.models import Family, FamilyMember
from django.db import transaction


class Command(BaseCommand):
    help = 'Set up initial data for the application - creates admin user and family with roles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username for the admin user'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@example.com',
            help='Email for the admin user'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Password for the admin user'
        )
        parser.add_argument(
            '--family-name',
            type=str,
            default='My Family',
            help='Name for the default family'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        family_name = options['family_name']

        self.stdout.write('🚀 Starting initial data setup...')

        # Create superuser if it doesn't exist
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Created superuser: {username}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Superuser {username} already exists')
            )

        # Create a default family if none exists for this user
        family, family_created = Family.objects.get_or_create(
            name=family_name,
            defaults={
                'description': f'Default family created for {username}'
            }
        )
        
        if family_created:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Created family: {family.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Family "{family.name}" already exists')
            )

        # Add the admin user as family admin if not already a member
        family_member, member_created = FamilyMember.objects.get_or_create(
            family=family,
            user=user,
            defaults={
                'role': 'admin',
                'can_create_meal_plans': True,
                'can_manage_recipes': True,
                'can_manage_shopping_lists': True,
                'can_invite_members': True
            }
        )
        
        if member_created:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Added {username} as family admin with full permissions')
            )
        else:
            # Update existing member to admin if needed
            if family_member.role != 'admin':
                family_member.role = 'admin'
                family_member.can_create_meal_plans = True
                family_member.can_manage_recipes = True
                family_member.can_manage_shopping_lists = True
                family_member.can_invite_members = True
                family_member.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Updated {username} to admin role')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  {username} is already a family admin')
                )

        # Display summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🎉 Setup completed successfully!'))
        self.stdout.write('')
        self.stdout.write('📋 Summary:')
        self.stdout.write(f'   👤 Admin User: {user.username} ({user.email})')
        self.stdout.write(f'   👨‍👩‍👧‍👦 Family: {family.name}')
        self.stdout.write(f'   🔑 Role: {family_member.role}')
        self.stdout.write('')
        self.stdout.write('🌐 You can now:')
        self.stdout.write('   • Login to your frontend app')
        self.stdout.write('   • Access family settings and roles')
        self.stdout.write('   • Manage family members and permissions')
        self.stdout.write('')
        self.stdout.write(f'🔗 Frontend: https://mealplannerfrontend-production.up.railway.app')
        self.stdout.write(f'🔗 API Docs: https://proud-mercy-production.up.railway.app/api/docs/')
        self.stdout.write(f'🔗 Admin Panel: https://proud-mercy-production.up.railway.app/admin/')
        self.stdout.write('')
        self.stdout.write(f'🔐 Login credentials: {username} / {password}')
        
        # Verify the setup
        self.stdout.write('')
        self.stdout.write('🔍 Verifying setup...')
        
        total_families = Family.objects.count()
        total_members = FamilyMember.objects.count()
        admin_members = FamilyMember.objects.filter(role='admin').count()
        
        self.stdout.write(f'   📊 Total families: {total_families}')
        self.stdout.write(f'   📊 Total members: {total_members}')
        self.stdout.write(f'   📊 Admin members: {admin_members}')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ All systems ready!'))