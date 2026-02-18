from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import json

User = get_user_model()


class ContentBlock(models.Model):
    """Reusable content blocks for CMS"""
    BLOCK_TYPES = [
        ('text', 'Text Block'),
        ('image', 'Image Block'),
        ('video', 'Video Block'),
        ('audio', 'Audio Block'),
        ('gallery', 'Gallery Block'),
        ('form', 'Form Block'),
        ('quiz', 'Quiz Block'),
        ('embed', 'Embed Block'),
        ('call_to_action', 'Call to Action'),
        ('testimonial', 'Testimonial'),
        ('pricing', 'Pricing Table'),
        ('feature_list', 'Feature List'),
        ('faq', 'FAQ Section'),
        ('stats', 'Statistics'),
        ('timeline', 'Timeline'),
        ('team', 'Team Members'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    block_type = models.CharField(max_length=30, choices=BLOCK_TYPES)
    
    # Content
    content = models.JSONField(default=dict)
    html_content = models.TextField(blank=True, null=True)
    css_classes = models.JSONField(default=list)
    custom_css = models.TextField(blank=True, null=True)
    
    # Media
    images = models.JSONField(default=list)
    videos = models.JSONField(default=list)
    documents = models.JSONField(default=list)
    
    # Settings
    is_template = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    # SEO
    seo_title = models.CharField(max_length=255, blank=True, null=True)
    seo_description = models.TextField(blank=True, null=True)
    seo_keywords = models.JSONField(default=list)
    
    # Analytics
    view_count = models.IntegerField(default=0)
    click_count = models.IntegerField(default=0)
    conversion_count = models.IntegerField(default=0)
    
    # Metadata
    tags = models.JSONField(default=list)
    category = models.CharField(max_length=100, blank=True, null=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_blocks')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_blocks', null=True, blank=True)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='content_blocks')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'content_blocks'
        indexes = [
            models.Index(fields=['block_type', 'is_active']),
            models.Index(fields=['is_template', 'is_public']),
            models.Index(fields=['category']),
            models.Index(fields=['tags']),
        ]

    def __str__(self):
        return f"{self.name} ({self.block_type})"


class Page(models.Model):
    """CMS pages with dynamic content"""
    PAGE_TYPES = [
        ('landing', 'Landing Page'),
        ('course', 'Course Page'),
        ('blog', 'Blog Post'),
        ('about', 'About Page'),
        ('contact', 'Contact Page'),
        ('help', 'Help Page'),
        ('faq', 'FAQ Page'),
        ('pricing', 'Pricing Page'),
        ('terms', 'Terms Page'),
        ('privacy', 'Privacy Policy'),
        ('custom', 'Custom Page'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('published', 'Published'),
        ('scheduled', 'Scheduled'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    page_type = models.CharField(max_length=30, choices=PAGE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Content
    content = models.JSONField(default=dict)  # Page structure with blocks
    html_content = models.TextField(blank=True, null=True)
    
    # Layout
    template = models.CharField(max_length=100, default='default')
    layout = models.JSONField(default=dict)
    
    # SEO
    seo_title = models.CharField(max_length=255, blank=True, null=True)
    seo_description = models.TextField(blank=True, null=True)
    seo_keywords = models.JSONField(default=list)
    og_image = models.URLField(blank=True, null=True)
    canonical_url = models.URLField(blank=True, null=True)
    
    # Settings
    is_homepage = models.BooleanField(default=False)
    show_in_navigation = models.BooleanField(default=True)
    require_login = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=False)
    
    # Publishing
    published_at = models.DateTimeField(null=True, blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    
    # Analytics
    view_count = models.IntegerField(default=0)
    unique_views = models.IntegerField(default=0)
    average_time_on_page = models.FloatField(default=0.0)
    bounce_rate = models.FloatField(default=0.0)
    
    # Social
    social_shares = models.IntegerField(default=0)
    facebook_shares = models.IntegerField(default=0)
    twitter_shares = models.IntegerField(default=0)
    linkedin_shares = models.IntegerField(default=0)
    
    # Metadata
    tags = models.JSONField(default=list)
    category = models.CharField(max_length=100, blank=True, null=True)
    featured_image = models.URLField(blank=True, null=True)
    
    # Version control
    current_version = models.IntegerField(default=1)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_pages')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_pages', null=True, blank=True)
    published_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='published_pages')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='pages')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_pages'
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['page_type', 'status']),
            models.Index(fields=['slug']),
            models.Index(fields['show_in_navigation']),
            models.Index(fields=['tags']),
        ]

    def __str__(self):
        return f"{self.title} ({self.status})"


class PageVersion(models.Model):
    """Version control for pages"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()
    
    # Content snapshot
    title = models.CharField(max_length=255)
    content = models.JSONField(default=dict)
    html_content = models.TextField(blank=True, null=True)
    layout = models.JSONField(default=dict)
    
    # Change information
    change_summary = models.TextField(blank=True, null=True)
    change_type = models.CharField(max_length=20, choices=[
        ('create', 'Create'),
        ('update', 'Update'),
        ('publish', 'Publish'),
        ('archive', 'Archive'),
    ], default='update')
    
    # Author
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='page_versions')
    
    # Diff information
    fields_changed = models.JSONField(default=list)
    additions = models.IntegerField(default=0)
    deletions = models.IntegerField(default=0)
    
    # Status
    is_current = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'page_versions'
        unique_together = ['page', 'version_number']
        ordering = ['-version_number']

    def __str__(self):
        return f"{self.page.title} v{self.version_number}"


class ContentWorkflow(models.Model):
    """Content approval workflow"""
    WORKFLOW_TYPES = [
        ('simple', 'Simple Approval'),
        ('multi_stage', 'Multi-stage Approval'),
        ('peer_review', 'Peer Review'),
        ('legal_review', 'Legal Review'),
        ('compliance', 'Compliance Review'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),
        ('in_review', 'In Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    workflow_type = models.CharField(max_length=30, choices=WORKFLOW_TYPES)
    
    # Configuration
    stages = models.JSONField(default=list)  # List of workflow stages
    approvers = models.JSONField(default=dict)  # Stage: [user_ids]
    conditions = models.JSONField(default=dict)  # Conditions for each stage
    
    # Settings
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    description = models.TextField(blank=True, null=True)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='content_workflows')
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_workflows')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'content_workflows'

    def __str__(self):
        return f"{self.name} ({self.workflow_type})"


class ContentWorkflowInstance(models.Model):
    """Instance of a workflow for specific content"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(ContentWorkflow, on_delete=models.CASCADE, related_name='instances')
    
    # Content reference
    content_type = models.CharField(max_length=50)  # page, course, lesson, etc.
    content_id = models.CharField(max_length=255)
    
    # Current state
    current_stage = models.IntegerField(default=0)
    status = models.CharField(max_length=30, choices=ContentWorkflow.STATUS_CHOICES, default='draft')
    
    # Initiator
    initiated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='initiated_workflows')
    
    # Timeline
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Comments and feedback
    comments = models.JSONField(default=list)
    feedback = models.JSONField(default=dict)
    
    # History
    stage_history = models.JSONField(default=list)
    
    class Meta:
        db_table = 'content_workflow_instances'
        unique_together = ['workflow', 'content_type', 'content_id']

    def __str__(self):
        return f"{self.workflow.name} - {self.content_type}:{self.content_id}"


class MediaLibrary(models.Model):
    """Centralized media library"""
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
        ('archive', 'Archive'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES)
    
    # File information
    file = models.FileField(upload_to='media/%Y/%m/')
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField(default=0)
    mime_type = models.CharField(max_length=100)
    file_hash = models.CharField(max_length=64)  # SHA-256
    
    # Image specific
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    format = models.CharField(max_length=20, blank=True, null=True)
    
    # Video specific
    duration = models.FloatField(null=True, blank=True)  # seconds
    bitrate = models.IntegerField(null=True, blank=True)
    codec = models.CharField(max_length=50, blank=True, null=True)
    
    # Document specific
    page_count = models.IntegerField(null=True, blank=True)
    
    # Metadata
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    caption = models.TextField(blank=True, null=True)
    
    # Organization
    tags = models.JSONField(default=list)
    category = models.CharField(max_length=100, blank=True, null=True)
    collection = models.CharField(max_length=100, blank=True, null=True)
    
    # Usage tracking
    usage_count = models.IntegerField(default=0)
    download_count = models.IntegerField(default=0)
    
    # Access control
    is_public = models.BooleanField(default=True)
    allowed_users = models.ManyToManyField(User, related_name='accessible_media', blank=True)
    
    # Processing
    processing_status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])
    
    # Thumbnails and previews
    thumbnail = models.ImageField(upload_to='media/thumbnails/', null=True, blank=True)
    preview = models.FileField(upload_to='media/previews/', null=True, blank=True)
    
    # CDN and optimization
    cdn_url = models.URLField(blank=True, null=True)
    optimized_versions = models.JSONField(default=dict)
    
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_media')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='media_library')
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'media_library'
        indexes = [
            models.Index(fields=['media_type', 'processing_status']),
            models.Index(fields=['category']),
            models.Index(fields=['tags']),
            models.Index(fields['file_hash']),
        ]

    def __str__(self):
        return f"{self.name} ({self.media_type})"


class Menu(models.Model):
    """Navigation menus"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=100)  # header, footer, sidebar, etc.
    
    # Structure
    items = models.JSONField(default=list)  # Hierarchical menu structure
    
    # Settings
    is_active = models.BooleanField(default=True)
    max_depth = models.IntegerField(default=3)
    
    # Styling
    css_class = models.CharField(max_length=100, blank=True, null=True)
    custom_css = models.TextField(blank=True, null=True)
    
    # Mobile
    mobile_layout = models.JSONField(default=dict)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='menus')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_menus'

    def __str__(self):
        return f"{self.name} ({self.location})"


class Form(models.Model):
    """Dynamic forms for CMS"""
    FORM_TYPES = [
        ('contact', 'Contact Form'),
        ('registration', 'Registration Form'),
        ('survey', 'Survey'),
        ('feedback', 'Feedback Form'),
        ('application', 'Application Form'),
        ('newsletter', 'Newsletter Signup'),
        ('support', 'Support Request'),
        ('custom', 'Custom Form'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    form_type = models.CharField(max_length=30, choices=FORM_TYPES)
    
    # Form structure
    fields = models.JSONField(default=dict)  # Form field definitions
    validation_rules = models.JSONField(default=dict)
    
    # Settings
    is_active = models.BooleanField(default=True)
    require_login = models.BooleanField(default=False)
    allow_multiple_submissions = models.BooleanField(default=True)
    
    # Confirmation
    success_message = models.TextField(blank=True, null=True)
    redirect_url = models.URLField(blank=True, null=True)
    send_email = models.BooleanField(default=True)
    email_recipients = models.JSONField(default=list)
    
    # Analytics
    submission_count = models.IntegerField(default=0)
    conversion_rate = models.FloatField(default=0.0)
    
    # Spam protection
    enable_captcha = models.BooleanField(default=False)
    honeypot_enabled = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_forms')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='forms')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_forms'

    def __str__(self):
        return f"{self.name} ({self.form_type})"


class FormSubmission(models.Model):
    """Form submissions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='submissions')
    
    # Submission data
    data = models.JSONField(default=dict)
    files = models.JSONField(default=list)
    
    # Metadata
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    
    # User
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='form_submissions')
    
    # Status
    status = models.CharField(max_length=20, default='new', choices=[
        ('new', 'New'),
        ('read', 'Read'),
        ('processed', 'Processed'),
        ('spam', 'Spam'),
    ])
    
    # Processing
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_submissions')
    processed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'form_submissions'
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Submission for {self.form.name}"


class Template(models.Model):
    """Page and component templates"""
    TEMPLATE_TYPES = [
        ('page', 'Page Template'),
        ('component', 'Component Template'),
        ('email', 'Email Template'),
        ('pdf', 'PDF Template'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    
    # Template content
    html_template = models.TextField()
    css_template = models.TextField(blank=True, null=True)
    js_template = models.TextField(blank=True, null=True)
    
    # Variables and logic
    variables = models.JSONField(default=dict)
    logic = models.JSONField(default=dict)
    
    # Settings
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Preview
    preview_image = models.ImageField(upload_to='template_previews/', null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_templates')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='templates')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_templates'

    def __str__(self):
        return f"{self.name} ({self.template_type})"


class SiteConfiguration(models.Model):
    """Global site configuration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic settings
    site_name = models.CharField(max_length=255)
    site_description = models.TextField()
    site_keywords = models.JSONField(default=list)
    
    # Branding
    logo = models.ImageField(upload_to='branding/', null=True, blank=True)
    favicon = models.ImageField(upload_to='branding/', null=True, blank=True)
    
    # Colors and theme
    primary_color = models.CharField(max_length=7, default='#007bff')
    secondary_color = models.CharField(max_length=7, default='#6c757d')
    accent_color = models.CharField(max_length=7, default='#28a745')
    
    # Typography
    font_family = models.CharField(max_length=100, default='Arial, sans-serif')
    font_size = models.CharField(max_length=20, default='16px')
    
    # Layout
    header_height = models.CharField(max_length=20, default='80px')
    footer_height = models.CharField(max_length=20, default='200px')
    
    # Social media
    social_links = models.JSONField(default=dict)
    
    # Contact information
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Analytics
    google_analytics_id = models.CharField(max_length=50, blank=True, null=True)
    facebook_pixel_id = models.CharField(max_length=50, blank=True, null=True)
    
    # SEO
    default_meta_description = models.TextField(blank=True, null=True)
    default_meta_keywords = models.JSONField(default=list)
    
    # Maintenance
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True, null=True)
    
    # Custom code
    custom_head_html = models.TextField(blank=True, null=True)
    custom_body_html = models.TextField(blank=True, null=True)
    custom_css = models.TextField(blank=True, null=True)
    custom_js = models.TextField(blank=True, null=True)
    
    tenant = models.OneToOneField('tenants.Tenant', on_delete=models.CASCADE, related_name='site_configuration')
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'site_configuration'

    def __str__(self):
        return f"Configuration for {self.site_name}"
