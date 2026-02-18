from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    tenant = models.ForeignKey(
        'tenants.Tenant', 
        on_delete=models.CASCADE, 
        related_name='users',
        null=True,
        blank=True
    )
    
    # Profile information
    phone_number = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        blank=True,
        null=True
    )
    date_of_birth = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    # Status and timestamps
    is_email_verified = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        ordering = ['email']
        indexes = [
            models.Index(fields=['tenant', 'role']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.email} ({self.role})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_tenant_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_teacher_or_admin(self):
        return self.role in ['admin', 'teacher'] or self.is_superuser


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Learning preferences
    preferred_language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    
    # Additional fields for students
    student_id = models.CharField(max_length=50, blank=True, null=True)
    grade_level = models.CharField(max_length=20, blank=True, null=True)
    
    # Additional fields for teachers
    employee_id = models.CharField(max_length=50, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    specialization = models.CharField(max_length=200, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'

    def __str__(self):
        return f"{self.user.full_name} Profile"


class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_sessions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.session_key[:8]}..."
