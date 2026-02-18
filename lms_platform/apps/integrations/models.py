from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import json
import hashlib

User = get_user_model()


class Webhook(models.Model):
    """Webhook configuration for event notifications"""
    EVENT_TYPES = [
        ('user.created', 'User Created'),
        ('user.updated', 'User Updated'),
        ('course.enrolled', 'Course Enrolled'),
        ('course.completed', 'Course Completed'),
        ('lesson.completed', 'Lesson Completed'),
        ('quiz.submitted', 'Quiz Submitted'),
        ('payment.completed', 'Payment Completed'),
        ('certificate.issued', 'Certificate Issued'),
        ('assignment.submitted', 'Assignment Submitted'),
        ('forum.post.created', 'Forum Post Created'),
        ('announcement.published', 'Announcement Published'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Configuration
    target_url = models.URLField()
    event_types = models.JSONField(default=list)  # List of events to subscribe to
    secret_key = models.CharField(max_length=255, blank=True, null=True)
    
    # Authentication
    auth_type = models.CharField(max_length=20, default='none', choices=[
        ('none', 'None'),
        ('api_key', 'API Key'),
        ('bearer_token', 'Bearer Token'),
        ('basic_auth', 'Basic Auth'),
        ('signature', 'Signature'),
    ])
    auth_credentials = models.JSONField(default=dict)
    
    # Headers
    custom_headers = models.JSONField(default=dict)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Retry settings
    retry_attempts = models.IntegerField(default=3)
    retry_delay = models.IntegerField(default=60)  # seconds
    
    # Filtering
    filters = models.JSONField(default=dict)  # Event filtering criteria
    
    # Rate limiting
    rate_limit = models.IntegerField(null=True, blank=True)  # Max requests per minute
    
    # Versioning
    api_version = models.CharField(max_length=10, default='v1')
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_webhooks')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='webhooks')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'webhooks'
        indexes = [
            models.Index(fields=['status', 'event_types']),
            models.Index(fields=['target_url']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return f"Webhook: {self.name}"


class WebhookDelivery(models.Model):
    """Webhook delivery tracking"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
    ]
    
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE, related_name='deliveries')
    
    # Event details
    event_type = models.CharField(max_length=50)
    event_id = models.UUIDField()
    payload = models.JSONField(default=dict)
    
    # Delivery details
    delivery_id = models.UUIDField(default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # HTTP details
    http_status_code = models.IntegerField(null=True, blank=True)
    response_headers = models.JSONField(default=dict)
    response_body = models.TextField(blank=True, null=True)
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Retry information
    attempt_count = models.IntegerField(default=1)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    
    # Error information
    error_message = models.TextField(blank=True, null=True)
    error_code = models.CharField(max_length=50, blank=True, null=True)
    
    # Duration
    duration = models.IntegerField(null=True, blank=True)  # milliseconds
    
    class Meta:
        db_table = 'webhook_deliveries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['webhook', 'status']),
            models.Index(fields=['event_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Delivery {self.delivery_id} - {self.event_type}"


class Integration(models.Model):
    """Third-party service integrations"""
    INTEGRATION_TYPES = [
        ('crm', 'CRM System'),
        ('hr', 'HR System'),
        ('sso', 'Single Sign-On'),
        ('payment', 'Payment Gateway'),
        ('email', 'Email Service'),
        ('sms', 'SMS Service'),
        ('storage', 'Cloud Storage'),
        ('analytics', 'Analytics Platform'),
        ('calendar', 'Calendar Service'),
        ('video', 'Video Platform'),
        ('document', 'Document Management'),
        ('project', 'Project Management'),
        ('communication', 'Communication Tool'),
        ('lms', 'External LMS'),
        ('api', 'Custom API'),
    ]
    
    STATUS_CHOICES = [
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('error', 'Error'),
        ('configuring', 'Configuring'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    integration_type = models.CharField(max_length=30, choices=INTEGRATION_TYPES)
    provider = models.CharField(max_length=100)  # Salesforce, Google, Microsoft, etc.
    
    # Configuration
    configuration = models.JSONField(default=dict)
    credentials = models.JSONField(default=dict)  # Encrypted
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disconnected')
    
    # Synchronization
    sync_enabled = models.BooleanField(default=False)
    sync_direction = models.CharField(max_length=20, default='bidirectional', choices=[
        ('import', 'Import Only'),
        ('export', 'Export Only'),
        ('bidirectional', 'Bidirectional'),
    ])
    sync_schedule = models.JSONField(default=dict)
    last_sync = models.DateTimeField(null=True, blank=True)
    
    # Data mapping
    field_mappings = models.JSONField(default=dict)
    transformation_rules = models.JSONField(default=list)
    
    # Features
    supported_features = models.JSONField(default=list)
    enabled_features = models.JSONField(default=list)
    
    # Limits and quotas
    api_quota = models.JSONField(default=dict)
    rate_limits = models.JSONField(default=dict)
    
    # Monitoring
    health_status = models.CharField(max_length=20, default='unknown')
    last_health_check = models.DateTimeField(null=True, blank=True)
    error_count = models.IntegerField(default=0)
    
    # Logs
    log_level = models.CharField(max_length=20, default='info')
    retention_days = models.IntegerField(default=30)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_integrations')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='integrations')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'integrations'
        indexes = [
            models.Index(fields=['integration_type', 'status']),
            models.Index(fields=['provider']),
            models.Index(fields ['sync_enabled', 'last_sync']),
        ]

    def __str__(self):
        return f"Integration: {self.name} ({self.provider})"


class IntegrationLog(models.Model):
    """Integration operation logs"""
    LOG_LEVELS = [
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    OPERATION_TYPES = [
        ('sync', 'Synchronization'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('query', 'Query'),
        ('webhook', 'Webhook'),
        ('auth', 'Authentication'),
    ]
    
    integration = models.ForeignKey(Integration, on_delete=models.CASCADE, related_name='logs')
    
    # Operation details
    operation_type = models.CharField(max_length=20, choices=OPERATION_TYPES)
    log_level = models.CharField(max_length=20, choices=LOG_LEVELS)
    
    # Message
    message = models.TextField()
    
    # Data
    request_data = models.JSONField(default=dict)
    response_data = models.JSONField(default=dict)
    
    # Context
    entity_type = models.CharField(max_length=50, blank=True, null=True)
    entity_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Timing
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)  # milliseconds
    
    # HTTP details (if applicable)
    http_method = models.CharField(max_length=10, blank=True, null=True)
    http_url = models.URLField(blank=True, null=True)
    http_status_code = models.IntegerField(null=True, blank=True)
    
    # Error details
    error_code = models.CharField(max_length=50, blank=True, null=True)
    error_details = models.JSONField(default=dict)
    
    # User context
    triggered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='integration_logs')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'integration_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['integration', 'log_level']),
            models.Index(fields=['operation_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.log_level.upper()}: {self.message[:50]}..."


class APIKey(models.Model):
    """API key management for external access"""
    KEY_TYPES = [
        ('read', 'Read Only'),
        ('write', 'Read/Write'),
        ('admin', 'Admin'),
        ('webhook', 'Webhook'),
        ('integration', 'Integration'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('revoked', 'Revoked'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    key_type = models.CharField(max_length=20, choices=KEY_TYPES)
    
    # Key details
    api_key = models.CharField(max_length=255, unique=True)
    key_hash = models.CharField(max_length=64)  # SHA-256 hash
    
    # Permissions
    permissions = models.JSONField(default=list)
    allowed_endpoints = models.JSONField(default=list)
    
    # Rate limiting
    rate_limit = models.IntegerField(null=True, blank=True)  # Requests per hour
    daily_limit = models.IntegerField(null=True, blank=True)  # Requests per day
    
    # IP restrictions
    allowed_ips = models.JSONField(default=list)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Expiration
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Usage tracking
    last_used = models.DateTimeField(null=True, blank=True)
    usage_count = models.IntegerField(default=0)
    
    # Owner
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    
    # Metadata
    description = models.TextField(blank=True, null=True)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='api_keys')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'api_keys'
        indexes = [
            models.Index(fields=['key_hash']),
            models.Index(fields=['status']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"API Key: {self.name}"


class APIUsage(models.Model):
    """API usage tracking"""
    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE, related_name='usage_logs')
    
    # Request details
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    
    # Response details
    status_code = models.IntegerField()
    response_size = models.IntegerField(null=True, blank=True)  # bytes
    
    # Timing
    requested_at = models.DateTimeField(auto_now_add=True)
    response_time = models.IntegerField(null=True, blank=True)  # milliseconds
    
    # User context
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='api_usage')
    
    # IP and location
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    
    # Error details
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'api_usage'
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['api_key', 'requested_at']),
            models.Index(fields=['endpoint']),
            models.Index(fields=['status_code']),
        ]

    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code}"


class DataMapping(models.Model):
    """Data field mapping between systems"""
    DIRECTION_TYPES = [
        ('import', 'Import'),
        ('export', 'Export'),
        ('bidirectional', 'Bidirectional'),
    ]
    
    FIELD_TYPES = [
        ('string', 'String'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('boolean', 'Boolean'),
        ('date', 'Date'),
        ('datetime', 'DateTime'),
        ('json', 'JSON'),
        ('array', 'Array'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    integration = models.ForeignKey(Integration, on_delete=models.CASCADE, related_name='data_mappings')
    
    # Source and target
    source_entity = models.CharField(max_length=100)
    target_entity = models.CharField(max_length=100)
    direction = models.CharField(max_length=20, choices=DIRECTION_TYPES)
    
    # Field mappings
    field_mappings = models.JSONField(default=dict)  # source_field: target_field
    
    # Field definitions
    source_fields = models.JSONField(default=dict)  # field_name: {type, required, default}
    target_fields = models.JSONField(default=dict)
    
    # Transformation rules
    transformations = models.JSONField(default=list)  # List of transformation rules
    validation_rules = models.JSONField(default=dict)
    
    # Sync settings
    sync_on_create = models.BooleanField(default=True)
    sync_on_update = models.BooleanField(default=True)
    sync_on_delete = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Statistics
    last_sync = models.DateTimeField(null=True, blank=True)
    records_synced = models.IntegerField(default=0)
    errors_count = models.IntegerField(default=0)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_mappings')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'data_mappings'
        unique_together = ['integration', 'source_entity', 'target_entity']

    def __str__(self):
        return f"Mapping: {self.source_entity} -> {self.target_entity}"


class ScheduledTask(models.Model):
    """Scheduled integration tasks"""
    TASK_TYPES = [
        ('sync', 'Data Synchronization'),
        ('cleanup', 'Data Cleanup'),
        ('report', 'Report Generation'),
        ('backup', 'Data Backup'),
        ('health_check', 'Health Check'),
        ('notification', 'Notification'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('paused', 'Paused'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    task_type = models.CharField(max_length=30, choices=TASK_TYPES)
    
    # Schedule
    cron_expression = models.CharField(max_length=100)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Configuration
    configuration = models.JSONField(default=dict)
    parameters = models.JSONField(default=dict)
    
    # Integration
    integration = models.ForeignKey(Integration, on_delete=models.CASCADE, related_name='scheduled_tasks', null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Execution history
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    run_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    
    # Notifications
    notify_on_success = models.BooleanField(default=False)
    notify_on_failure = models.BooleanField(default=True)
    notification_recipients = models.JSONField(default=list)
    
    # Timeout and retry
    timeout = models.IntegerField(default=3600)  # seconds
    max_retries = models.IntegerField(default=3)
    retry_delay = models.IntegerField(default=300)  # seconds
    
    # Dependencies
    dependencies = models.JSONField(default=list)  # Other tasks that must complete first
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduled_tasks')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='scheduled_tasks')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scheduled_tasks'
        indexes = [
            models.Index(fields=['status', 'next_run']),
            models.Index(fields=['task_type']),
            models.Index(fields=['integration']),
        ]

    def __str__(self):
        return f"Task: {self.name}"


class TaskExecution(models.Model):
    """Scheduled task execution history"""
    task = models.ForeignKey(ScheduledTask, on_delete=models.CASCADE, related_name='executions')
    
    # Execution details
    execution_id = models.UUIDField(default=uuid.uuid4, editable=False)
    
    # Status
    status = models.CharField(max_length=20, choices=ScheduledTask.STATUS_CHOICES, default='active')
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)  # seconds
    
    # Results
    result = models.JSONField(default=dict)
    output = models.TextField(blank=True, null=True)
    
    # Error handling
    error_message = models.TextField(blank=True, null=True)
    error_traceback = models.TextField(blank=True, null=True)
    retry_count = models.IntegerField(default=0)
    
    # Metrics
    records_processed = models.IntegerField(default=0)
    records_success = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    
    # Trigger context
    triggered_by = models.CharField(max_length=20, default='schedule')  # schedule, manual, api
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'task_executions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task', 'status']),
            models.Index(fields=['started_at']),
        ]

    def __str__(self):
        return f"Task Execution {self.execution_id} - {self.task.name}"


class IntegrationTemplate(models.Model):
    """Pre-configured integration templates"""
    CATEGORIES = [
        ('crm', 'CRM'),
        ('hr', 'HR'),
        ('marketing', 'Marketing'),
        ('communication', 'Communication'),
        ('productivity', 'Productivity'),
        ('analytics', 'Analytics'),
        ('payment', 'Payment'),
        ('storage', 'Storage'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORIES)
    provider = models.CharField(max_length=100)
    
    # Template configuration
    template_config = models.JSONField(default=dict)
    default_mappings = models.JSONField(default=dict)
    required_fields = models.JSONField(default=list)
    
    # Features
    supported_features = models.JSONField(default=list)
    
    # Documentation
    setup_guide = models.TextField(blank=True, null=True)
    api_documentation = models.URLField(blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Usage
    usage_count = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    
    # Version
    version = models.CharField(max_length=20, default='1.0.0')
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='integration_templates')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'integration_templates'
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['provider']),
            models.Index(fields=['is_featured']),
        ]

    def __str__(self):
        return f"Template: {self.name} ({self.provider})"
