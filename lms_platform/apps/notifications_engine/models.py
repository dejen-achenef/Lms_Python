from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import json

User = get_user_model()


class NotificationTemplate(models.Model):
    """Advanced notification templates"""
    TEMPLATE_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App'),
        ('webhook', 'Webhook'),
        ('slack', 'Slack'),
        ('teams', 'Microsoft Teams'),
        ('discord', 'Discord'),
    ]
    
    CATEGORIES = [
        ('academic', 'Academic'),
        ('administrative', 'Administrative'),
        ('marketing', 'Marketing'),
        ('system', 'System'),
        ('social', 'Social'),
        ('security', 'Security'),
        ('payment', 'Payment'),
        ('reminder', 'Reminder'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    category = models.CharField(max_length=30, choices=CATEGORIES)
    
    # Content
    subject_template = models.CharField(max_length=255, blank=True, null=True)
    body_template = models.TextField()
    html_template = models.TextField(blank=True, null=True)
    
    # Variables
    variables = models.JSONField(default=dict)  # Available template variables
    default_values = models.JSONField(default=dict)
    
    # Localization
    language = models.CharField(max_length=10, default='en')
    localized_versions = models.JSONField(default=dict)
    
    # Styling
    css_styles = models.TextField(blank=True, null=True)
    inline_styles = models.BooleanField(default=True)
    
    # Attachments
    default_attachments = models.JSONField(default=list)
    
    # Settings
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    
    # Approval
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_templates')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Version control
    version = models.IntegerField(default=1)
    parent_template = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_templates')
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_templates')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='notification_templates')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_templates'
        indexes = [
            models.Index(fields=['template_type', 'is_active']),
            models.Index(fields=['category']),
            models.Index(fields=['language']),
        ]

    def __str__(self):
        return f"Template: {self.name} ({self.template_type})"


class NotificationChannel(models.Model):
    """Notification channel configuration"""
    CHANNEL_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App'),
        ('webhook', 'Webhook'),
        ('slack', 'Slack'),
        ('teams', 'Microsoft Teams'),
        ('discord', 'Discord'),
        ('telegram', 'Telegram'),
        ('whatsapp', 'WhatsApp'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
        ('maintenance', 'Maintenance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    channel_type = models.CharField(max_length=20, choices=CHANNEL_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Configuration
    configuration = models.JSONField(default=dict)
    credentials = models.JSONField(default=dict)  # Encrypted
    
    # Limits and quotas
    rate_limit = models.IntegerField(null=True, blank=True)  # Messages per minute
    daily_limit = models.IntegerField(null=True, blank=True)  # Messages per day
    
    # Retry settings
    retry_attempts = models.IntegerField(default=3)
    retry_delay = models.IntegerField(default=60)  # seconds
    
    # Filtering
    allowed_users = models.ManyToManyField(User, related_name='allowed_channels', blank=True)
    blocked_users = models.ManyToManyField(User, related_name='blocked_channels', blank=True)
    
    # Scheduling
    business_hours_only = models.BooleanField(default=False)
    business_hours = models.JSONField(default=dict)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Monitoring
    health_status = models.CharField(max_length=20, default='unknown')
    last_health_check = models.DateTimeField(null=True, blank=True)
    
    # Analytics
    sent_count = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_channels')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='notification_channels')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_channels'
        indexes = [
            models.Index(fields=['channel_type', 'status']),
            models.Index(fields=['health_status']),
        ]

    def __str__(self):
        return f"Channel: {self.name} ({self.channel_type})"


class NotificationRule(models.Model):
    """Advanced notification rules and triggers"""
    TRIGGER_TYPES = [
        ('event', 'Event-based'),
        ('schedule', 'Scheduled'),
        ('condition', 'Condition-based'),
        ('api', 'API-triggered'),
        ('manual', 'Manual'),
    ]
    
    CONDITION_OPERATORS = [
        ('equals', 'Equals'),
        ('not_equals', 'Not Equals'),
        ('greater_than', 'Greater Than'),
        ('less_than', 'Less Than'),
        ('contains', 'Contains'),
        ('starts_with', 'Starts With'),
        ('ends_with', 'Ends With'),
        ('in', 'In'),
        ('not_in', 'Not In'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_TYPES)
    
    # Event configuration
    event_types = models.JSONField(default=list)
    event_filters = models.JSONField(default=dict)
    
    # Conditions
    conditions = models.JSONField(default=list)  # List of condition groups
    
    # Actions
    actions = models.JSONField(default=list)  # List of actions to execute
    
    # Channels
    channels = models.ManyToManyField(NotificationChannel, related_name='rules')
    
    # Templates
    templates = models.JSONField(default=dict)  # channel_type: template_id
    
    # Recipients
    recipient_rules = models.JSONField(default=dict)
    dynamic_recipients = models.JSONField(default=dict)
    
    # Scheduling
    schedule_config = models.JSONField(default=dict)
    
    # Priority and urgency
    priority = models.IntegerField(default=5)  # 1-10
    urgency = models.CharField(max_length=20, default='normal', choices=[
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
        ('critical', 'Critical'),
    ])
    
    # Rate limiting
    rate_limit = models.IntegerField(null=True, blank=True)  # Max notifications per time period
    rate_limit_period = models.IntegerField(default=3600)  # seconds
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Analytics
    trigger_count = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rules')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='notification_rules')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_rules'
        indexes = [
            models.Index(fields=['trigger_type', 'is_active']),
            models.Index(fields=['priority']),
            models.Index(fields=['urgency']),
        ]

    def __str__(self):
        return f"Rule: {self.name}"


class Notification(models.Model):
    """Individual notification messages"""
    STATUSES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    PRIORITIES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Recipients
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    additional_recipients = models.JSONField(default=list)
    
    # Content
    subject = models.CharField(max_length=255, blank=True, null=True)
    body = models.TextField()
    html_body = models.TextField(blank=True, null=True)
    
    # Channel and type
    channel = models.ForeignKey(NotificationChannel, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30)
    
    # Status and priority
    status = models.CharField(max_length=20, choices=STATUSES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITIES, default='normal')
    
    # Scheduling
    send_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Tracking
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # External IDs
    external_id = models.CharField(max_length=255, blank=True, null=True)
    provider_message_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Metadata
    metadata = models.JSONField(default=dict)
    template_data = models.JSONField(default=dict)
    
    # Attachments
    attachments = models.JSONField(default=list)
    
    # Error handling
    error_message = models.TextField(blank=True, null=True)
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    
    # Source
    source_rule = models.ForeignKey(NotificationRule, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    source_event = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['channel', 'status']),
            models.Index(fields=['priority', 'send_at']),
            models.Index(fields=['notification_type']),
        ]

    def __str__(self):
        return f"Notification for {self.recipient.email} - {self.status}"


class UserNotificationPreferences(models.Model):
    """User notification preferences"""
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push'),
        ('in_app', 'In-App'),
    ]
    
    FREQUENCY_CHOICES = [
        ('immediate', 'Immediate'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('never', 'Never'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Global preferences
    enable_notifications = models.BooleanField(default=True)
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Channel preferences
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    
    # Category preferences
    category_preferences = models.JSONField(default=dict)  # category: {channel: frequency}
    
    # Course-specific preferences
    course_preferences = models.JSONField(default=dict)  # course_id: {notifications_enabled: bool}
    
    # Frequency controls
    max_daily_emails = models.IntegerField(default=50)
    max_daily_push = models.IntegerField(default=100)
    max_daily_sms = models.IntegerField(default=10)
    
    # Content preferences
    email_format = models.CharField(max_length=20, default='html', choices=[
        ('html', 'HTML'),
        ('text', 'Text'),
        ('both', 'Both'),
    ])
    
    # Privacy
    allow_marketing = models.BooleanField(default=False)
    allow_analytics = models.BooleanField(default=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_notification_preferences'

    def __str__(self):
        return f"Preferences for {self.user.email}"


class NotificationAnalytics(models.Model):
    """Notification analytics and insights"""
    ANALYSIS_TYPES = [
        ('delivery', 'Delivery Analysis'),
        ('engagement', 'Engagement Analysis'),
        ('performance', 'Performance Analysis'),
        ('trends', 'Trend Analysis'),
        ('user_behavior', 'User Behavior Analysis'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis_type = models.CharField(max_length=30, choices=ANALYSIS_TYPES)
    
    # Time period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Delivery metrics
    total_sent = models.IntegerField(default=0)
    total_delivered = models.IntegerField(default=0)
    total_failed = models.IntegerField(default=0)
    delivery_rate = models.FloatField(default=0.0)
    
    # Engagement metrics
    total_opened = models.IntegerField(default=0)
    total_clicked = models.IntegerField(default=0)
    open_rate = models.FloatField(default=0.0)
    click_rate = models.FloatField(default=0.0)
    
    # Channel breakdown
    channel_metrics = models.JSONField(default=dict)
    
    # Type breakdown
    type_metrics = models.JSONField(default=dict)
    
    # Performance metrics
    average_send_time = models.FloatField(default=0.0)  # seconds
    average_delivery_time = models.FloatField(default=0.0)  # seconds
    
    # User behavior
    most_active_users = models.JSONField(default=list)
    least_active_users = models.JSONField(default=list)
    
    # Trends
    sending_trends = models.JSONField(default=list)
    engagement_trends = models.JSONField(default=list)
    
    # Recommendations
    recommendations = models.JSONField(default=list)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='notification_analytics')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notification_analytics'
        unique_together = ['analysis_type', 'period_start', 'period_end', 'tenant']
        ordering = ['-period_start']

    def __str__(self):
        return f"{self.analysis_type}: {self.period_start.date()} to {self.period_end.date()}"


class NotificationBatch(models.Model):
    """Batch notification processing"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Batch configuration
    total_recipients = models.IntegerField(default=0)
    processed_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    
    # Content
    subject = models.CharField(max_length=255, blank=True, null=True)
    body_template = models.TextField()
    template_data = models.JSONField(default=dict)
    
    # Channels
    channels = models.ManyToManyField(NotificationChannel, related_name='batches')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    estimated_completion = models.DateTimeField(null=True, blank=True)
    
    # Progress
    progress_percentage = models.FloatField(default=0.0)
    
    # Settings
    send_immediately = models.BooleanField(default=False)
    schedule_at = models.DateTimeField(null=True, blank=True)
    
    # Error handling
    error_threshold = models.FloatField(default=0.1)  # Stop if error rate exceeds 10%
    errors = models.JSONField(default=list)
    
    # Created by
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_batches')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='notification_batches')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_batches'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return f"Batch: {self.name} ({self.status})"


class NotificationDeliveryLog(models.Model):
    """Detailed delivery logging"""
    LOG_LEVELS = [
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='delivery_logs')
    
    # Log details
    log_level = models.CharField(max_length=20, choices=LOG_LEVELS)
    message = models.TextField()
    
    # HTTP details (if applicable)
    http_status_code = models.IntegerField(null=True, blank=True)
    http_response = models.TextField(blank=True, null=True)
    
    # Timing
    timestamp = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(null=True, blank=True)  # milliseconds
    
    # Context
    context = models.JSONField(default=dict)
    
    # Provider details
    provider_response = models.JSONField(default=dict)
    provider_message_id = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        db_table = 'notification_delivery_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['notification', 'timestamp']),
            models.Index(fields=['log_level']),
        ]

    def __str__(self):
        return f"{self.log_level.upper()}: {self.message[:50]}..."
