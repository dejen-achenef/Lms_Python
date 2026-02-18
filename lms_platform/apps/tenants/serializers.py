from rest_framework import serializers
from .models import Tenant, TenantSettings


class TenantSerializer(serializers.ModelSerializer):
    user_count = serializers.ReadOnlyField()
    course_count = serializers.ReadOnlyField()
    is_enterprise = serializers.ReadOnlyField()
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'subdomain', 'domain', 'is_active', 
            'created_at', 'updated_at', 'plan_type', 'max_users', 
            'max_courses', 'user_count', 'course_count', 'is_enterprise'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TenantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ['name', 'subdomain', 'domain', 'plan_type', 'max_users', 'max_courses']
    
    def validate_subdomain(self, value):
        if value.lower() in ['www', 'api', 'admin', 'mail', 'ftp']:
            raise serializers.ValidationError("This subdomain is reserved.")
        return value.lower()


class TenantSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantSettings
        fields = [
            'logo', 'primary_color', 'secondary_color', 'custom_css',
            'allow_signup', 'require_email_verification', 'session_timeout'
        ]
