from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Family(models.Model):
    """Family group for shared meal planning"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, help_text="Family name")
    description = models.TextField(blank=True, help_text="Family description")
    
    # Family settings
    default_servings = models.PositiveIntegerField(
        default=4,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        help_text="Default number of servings for meal plans"
    )
    
    # Meal planning preferences
    meal_planning_start_day = models.CharField(
        max_length=10,
        choices=[
            ('monday', 'Maandag'),
            ('sunday', 'Zondag'),
            ('saturday', 'Zaterdag'),
        ],
        default='monday',
        help_text="Day of the week to start meal planning"
    )
    
    # Shopping preferences
    shopping_day = models.CharField(
        max_length=10,
        choices=[
            ('monday', 'Maandag'),
            ('tuesday', 'Dinsdag'),
            ('wednesday', 'Woensdag'),
            ('thursday', 'Donderdag'),
            ('friday', 'Vrijdag'),
            ('saturday', 'Zaterdag'),
            ('sunday', 'Zondag'),
        ],
        default='saturday',
        help_text="Preferred shopping day"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Family"
        verbose_name_plural = "Families"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def member_count(self):
        """Return the number of family members"""
        return self.members.count()
    
    @property
    def admin_count(self):
        """Return the number of family admins"""
        return self.members.filter(role='admin').count()


class FamilyMember(models.Model):
    """Family member with role and permissions"""
    
    ROLE_CHOICES = [
        ('admin', 'Beheerder'),
        ('member', 'Lid'),
        ('child', 'Kind'),
        ('viewer', 'Kijker'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name='members'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='family_memberships'
    )
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='member',
        help_text="Role within the family"
    )
    
    # Permissions
    can_create_meal_plans = models.BooleanField(
        default=True,
        help_text="Can create and edit meal plans"
    )
    can_manage_recipes = models.BooleanField(
        default=True,
        help_text="Can create and edit recipes"
    )
    can_manage_shopping_lists = models.BooleanField(
        default=True,
        help_text="Can create and edit shopping lists"
    )
    can_invite_members = models.BooleanField(
        default=False,
        help_text="Can invite new family members"
    )
    
    # Child-specific settings
    age = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Age of family member (for child accounts)"
    )
    parental_controls = models.BooleanField(
        default=False,
        help_text="Enable parental controls for this member"
    )
    can_view_all_recipes = models.BooleanField(
        default=True,
        help_text="Can view all family recipes"
    )
    can_suggest_meals = models.BooleanField(
        default=True,
        help_text="Can suggest meals for meal planning"
    )
    
    # Preferences
    dietary_restrictions = models.JSONField(
        default=list,
        help_text="List of dietary restrictions"
    )
    favorite_cuisines = models.JSONField(
        default=list,
        help_text="List of favorite cuisines"
    )
    
    # Metadata
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['family', 'user']
        ordering = ['role', 'user__first_name', 'user__username']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.family.name}"
    
    @property
    def display_name(self):
        """Return display name for the member"""
        return self.user.get_full_name() or self.user.username
    
    def has_permission(self, permission):
        """Check if member has specific permission"""
        if self.role == 'admin':
            return True
        
        # Child users have limited permissions
        if self.role == 'child':
            child_permissions = {
                'view_recipes': self.can_view_all_recipes,
                'suggest_meals': self.can_suggest_meals,
                'create_meal_plans': False,  # Children can't create meal plans
                'manage_recipes': False,     # Children can't manage recipes
                'manage_shopping_lists': False,  # Children can't manage shopping lists
                'invite_members': False,     # Children can't invite members
            }
            return child_permissions.get(permission, False)
        
        permission_map = {
            'create_meal_plans': self.can_create_meal_plans,
            'manage_recipes': self.can_manage_recipes,
            'manage_shopping_lists': self.can_manage_shopping_lists,
            'invite_members': self.can_invite_members,
            'view_recipes': self.can_view_all_recipes,
            'suggest_meals': self.can_suggest_meals,
        }
        
        return permission_map.get(permission, False)
    
    def get_default_permissions_for_role(self):
        """Get default permissions based on role"""
        if self.role == 'admin':
            return {
                'can_create_meal_plans': True,
                'can_manage_recipes': True,
                'can_manage_shopping_lists': True,
                'can_invite_members': True,
                'can_view_all_recipes': True,
                'can_suggest_meals': True,
                'parental_controls': False,
            }
        elif self.role == 'member':
            return {
                'can_create_meal_plans': True,
                'can_manage_recipes': True,
                'can_manage_shopping_lists': True,
                'can_invite_members': False,
                'can_view_all_recipes': True,
                'can_suggest_meals': True,
                'parental_controls': False,
            }
        elif self.role == 'child':
            return {
                'can_create_meal_plans': False,
                'can_manage_recipes': False,
                'can_manage_shopping_lists': False,
                'can_invite_members': False,
                'can_view_all_recipes': True,
                'can_suggest_meals': True,
                'parental_controls': True,
            }
        elif self.role == 'viewer':
            return {
                'can_create_meal_plans': False,
                'can_manage_recipes': False,
                'can_manage_shopping_lists': False,
                'can_invite_members': False,
                'can_view_all_recipes': True,
                'can_suggest_meals': False,
                'parental_controls': False,
            }
        
        return {}
    
    def save(self, *args, **kwargs):
        """Override save to ensure proper permissions are set based on role"""
        # Set default permissions based on role if this is a new instance
        if not self.pk:
            defaults = self.get_default_permissions_for_role()
            for field, value in defaults.items():
                if hasattr(self, field):
                    setattr(self, field, value)
        
        super().save(*args, **kwargs)


class FamilyInvitation(models.Model):
    """Invitation to join a family"""
    
    STATUS_CHOICES = [
        ('pending', 'In afwachting'),
        ('accepted', 'Geaccepteerd'),
        ('declined', 'Afgewezen'),
        ('expired', 'Verlopen'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name='invitations'
    )
    invited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_invitations'
    )
    
    # Invitation details
    email = models.EmailField(help_text="Email address of invitee")
    role = models.CharField(
        max_length=10,
        choices=FamilyMember.ROLE_CHOICES,
        default='member',
        help_text="Role to assign when invitation is accepted"
    )
    
    # Status
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Optional message
    message = models.TextField(
        blank=True,
        help_text="Optional message to include with invitation"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="When invitation expires")
    responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['family', 'email']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invitation to {self.email} for {self.family.name}"
    
    @property
    def is_expired(self):
        """Check if invitation has expired"""
        from django.utils import timezone
        if self.expires_at is None:
            return False
        return timezone.now() > self.expires_at
    
    def accept(self, user):
        """Accept the invitation and create family membership"""
        if self.status != 'pending' or self.is_expired:
            return False
        
        # Create family membership
        FamilyMember.objects.create(
            family=self.family,
            user=user,
            role=self.role
        )
        
        # Update invitation status
        self.status = 'accepted'
        self.responded_at = timezone.now()
        self.save()
        
        return True
    
    def decline(self):
        """Decline the invitation"""
        if self.status != 'pending':
            return False
        
        self.status = 'declined'
        self.responded_at = timezone.now()
        self.save()
        
        return True