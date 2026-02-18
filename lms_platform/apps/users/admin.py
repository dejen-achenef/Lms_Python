from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, UserSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'role', 'tenant', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'is_superuser', 'tenant', 'date_joined']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['email']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'avatar', 'bio')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_email_verified', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Tenant Info', {'fields': ('role', 'tenant')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'role', 'tenant'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'preferred_language', 'timezone', 'email_notifications', 'push_notifications']
    list_filter = ['preferred_language', 'timezone', 'email_notifications', 'push_notifications']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_key', 'ip_address', 'is_active', 'last_activity']
    list_filter = ['is_active', 'created_at', 'last_activity']
    search_fields = ['user__email', 'ip_address', 'session_key']
    readonly_fields = ['session_key', 'created_at', 'last_activity']
