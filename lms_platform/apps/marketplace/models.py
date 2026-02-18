from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import json

User = get_user_model()


class InstructorProfile(models.Model):
    """Instructor profiles for marketplace"""
    VERIFICATION_STATUS = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]
    
    EXPERTISE_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
        ('master', 'Master'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor_profile')
    
    # Professional information
    bio = models.TextField()
    headline = models.CharField(max_length=255)
    expertise_areas = models.JSONField(default=list)
    experience_years = models.IntegerField(default=0)
    expertise_level = models.CharField(max_length=20, choices=EXPERTISE_LEVELS, default='intermediate')
    
    # Verification
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    verification_documents = models.JSONField(default=list)
    verified_credentials = models.JSONField(default=list)
    
    # Social proof
    linkedin_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    
    # Media
    profile_image = models.ImageField(upload_to='instructor_profiles/', null=True, blank=True)
    intro_video = models.FileField(upload_to='instructor_videos/', null=True, blank=True)
    
    # Statistics
    total_students = models.IntegerField(default=0)
    total_courses = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    average_rating = models.FloatField(default=0.0)
    review_count = models.IntegerField(default=0)
    
    # Availability
    available_for_consulting = models.BooleanField(default=False)
    consultation_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    response_time = models.IntegerField(default=24)  # hours
    
    # Preferences
    teaching_languages = models.JSONField(default=['en'])
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Banking
    payout_method = models.JSONField(default=dict)
    tax_information = models.JSONField(default=dict)
    
    # Featured
    is_featured = models.BooleanField(default=False)
    featured_until = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'instructor_profiles'
        indexes = [
            models.Index(fields=['verification_status']),
            models.Index(fields=['expertise_level']),
            models.Index(fields=['average_rating']),
            models.Index(fields=['is_featured']),
        ]

    def __str__(self):
        return f"Instructor: {self.user.full_name}"


class CourseMarketplace(models.Model):
    """Marketplace listing for courses"""
    LISTING_TYPES = [
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('featured', 'Featured'),
        ('trending', 'Trending'),
        ('new', 'New'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
        ('archived', 'Archived'),
    ]
    
    course = models.OneToOneField('courses.Course', on_delete=models.CASCADE, related_name='marketplace_listing')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marketplace_courses')
    
    # Listing details
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPES, default='standard')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Marketplace pricing
    marketplace_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    promotional_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Commission
    commission_rate = models.FloatField(default=0.15)  # 15% marketplace commission
    instructor_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Marketing
    marketing_description = models.TextField()
    target_audience = models.JSONField(default=list)
    learning_outcomes = models.JSONField(default=list)
    prerequisites = models.JSONField(default=list)
    
    # Media
    promotional_video = models.URLField(blank=True, null=True)
    gallery_images = models.JSONField(default=list)
    
    # SEO and discovery
    seo_title = models.CharField(max_length=255, blank=True, null=True)
    seo_description = models.TextField(blank=True, null=True)
    tags = models.JSONField(default=list)
    category_tags = models.JSONField(default=list)
    
    # Analytics
    views = models.IntegerField(default=0)
    unique_views = models.IntegerField(default=0)
    wishlist_adds = models.IntegerField(default=0)
    cart_adds = models.IntegerField(default=0)
    conversion_rate = models.FloatField(default=0.0)
    
    # Reviews and ratings
    marketplace_rating = models.FloatField(default=0.0)
    marketplace_reviews = models.IntegerField(default=0)
    
    # Featured placement
    is_featured = models.BooleanField(default=False)
    featured_start = models.DateTimeField(null=True, blank=True)
    featured_end = models.DateTimeField(null=True, blank=True)
    
    # Approval workflow
    submitted_for_review = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_courses')
    review_notes = models.TextField(blank=True, null=True)
    
    published_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_marketplace'
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['listing_type', 'is_featured']),
            models.Index(fields=['instructor', 'status']),
            models.Index(fields=['marketplace_rating']),
            models.Index(fields=['views']),
        ]

    def __str__(self):
        return f"Marketplace: {self.course.title}"


class StudentReview(models.Model):
    """Student reviews for courses and instructors"""
    RATING_CHOICES = [(i, i) for i in range(1, 6)]  # 1-5 stars
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='student_reviews', null=True, blank=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='instructor_reviews', null=True, blank=True)
    
    # Rating
    overall_rating = models.IntegerField(choices=RATING_CHOICES)
    content_quality = models.IntegerField(choices=RATING_CHOICES)
    instructor_effectiveness = models.IntegerField(choices=RATING_CHOICES)
    value_for_money = models.IntegerField(choices=RATING_CHOICES)
    
    # Review content
    title = models.CharField(max_length=255)
    review_text = models.TextField()
    
    # Pros and cons
    pros = models.JSONField(default=list)
    cons = models.JSONField(default=list)
    
    # Verification
    verified_purchase = models.BooleanField(default=False)
    completed_course = models.BooleanField(default=False)
    
    # Helpful votes
    helpful_votes = models.IntegerField(default=0)
    total_votes = models.IntegerField(default=0)
    
    # Response
    instructor_response = models.TextField(blank=True, null=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    # Moderation
    is_visible = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    moderated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_reviews')
    moderation_reason = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_reviews'
        unique_together = ['student', 'course']
        indexes = [
            models.Index(fields=['course', 'overall_rating']),
            models.Index(fields=['instructor', 'overall_rating']),
            models.Index(fields=['verified_purchase']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Review by {self.student.email}"


class MarketplaceTransaction(models.Model):
    """Financial transactions in marketplace"""
    TRANSACTION_TYPES = [
        ('course_purchase', 'Course Purchase'),
        ('instructor_payout', 'Instructor Payout'),
        ('refund', 'Refund'),
        ('commission', 'Commission'),
        ('bonus', 'Bonus'),
        ('penalty', 'Penalty'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Amounts
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Currency
    currency = models.CharField(max_length=3, default='USD')
    exchange_rate = models.FloatField(default=1.0)
    
    # Related entities
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchase_transactions', null=True, blank=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earning_transactions', null=True, blank=True)
    
    # Payment details
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    payment_reference = models.CharField(max_length=255, blank=True, null=True)
    gateway_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Refund information
    refund_reason = models.TextField(blank=True, null=True)
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    
    # Processing
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_transactions')
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'marketplace_transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_type', 'status']),
            models.Index(fields=['student', 'created_at']),
            models.Index(fields=['instructor', 'created_at']),
            models.Index(fields=['course', 'created_at']),
        ]

    def __str__(self):
        return f"{self.transaction_type}: {self.gross_amount} {self.currency}"


class Wishlist(models.Model):
    """Student wishlist for courses"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='wishlist_items')
    
    # Metadata
    added_at = models.DateTimeField(auto_now_add=True)
    price_when_added = models.DecimalField(max_digits=10, decimal_places=2)
    discount_when_added = models.IntegerField(default=0)
    
    # Notifications
    price_drop_notification = models.BooleanField(default=True)
    enrollment_open_notification = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'wishlists'
        unique_together = ['student', 'course']
        indexes = [
            models.Index(fields=['student', 'added_at']),
            models.Index(fields=['course']),
        ]

    def __str__(self):
        return f"{self.student.email} - {self.course.title}"


class Bundle(models.Model):
    """Course bundles for package deals"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Courses in bundle
    courses = models.ManyToManyField('courses.Course', related_name='bundles')
    
    # Pricing
    individual_price_total = models.DecimalField(max_digits=12, decimal_places=2)
    bundle_price = models.DecimalField(max_digits=12, decimal_places=2)
    savings_percentage = models.FloatField(default=0.0)
    
    # Settings
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    max_purchases = models.IntegerField(null=True, blank=True)
    
    # Time limits
    available_from = models.DateTimeField(null=True, blank=True)
    available_until = models.DateTimeField(null=True, blank=True)
    
    # Analytics
    purchase_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    
    # Media
    bundle_image = models.ImageField(upload_to='bundle_images/', null=True, blank=True)
    promotional_video = models.URLField(blank=True, null=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_bundles')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='bundles')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_bundles'
        ordering = ['-created_at']

    def __str__(self):
        return f"Bundle: {self.title}"


class Coupon(models.Model):
    """Discount coupons and promotional codes"""
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
        ('buy_x_get_y', 'Buy X Get Y'),
        ('free_shipping', 'Free Shipping'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Discount details
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Applicability
    applicable_courses = models.ManyToManyField('courses.Course', related_name='coupons', blank=True)
    applicable_instructors = models.ManyToManyField(User, related_name='instructor_coupons', blank=True)
    applicable_bundles = models.ManyToManyField(Bundle, related_name='coupons', blank=True)
    
    # Usage limits
    max_uses = models.IntegerField(null=True, blank=True)
    max_uses_per_user = models.IntegerField(default=1)
    used_count = models.IntegerField(default=0)
    
    # Minimum requirements
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    minimum_courses = models.IntegerField(null=True, blank=True)
    
    # Time limits
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    
    # User restrictions
    restricted_users = models.ManyToManyField(User, related_name='restricted_coupons', blank=True)
    allowed_user_groups = models.JSONField(default=list)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    
    # Analytics
    total_discount_given = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    conversion_rate = models.FloatField(default=0.0)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_coupons')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='coupons')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'coupons'
        indexes = [
            models.Index(fields=['code', 'is_active']),
            models.Index(fields=['valid_from', 'valid_until']),
            models.Index(fields=['discount_type']),
        ]

    def __str__(self):
        return f"Coupon: {self.code}"


class Affiliate(models.Model):
    """Affiliate marketing program"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('suspended', 'Suspended'),
        ('terminated', 'Terminated'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='affiliate_profile')
    
    # Affiliate details
    affiliate_code = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Commission structure
    commission_rate = models.FloatField(default=0.10)  # 10% default
    tier_levels = models.JSONField(default=dict)
    
    # Payout information
    payout_method = models.JSONField(default=dict)
    minimum_payout = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    
    # Tracking
    tracking_pixel = models.URLField(blank=True, null=True)
    custom_landing_page = models.URLField(blank=True, null=True)
    
    # Analytics
    total_clicks = models.IntegerField(default=0)
    total_conversions = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Approval
    applied_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_affiliates')
    
    class Meta:
        db_table = 'affiliates'
        indexes = [
            models.Index(fields=['affiliate_code']),
            models.Index(fields=['status']),
            models.Index(fields=['total_earnings']),
        ]

    def __str__(self):
        return f"Affiliate: {self.user.email}"


class AffiliateClick(models.Model):
    """Affiliate click tracking"""
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE, related_name='clicks')
    
    # Click details
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    referrer = models.URLField(blank=True, null=True)
    
    # Landing page
    landing_page = models.URLField()
    
    # Conversion
    converted = models.BooleanField(default=False)
    conversion_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    commission_earned = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Timing
    clicked_at = models.DateTimeField(auto_now_add=True)
    converted_at = models.DateTimeField(null=True, blank=True)
    
    # User (if logged in)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='affiliate_clicks')
    
    class Meta:
        db_table = 'affiliate_clicks'
        indexes = [
            models.Index(fields=['affiliate', 'clicked_at']),
            models.Index(fields=['converted', 'converted_at']),
            models.Index(fields=['ip_address']),
        ]

    def __str__(self):
        return f"Click by {self.affiliate.user.email}"


class MarketplaceAnalytics(models.Model):
    """Marketplace analytics and insights"""
    ANALYSIS_TYPES = [
        ('daily', 'Daily Summary'),
        ('weekly', 'Weekly Summary'),
        ('monthly', 'Monthly Summary'),
        ('instructor', 'Instructor Performance'),
        ('course', 'Course Performance'),
        ('trending', 'Trending Analysis'),
        ('revenue', 'Revenue Analysis'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis_type = models.CharField(max_length=30, choices=ANALYSIS_TYPES)
    
    # Time period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Course metrics
    total_courses = models.IntegerField(default=0)
    new_courses = models.IntegerField(default=0)
    active_courses = models.IntegerField(default=0)
    
    # Student metrics
    total_students = models.IntegerField(default=0)
    new_students = models.IntegerField(default=0)
    active_students = models.IntegerField(default=0)
    
    # Revenue metrics
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    instructor_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    marketplace_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Engagement metrics
    total_views = models.IntegerField(default=0)
    total_reviews = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    
    # Conversion metrics
    conversion_rate = models.FloatField(default=0.0)
    cart_abandonment_rate = models.FloatField(default=0.0)
    
    # Top performers
    top_courses = models.JSONField(default=list)
    top_instructors = models.JSONField(default=list)
    trending_courses = models.JSONField(default=list)
    
    # Geographic data
    geographic_distribution = models.JSONField(default=dict)
    
    # Raw data
    raw_data = models.JSONField(default=dict)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='marketplace_analytics')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'marketplace_analytics'
        unique_together = ['analysis_type', 'period_start', 'period_end', 'tenant']
        ordering = ['-period_start']

    def __str__(self):
        return f"{self.analysis_type}: {self.period_start.date()} to {self.period_end.date()}"
