from django.db import models
from django.utils import timezone
import uuid


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('course_enrollment', 'Course Enrollment'),
        ('lesson_completed', 'Lesson Completed'),
        ('assignment_due', 'Assignment Due'),
        ('grade_posted', 'Grade Posted'),
        ('course_announcement', 'Course Announcement'),
        ('payment_received', 'Payment Received'),
        ('system_update', 'System Update'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='notifications')
    
    # Content
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='medium')
    
    # Related objects
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    assignment = models.ForeignKey('enrollments.Assignment', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    
    # Status
    is_read = models.BooleanField(default=False)
    is_email_sent = models.BooleanField(default=False)
    is_push_sent = models.BooleanField(default=False)
    
    # Metadata
    action_url = models.URLField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['priority']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.title}"

    def mark_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

    def mark_email_sent(self):
        if not self.is_email_sent:
            self.is_email_sent = True
            self.email_sent_at = timezone.now()
            self.save()


class NotificationTemplate(models.Model):
    NOTIFICATION_TYPES = [
        ('course_enrollment', 'Course Enrollment'),
        ('lesson_completed', 'Lesson Completed'),
        ('assignment_due', 'Assignment Due'),
        ('grade_posted', 'Grade Posted'),
        ('course_announcement', 'Course Announcement'),
        ('payment_received', 'Payment Received'),
        ('system_update', 'System Update'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='notification_templates')
    
    # Email template
    email_subject = models.CharField(max_length=255)
    email_body_html = models.TextField()
    email_body_text = models.TextField()
    
    # Push notification template
    push_title = models.CharField(max_length=255)
    push_message = models.TextField()
    
    # In-app notification template
    in_app_title = models.CharField(max_length=255)
    in_app_message = models.TextField()
    
    # Settings
    is_active = models.BooleanField(default=True)
    send_email = models.BooleanField(default=True)
    send_push = models.BooleanField(default=True)
    send_in_app = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_templates'
        unique_together = ['notification_type', 'tenant']
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.tenant.name}"


class NotificationPreference(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email preferences
    email_course_updates = models.BooleanField(default=True)
    email_assignment_reminders = models.BooleanField(default=True)
    email_grade_notifications = models.BooleanField(default=True)
    email_payment_receipts = models.BooleanField(default=True)
    email_system_updates = models.BooleanField(default=False)
    
    # Push notification preferences
    push_course_updates = models.BooleanField(default=True)
    push_assignment_reminders = models.BooleanField(default=True)
    push_grade_notifications = models.BooleanField(default=True)
    push_payment_receipts = models.BooleanField(default=True)
    push_system_updates = models.BooleanField(default=False)
    
    # In-app preferences
    in_app_course_updates = models.BooleanField(default=True)
    in_app_assignment_reminders = models.BooleanField(default=True)
    in_app_grade_notifications = models.BooleanField(default=True)
    in_app_payment_receipts = models.BooleanField(default=True)
    in_app_system_updates = models.BooleanField(default=True)
    
    # General settings
    digest_frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Immediate'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('never', 'Never'),
        ],
        default='immediate'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'

    def __str__(self):
        return f"{self.user.email} Preferences"


class Announcement(models.Model):
    ANNOUNCEMENT_TYPES = [
        ('system', 'System'),
        ('tenant', 'Tenant'),
        ('course', 'Course'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    announcement_type = models.CharField(max_length=20, choices=ANNOUNCEMENT_TYPES)
    
    # Target audience
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, null=True, blank=True, related_name='announcements')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, null=True, blank=True, related_name='announcements')
    target_roles = models.JSONField(default=list)  # ['admin', 'teacher', 'student']
    
    # Display settings
    is_active = models.BooleanField(default=True)
    is_pinned = models.BooleanField(default=False)
    show_popup = models.BooleanField(default=False)
    
    # Scheduling
    publish_at = models.DateTimeField(default=timezone.now)
    expire_at = models.DateTimeField(null=True, blank=True)
    
    # Author
    author = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='announcements')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'announcements'
        ordering = ['-publish_at']
        indexes = [
            models.Index(fields=['is_active', 'publish_at']),
            models.Index(fields=['announcement_type']),
            models.Index(fields=['is_pinned']),
        ]

    def __str__(self):
        return self.title

    @property
    def is_current(self):
        now = timezone.now()
        return (
            self.is_active and
            self.publish_at <= now and
            (self.expire_at is None or self.expire_at > now)
        )
