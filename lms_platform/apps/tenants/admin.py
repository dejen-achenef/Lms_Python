from django.contrib import admin
from .models import Tenant, TenantSettings


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'subdomain', 'domain', 'plan_type', 'is_active', 'created_at']
    list_filter = ['is_active', 'plan_type', 'created_at']
    search_fields = ['name', 'subdomain', 'domain']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'subdomain', 'domain', 'is_active')
        }),
        ('Plan Information', {
            'fields': ('plan_type', 'max_users', 'max_courses')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TenantSettings)
class TenantSettingsAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'allow_signup', 'require_email_verification', 'session_timeout']
    list_filter = ['allow_signup', 'require_email_verification']
    search_fields = ['tenant__name']
