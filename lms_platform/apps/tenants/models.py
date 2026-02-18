from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid


class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    subdomain = models.CharField(
        max_length=100,
        unique=True,
        validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9-]+$',
                message='Subdomain can only contain letters, numbers, and hyphens.'
            )
        ]
    )
    domain = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Subscription details
    plan_type = models.CharField(
        max_length=20,
        choices=[
            ('basic', 'Basic'),
            ('pro', 'Professional'),
            ('enterprise', 'Enterprise'),
        ],
        default='basic'
    )
    max_users = models.IntegerField(default=50)
    max_courses = models.IntegerField(default=10)
    
    class Meta:
        db_table = 'tenants'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def is_enterprise(self):
        return self.plan_type == 'enterprise'

    @property
    def user_count(self):
        from apps.users.models import User
        return User.objects.filter(tenant=self).count()

    @property
    def course_count(self):
        from apps.courses.models import Course
        return Course.objects.filter(tenant=self).count()


class TenantSettings(models.Model):
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='settings')
    logo = models.ImageField(upload_to='tenant_logos/', blank=True, null=True)
    primary_color = models.CharField(max_length=7, default='#007bff')
    secondary_color = models.CharField(max_length=7, default='#6c757d')
    custom_css = models.TextField(blank=True, null=True)
    allow_signup = models.BooleanField(default=True)
    require_email_verification = models.BooleanField(default=True)
    session_timeout = models.IntegerField(default=30)  # minutes
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tenant_settings'

    def __str__(self):
        return f"{self.tenant.name} Settings"
