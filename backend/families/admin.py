from django.contrib import admin
from .models import Family, FamilyMember, FamilyInvitation


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ['name', 'member_count', 'admin_count', 'created_at']
    list_filter = ['created_at', 'meal_planning_start_day', 'shopping_day']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'member_count', 'admin_count']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Settings', {
            'fields': ('default_servings', 'meal_planning_start_day', 'shopping_day')
        }),
        ('Metadata', {
            'fields': ('id', 'member_count', 'admin_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'family', 'role', 'display_name', 'joined_at']
    list_filter = ['role', 'joined_at', 'can_create_meal_plans', 'can_manage_recipes']
    search_fields = ['user__username', 'user__email', 'family__name']
    readonly_fields = ['id', 'joined_at', 'updated_at', 'display_name']
    
    fieldsets = (
        (None, {
            'fields': ('family', 'user', 'role')
        }),
        ('Permissions', {
            'fields': (
                'can_create_meal_plans', 'can_manage_recipes', 
                'can_manage_shopping_lists', 'can_invite_members'
            )
        }),
        ('Preferences', {
            'fields': ('dietary_restrictions', 'favorite_cuisines')
        }),
        ('Metadata', {
            'fields': ('id', 'display_name', 'joined_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(FamilyInvitation)
class FamilyInvitationAdmin(admin.ModelAdmin):
    list_display = ['email', 'family', 'role', 'status', 'invited_by', 'created_at']
    list_filter = ['status', 'role', 'created_at', 'expires_at']
    search_fields = ['email', 'family__name', 'invited_by__username']
    readonly_fields = ['id', 'created_at', 'responded_at', 'is_expired']
    
    fieldsets = (
        (None, {
            'fields': ('family', 'invited_by', 'email', 'role')
        }),
        ('Status', {
            'fields': ('status', 'expires_at', 'responded_at', 'is_expired')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        })
    )