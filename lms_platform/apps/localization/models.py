from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import json

User = get_user_model()


class Language(models.Model):
    """Supported languages"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('beta', 'Beta'),
        ('deprecated', 'Deprecated'),
        ('disabled', 'Disabled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=10, unique=True)  # en, es, fr, etc.
    name = models.CharField(max_length=100)  # English, Spanish, French
    native_name = models.CharField(max_length=100)  # English, Español, Français
    
    # Locale information
    locale_code = models.CharField(max_length=20)  # en-US, es-ES, fr-FR
    rtl = models.BooleanField(default=False)  # Right-to-left
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Progress
    translation_progress = models.FloatField(default=0.0)  # Percentage translated
    
    # Settings
    is_default = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    
    # Regional settings
    date_format = models.CharField(max_length=50, default='MM/DD/YYYY')
    time_format = models.CharField(max_length=50, default='12-hour')
    number_format = models.JSONField(default=dict)
    currency_format = models.JSONField(default=dict)
    
    # Metadata
    flag_icon = models.CharField(max_length=10, blank=True, null=True)
    sort_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'languages'
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['is_default']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class TranslationKey(models.Model):
    """Translation keys and source strings"""
    KEY_TYPES = [
        ('ui', 'UI Text'),
        ('content', 'Content'),
        ('email', 'Email Template'),
        ('error', 'Error Message'),
        ('help', 'Help Text'),
        ('meta', 'Metadata'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('deprecated', 'Deprecated'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=255, unique=True)
    key_type = models.CharField(max_length=20, choices=KEY_TYPES, default='ui')
    
    # Source text
    source_text = models.TextField()
    source_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='source_keys')
    
    # Context
    context = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    # Location information
    file_path = models.CharField(max_length=500, blank=True, null=True)
    line_number = models.IntegerField(null=True, blank=True)
    component = models.CharField(max_length=100, blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Character limits
    max_length = models.IntegerField(null=True, blank=True)
    
    # Variables
    variables = models.JSONField(default=list)  # List of variables in the text
    
    # Tags
    tags = models.JSONField(default=list)
    
    # Usage tracking
    usage_count = models.IntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'translation_keys'
        indexes = [
            models.Index(fields=['key_type', 'status']),
            models.Index(fields=['source_language']),
            models.Index(fields=['component']),
            models.Index(fields=['tags']),
        ]

    def __str__(self):
        return f"{self.key}: {self.source_text[:50]}..."


class Translation(models.Model):
    """Translated strings"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('rejected', 'Rejected'),
    ]
    
    QUALITY_LEVELS = [
        ('machine', 'Machine Translation'),
        ('professional', 'Professional'),
        ('expert', 'Expert'),
        ('native', 'Native Speaker'),
    ]
    
    translation_key = models.ForeignKey(TranslationKey, on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='translations')
    
    # Translation
    translated_text = models.TextField()
    
    # Status and quality
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    quality_level = models.CharField(max_length=20, choices=QUALITY_LEVELS, default='machine')
    
    # Translation metadata
    word_count = models.IntegerField(default=0)
    character_count = models.IntegerField(default=0)
    
    # Translation source
    translation_method = models.CharField(max_length=50, default='manual')  # manual, machine, ai, etc.
    translator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='translations')
    
    # Review process
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_translations')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True, null=True)
    
    # Version control
    version = models.IntegerField(default=1)
    parent_translation = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_translations')
    
    # Alternatives
    alternatives = models.JSONField(default=list)  # Alternative translations
    
    # Notes and context
    translator_notes = models.TextField(blank=True, null=True)
    cultural_notes = models.TextField(blank=True, null=True)
    
    # Validation
    length_valid = models.BooleanField(default=True)
    grammar_valid = models.BooleanField(default=True)
    validation_errors = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'translations'
        unique_together = ['translation_key', 'language']
        indexes = [
            models.Index(fields=['language', 'status']),
            models.Index(fields ['translator']),
            models.Index(fields ['quality_level']),
        ]

    def __str__(self):
        return f"{self.translation_key.key} -> {self.language.name}"


class LocalizationProject(models.Model):
    """Localization projects and workflows"""
    PROJECT_TYPES = [
        ('website', 'Website'),
        ('mobile_app', 'Mobile App'),
        ('course', 'Course'),
        ('documentation', 'Documentation'),
        ('marketing', 'Marketing'),
        ('product', 'Product'),
    ]
    
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('in_progress', 'In Progress'),
        ('review', 'Under Review'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    project_type = models.CharField(max_length=30, choices=PROJECT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    
    # Source and target languages
    source_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='source_projects')
    target_languages = models.ManyToManyField(Language, related_name='target_projects')
    
    # Content scope
    translation_keys = models.ManyToManyField(TranslationKey, related_name='projects')
    
    # Timeline
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Progress
    overall_progress = models.FloatField(default=0.0)
    language_progress = models.JSONField(default=dict)
    
    # Team
    project_manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_projects')
    translators = models.ManyToManyField(User, related_name='translation_projects', blank=True)
    reviewers = models.ManyToManyField(User, related_name='review_projects', blank=True)
    
    # Budget and resources
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    
    # Quality requirements
    quality_level = models.CharField(max_length=20, choices=Translation.QUALITY_LEVELS)
    style_guide = models.TextField(blank=True, null=True)
    glossary = models.JSONField(default=dict)
    
    # Settings
    machine_translation_allowed = models.BooleanField(default=False)
    crowdsourced = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'localization_projects'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields ['project_type']),
            models.Index(fields ['start_date']),
        ]

    def __str__(self):
        return f"Project: {self.name}"


class TranslationMemory(models.Model):
    """Translation memory for reuse"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Source text
    source_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='tm_source')
    source_text = models.TextField()
    
    # Translation
    target_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='tm_target')
    target_text = models.TextField()
    
    # Context
    domain = models.CharField(max_length=100, blank=True, null=True)
    context = models.TextField(blank=True, null=True)
    
    # Quality metrics
    quality_score = models.FloatField(default=0.0)
    usage_count = models.IntegerField(default=0)
    
    # Validation
    validated = models.BooleanField(default=False)
    validated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='validated_tm')
    validated_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tm')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'translation_memory'
        indexes = [
            models.Index(fields=['source_language', 'target_language']),
            models.Index(fields=['domain']),
            models.Index(fields ['quality_score']),
        ]

    def __str__(self):
        return f"TM: {self.source_text[:30]}... -> {self.target_text[:30]}..."


class Glossary(models.Model):
    """Glossary terms and definitions"""
    TERM_TYPES = [
        ('technical', 'Technical'),
        ('business', 'Business'),
        ('marketing', 'Marketing'),
        ('legal', 'Legal'),
        ('brand', 'Brand'),
        ('product', 'Product'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    term = models.CharField(max_length=255)
    term_type = models.CharField(max_length=20, choices=TERM_TYPES)
    
    # Definition and context
    definition = models.TextField()
    context = models.TextField(blank=True, null=True)
    
    # Translations
    translations = models.JSONField(default=dict)  # language_code: translated_term
    
    # Usage notes
    usage_notes = models.TextField(blank=True, null=True)
    grammar_notes = models.TextField(blank=True, null=True)
    
    # Status
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_glossary_terms')
    
    # Project association
    projects = models.ManyToManyField(LocalizationProject, related_name='glossary_terms', blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='glossary_terms')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='glossary')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'glossary'
        unique_together = ['term', 'tenant']
        indexes = [
            models.Index(fields=['term_type']),
            models.Index(fields ['is_approved']),
        ]

    def __str__(self):
        return f"Glossary: {self.term}"


class LocaleSettings(models.Model):
    """Locale-specific settings and configurations"""
    language = models.OneToOneField(Language, on_delete=models.CASCADE, related_name='locale_settings')
    
    # Date and time
    date_formats = models.JSONField(default=dict)
    time_formats = models.JSONField(default=dict)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Number formatting
    decimal_separator = models.CharField(max_length=5, default='.')
    thousands_separator = models.CharField(max_length=5, default=',')
    
    # Currency
    currency_code = models.CharField(max_length=3, blank=True, null=True)
    currency_symbol = models.CharField(max_length=10, blank=True, null=True)
    currency_format = models.CharField(max_length=50, blank=True, null=True)
    
    # Address formatting
    address_format = models.TextField(blank=True, null=True)
    
    # Cultural preferences
    week_starts_on = models.IntegerField(default=0)  # 0 = Sunday, 1 = Monday
    weekend_days = models.JSONField(default=list)  # [0, 6] for Sunday, Saturday
    
    # Legal and compliance
    privacy_policy_required = models.BooleanField(default=False)
    cookie_consent_required = models.BooleanField(default=False)
    age_restriction = models.IntegerField(null=True, blank=True)
    
    # Content preferences
    content_rating_system = models.CharField(max_length=50, blank=True, null=True)
    
    # SEO settings
    hreflang = models.CharField(max_length=10, blank=True, null=True)
    canonical_url_pattern = models.CharField(max_length=255, blank=True, null=True)
    
    # Custom settings
    custom_settings = models.JSONField(default=dict)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'locale_settings'

    def __str__(self):
        return f"Locale Settings: {self.language.name}"


class UserLanguagePreference(models.Model):
    """User language preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='language_preference')
    
    # Primary language
    primary_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='primary_users')
    
    # Secondary languages (order of preference)
    secondary_languages = models.ManyToManyField(Language, related_name='secondary_users', blank=True)
    
    # Auto-translation settings
    auto_translate = models.BooleanField(default=True)
    show_original = models.BooleanField(default=False)
    
    # Content language preferences
    course_language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True, related_name='course_users')
    ui_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='ui_users')
    
    # Regional settings
    timezone = models.CharField(max_length=50, default='UTC')
    date_format = models.CharField(max_length=50, blank=True, null=True)
    time_format = models.CharField(max_length=50, blank=True, null=True)
    
    # Accessibility
    high_contrast = models.BooleanField(default=False)
    large_text = models.BooleanField(default=False)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_language_preferences'

    def __str__(self):
        return f"Language Preference: {self.user.email}"


class LocalizationAnalytics(models.Model):
    """Localization analytics and insights"""
    ANALYSIS_TYPES = [
        ('usage', 'Usage Analysis'),
        ('quality', 'Quality Analysis'),
        ('progress', 'Progress Analysis'),
        ('cost', 'Cost Analysis'),
        ('engagement', 'Engagement Analysis'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis_type = models.CharField(max_length=30, choices=ANALYSIS_TYPES)
    
    # Time period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Language breakdown
    language_metrics = models.JSONField(default=dict)
    
    # Usage metrics
    total_translations = models.IntegerField(default=0)
    translations_by_type = models.JSONField(default=dict)
    
    # Quality metrics
    average_quality_score = models.FloatField(default=0.0)
    error_rate = models.FloatField(default=0.0)
    
    # Progress metrics
    completion_rates = models.JSONField(default=dict)
    
    # Cost metrics
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    cost_per_word = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    # User engagement
    language_switches = models.IntegerField(default=0)
    most_popular_languages = models.JSONField(default=list)
    
    # Recommendations
    recommendations = models.JSONField(default=list)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='localization_analytics')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'localization_analytics'
        unique_together = ['analysis_type', 'period_start', 'period_end', 'tenant']
        ordering = ['-period_start']

    def __str__(self):
        return f"{self.analysis_type}: {self.period_start.date()} to {self.period_end.date()}"
