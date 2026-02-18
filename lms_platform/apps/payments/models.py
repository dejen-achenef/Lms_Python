from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHODS = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='payments')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='payments')
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='stripe')
    
    # External payment IDs
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    paypal_payment_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Refund details
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    refund_reason = models.TextField(blank=True, null=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['course', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.course.title} (${self.amount})"

    @property
    def is_refunded(self):
        return self.status == 'refunded'

    @property
    def refund_available(self):
        return self.status == 'completed' and self.refund_amount < self.amount

    def process_refund(self, amount, reason=''):
        if amount > self.amount - self.refund_amount:
            raise ValueError("Refund amount exceeds available amount")
        
        self.refund_amount += amount
        self.refund_reason = reason
        self.refunded_at = timezone.now()
        
        if self.refund_amount >= self.amount:
            self.status = 'refunded'
        
        self.save()


class Subscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='subscriptions')
    
    # Subscription details
    plan_type = models.CharField(
        max_length=20,
        choices=[
            ('basic', 'Basic'),
            ('pro', 'Professional'),
            ('enterprise', 'Enterprise'),
        ]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Billing
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    billing_cycle = models.CharField(
        max_length=20,
        choices=[
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
        ]
    )
    
    # Dates
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # External IDs
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Usage tracking
    current_users = models.IntegerField(default=0)
    current_courses = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscriptions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.tenant.name} - {self.plan_type} ({self.status})"

    @property
    def is_active(self):
        return self.status == 'active' and self.ends_at > timezone.now()

    @property
    def days_until_expiry(self):
        if self.ends_at:
            return (self.ends_at - timezone.now()).days
        return 0

    def can_add_user(self):
        if self.plan_type == 'enterprise':
            return True
        return self.current_users < self.tenant.max_users

    def can_add_course(self):
        if self.plan_type == 'enterprise':
            return True
        return self.current_courses < self.tenant.max_courses


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=50, unique=True)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='invoices')
    
    # Invoice details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Dates
    issue_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Related payments
    payments = models.ManyToManyField(Payment, blank=True, related_name='invoices')
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'invoices'
        ordering = ['-issue_date']

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.tenant.name}"

    @property
    def is_overdue(self):
        return self.status in ['sent', 'overdue'] and timezone.now() > self.due_date

    @property
    def amount_paid(self):
        return self.payments.filter(status='completed').aggregate(
            total=models.Sum('amount')
        )['total'] or 0

    @property
    def balance_due(self):
        return self.total_amount - self.amount_paid

    def mark_paid(self):
        self.status = 'paid'
        self.paid_at = timezone.now()
        self.save()


class DiscountCode(models.Model):
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Discount details
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Usage limits
    max_uses = models.IntegerField(null=True, blank=True)
    used_count = models.IntegerField(default=0)
    max_uses_per_user = models.IntegerField(default=1)
    
    # Validity
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    
    # Applicability
    applicable_courses = models.ManyToManyField('courses.Course', blank=True, related_name='discount_codes')
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='discount_codes')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'discount_codes'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.discount_value}{'%' if self.discount_type == 'percentage' else '$'}"

    @property
    def is_valid(self):
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_until and
            (self.max_uses is None or self.used_count < self.max_uses)
        )

    def can_use(self, user):
        if not self.is_valid:
            return False
        
        # Check per-user limit
        user_uses = Payment.objects.filter(
            user=user,
            metadata__discount_code=self.code,
            status='completed'
        ).count()
        
        return user_uses < self.max_uses_per_user

    def apply_discount(self, amount):
        if self.discount_type == 'percentage':
            return amount * (self.discount_value / 100)
        else:
            return min(self.discount_value, amount)

    def record_usage(self):
        self.used_count += 1
        self.save()
