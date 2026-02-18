from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import json

User = get_user_model()


class MobileDevice(models.Model):
    """Mobile device registration and management"""
    DEVICE_TYPES = [
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('tablet', 'Tablet'),
        ('web', 'Web'),
        ('desktop', 'Desktop'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('revoked', 'Revoked'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mobile_devices')
    
    # Device information
    device_id = models.CharField(max_length=255, unique=True)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES)
    device_name = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    
    # Software information
    os_version = models.CharField(max_length=50, blank=True, null=True)
    app_version = models.CharField(max_length=50, blank=True, null=True)
    build_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Push notification
    push_token = models.CharField(max_length=500, blank=True, null=True)
    push_enabled = models.BooleanField(default=True)
    
    # Security
    biometric_enabled = models.BooleanField(default=False)
    jailbroken = models.BooleanField(default=False)
    encrypted = models.BooleanField(default=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    last_seen = models.DateTimeField(auto_now=True)
    
    # Usage statistics
    total_sessions = models.IntegerField(default=0)
    total_duration = models.IntegerField(default=0)  # minutes
    data_usage = models.BigIntegerField(default=0)  # bytes
    
    # Preferences
    auto_download_wifi = models.BooleanField(default=True)
    auto_download_cellular = models.BooleanField(default=False)
    video_quality = models.CharField(max_length=20, default='auto', choices=[
        ('auto', 'Auto'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('ultra', 'Ultra'),
    ])
    
    # Metadata
    metadata = models.JSONField(default=dict)
    
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mobile_devices'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['device_type', 'status']),
            models.Index(fields=['last_seen']),
        ]

    def __str__(self):
        return f"{self.device_name} ({self.user.email})"


class OfflineContent(models.Model):
    """Offline content synchronization"""
    CONTENT_TYPES = [
        ('course', 'Course'),
        ('lesson', 'Lesson'),
        ('video', 'Video'),
        ('quiz', 'Quiz'),
        ('document', 'Document'),
        ('audio', 'Audio'),
        ('image', 'Image'),
    ]
    
    SYNC_STATUS = [
        ('pending', 'Pending'),
        ('downloading', 'Downloading'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
        ('deleted', 'Deleted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offline_content')
    device = models.ForeignKey(MobileDevice, on_delete=models.CASCADE, related_name='offline_content')
    
    # Content reference
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content_id = models.CharField(max_length=255)
    content_version = models.IntegerField(default=1)
    
    # File information
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField(default=0)  # bytes
    file_hash = models.CharField(max_length=64, blank=True, null=True)  # SHA-256
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    
    # Synchronization
    sync_status = models.CharField(max_length=20, choices=SYNC_STATUS, default='pending')
    download_progress = models.FloatField(default=0.0)
    download_speed = models.IntegerField(null=True, blank=True)  # bytes per second
    retry_count = models.IntegerField(default=0)
    
    # Timing
    requested_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    # Usage
    access_count = models.IntegerField(default=0)
    last_position = models.BigIntegerField(default=0)  # bytes or seconds
    
    # Cache management
    priority = models.IntegerField(default=0)  # Higher number = higher priority
    auto_delete = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'offline_content'
        unique_together = ['user', 'device', 'content_type', 'content_id']
        indexes = [
            models.Index(fields=['user', 'sync_status']),
            models.Index(fields=['device', 'sync_status']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['priority']),
        ]

    def __str__(self):
        return f"{self.content_type}:{self.content_id} - {self.user.email}"


class SyncSession(models.Model):
    """Synchronization session tracking"""
    SYNC_TYPES = [
        ('full', 'Full Sync'),
        ('incremental', 'Incremental Sync'),
        ('push', 'Push Sync'),
        ('pull', 'Pull Sync'),
    ]
    
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('timeout', 'Timeout'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sync_sessions')
    device = models.ForeignKey(MobileDevice, on_delete=models.CASCADE, related_name='sync_sessions')
    
    # Session details
    sync_type = models.CharField(max_length=20, choices=SYNC_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started')
    
    # Statistics
    total_items = models.IntegerField(default=0)
    processed_items = models.IntegerField(default=0)
    failed_items = models.IntegerField(default=0)
    uploaded_items = models.IntegerField(default=0)
    downloaded_items = models.IntegerField(default=0)
    
    # Data transfer
    bytes_uploaded = models.BigIntegerField(default=0)
    bytes_downloaded = models.BigIntegerField(default=0)
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)  # seconds
    
    # Network information
    connection_type = models.CharField(max_length=20, blank=True, null=True)  # wifi, cellular, etc.
    network_quality = models.CharField(max_length=20, default='good')  # poor, fair, good, excellent
    
    # Error handling
    error_message = models.TextField(blank=True, null=True)
    error_code = models.CharField(max_length=50, blank=True, null=True)
    retry_count = models.IntegerField(default=0)
    
    # Metadata
    metadata = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'sync_sessions'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['device', 'started_at']),
            models.Index(fields=['sync_type', 'status']),
        ]

    def __str__(self):
        return f"{self.sync_type} - {self.user.email} ({self.status})"


class MobileUsageAnalytics(models.Model):
    """Mobile app usage analytics"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mobile_analytics')
    device = models.ForeignKey(MobileDevice, on_delete=models.CASCADE, related_name='analytics')
    
    # Session information
    session_id = models.CharField(max_length=255)
    session_start = models.DateTimeField()
    session_end = models.DateTimeField(null=True, blank=True)
    session_duration = models.IntegerField(null=True, blank=True)  # seconds
    
    # Usage metrics
    screens_viewed = models.IntegerField(default=0)
    actions_performed = models.IntegerField(default=0)
    errors_encountered = models.IntegerField(default=0)
    
    # Content interaction
    lessons_started = models.IntegerField(default=0)
    lessons_completed = models.IntegerField(default=0)
    quiz_attempts = models.IntegerField(default=0)
    videos_watched = models.IntegerField(default=0)
    total_watch_time = models.IntegerField(default=0)  # seconds
    
    # Offline usage
    offline_time = models.IntegerField(default=0)  # seconds
    offline_content_accessed = models.IntegerField(default=0)
    
    # Performance metrics
    app_load_time = models.FloatField(null=True, blank=True)  # seconds
    average_response_time = models.FloatField(null=True, blank=True)  # seconds
    crash_count = models.IntegerField(default=0)
    
    # Geographic data
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    
    # Device performance
    battery_level_start = models.IntegerField(null=True, blank=True)
    battery_level_end = models.IntegerField(null=True, blank=True)
    memory_usage = models.BigIntegerField(null=True, blank=True)  # bytes
    storage_usage = models.BigIntegerField(null=True, blank=True)  # bytes
    
    # Network performance
    connection_type = models.CharField(max_length=20, blank=True, null=True)
    network_speed = models.FloatField(null=True, blank=True)  # Mbps
    data_transferred = models.BigIntegerField(default=0)  # bytes
    
    # Feature usage
    features_used = models.JSONField(default=list)
    feature_usage_time = models.JSONField(default=dict)  # feature_name: seconds
    
    # Metadata
    app_version = models.CharField(max_length=50, blank=True, null=True)
    os_version = models.CharField(max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'mobile_usage_analytics'
        indexes = [
            models.Index(fields=['user', 'session_start']),
            models.Index(fields=['device', 'session_start']),
            models.Index(fields=['session_start']),
        ]

    def __str__(self):
        return f"Session {self.session_id} - {self.user.email}"


class PushNotification(models.Model):
    """Push notification management"""
    NOTIFICATION_TYPES = [
        ('lesson_reminder', 'Lesson Reminder'),
        ('assignment_due', 'Assignment Due'),
        ('course_update', 'Course Update'),
        ('achievement', 'Achievement'),
        ('message', 'Message'),
        ('system', 'System'),
        ('marketing', 'Marketing'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('opened', 'Opened'),
        ('clicked', 'Clicked'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Recipients
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_notifications')
    device = models.ForeignKey(MobileDevice, on_delete=models.CASCADE, related_name='push_notifications', null=True, blank=True)
    
    # Content
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    body = models.TextField()
    data = models.JSONField(default=dict)  # Additional payload data
    
    # Delivery
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='normal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Scheduling
    send_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Tracking
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    
    # Platform-specific
    platform = models.CharField(max_length=20, blank=True, null=True)  # ios, android
    message_id = models.CharField(max_length=255, blank=True, null=True)  # Platform message ID
    
    # Analytics
    delivery_attempts = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    
    # Metadata
    campaign = models.CharField(max_length=100, blank=True, null=True)
    metadata = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'push_notifications'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['notification_type', 'status']),
            models.Index(fields=['send_at']),
            models.Index(fields=['priority', 'status']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.email}"


class MobileAppConfig(models.Model):
    """Mobile app configuration and feature flags"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # App information
    app_name = models.CharField(max_length=255)
    app_version = models.CharField(max_length=50)
    build_number = models.CharField(max_length=50)
    
    # Platform
    platform = models.CharField(max_length=20, choices=[
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('all', 'All'),
    ])
    
    # Feature flags
    features = models.JSONField(default=dict)  # feature_name: enabled/disabled
    experimental_features = models.JSONField(default=dict)
    
    # Configuration
    api_base_url = models.URLField()
    cdn_base_url = models.URLField(blank=True, null=True)
    websocket_url = models.URLField(blank=True, null=True)
    
    # Security
    api_key_required = models.BooleanField(default=True)
    certificate_pinning = models.BooleanField(default=False)
    jailbreak_detection = models.BooleanField(default=True)
    
    # Performance
    max_cache_size = models.BigIntegerField(default=1073741824)  # 1GB
    max_concurrent_downloads = models.IntegerField(default=3)
    connection_timeout = models.IntegerField(default=30)  # seconds
    
    # UI/UX
    theme = models.JSONField(default=dict)
    branding = models.JSONField(default=dict)
    
    # Behavior
    auto_play_videos = models.BooleanField(default=False)
    preload_content = models.BooleanField(default=True)
    background_sync = models.BooleanField(default=True)
    
    # Limits
    max_offline_courses = models.IntegerField(default=10)
    max_offline_lessons_per_course = models.IntegerField(default=50)
    max_video_quality = models.CharField(max_length=20, default='1080p')
    
    # Status
    is_active = models.BooleanField(default=True)
    is_mandatory = models.BooleanField(default=False)
    
    # Deployment
    deployment_date = models.DateTimeField(null=True, blank=True)
    deprecation_date = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    release_notes = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='mobile_configs')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mobile_app_configs'
        unique_together = ['platform', 'app_version', 'build_number']

    def __str__(self):
        return f"{self.app_name} {self.app_version} ({self.platform})"


class MobileCrashReport(models.Model):
    """Mobile app crash reporting"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crash_reports', null=True, blank=True)
    device = models.ForeignKey(MobileDevice, on_delete=models.CASCADE, related_name='crash_reports')
    
    # Crash information
    crash_type = models.CharField(max_length=100)  # exception, ANR, etc.
    crash_message = models.TextField()
    stack_trace = models.TextField()
    
    # App state
    app_version = models.CharField(max_length=50)
    build_number = models.CharField(max_length=50)
    
    # Device state
    battery_level = models.IntegerField(null=True, blank=True)
    memory_available = models.BigIntegerField(null=True, blank=True)
    storage_available = models.BigIntegerField(null=True, blank=True)
    network_type = models.CharField(max_length=20, blank=True, null=True)
    
    # User context
    current_screen = models.CharField(max_length=255, blank=True, null=True)
    user_action = models.CharField(max_length=255, blank=True, null=True)
    
    # System information
    os_version = models.CharField(max_length=50)
    device_model = models.CharField(max_length=100, blank=True, null=True)
    
    # Reproduction
    reproduction_steps = models.TextField(blank=True, null=True)
    attachments = models.JSONField(default=list)  # logs, screenshots
    
    # Status
    status = models.CharField(max_length=20, default='new', choices=[
        ('new', 'New'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
        ('wont_fix', "Won't Fix"),
        ('duplicate', 'Duplicate'),
    ])
    
    # Assignment
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_crashes')
    
    # Resolution
    resolution_notes = models.TextField(blank=True, null=True)
    fixed_in_version = models.CharField(max_length=50, blank=True, null=True)
    
    occurred_at = models.DateTimeField()
    reported_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'mobile_crash_reports'
        ordering = ['-occurred_at']
        indexes = [
            models.Index(fields=['crash_type', 'status']),
            models.Index(fields=['app_version', 'status']),
            models.Index(fields=['occurred_at']),
        ]

    def __str__(self):
        return f"{self.crash_type} - {self.device.device_name}"
