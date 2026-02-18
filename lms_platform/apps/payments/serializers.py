from rest_framework import serializers
from .models import Payment, Subscription, Invoice, DiscountCode


class PaymentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'user_name', 'course', 'course_title', 'amount',
            'currency', 'status', 'payment_method', 'stripe_payment_intent_id',
            'refund_amount', 'refund_reason', 'refunded_at', 'metadata',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'user', 'stripe_payment_intent_id', 'refund_amount',
            'refund_reason', 'refunded_at', 'created_at', 'updated_at', 'completed_at'
        ]


class PaymentCreateSerializer(serializers.ModelSerializer):
    stripe_token = serializers.CharField(write_only=True)
    discount_code = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Payment
        fields = ['course', 'amount', 'stripe_token', 'discount_code']
    
    def validate_course(self, value):
        if not value.is_free and value.price <= 0:
            raise serializers.ValidationError("Invalid course for payment.")
        return value


class SubscriptionSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'tenant', 'tenant_name', 'plan_type', 'status', 'amount',
            'currency', 'billing_cycle', 'starts_at', 'ends_at', 'cancelled_at',
            'stripe_subscription_id', 'current_users', 'current_courses',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'stripe_subscription_id', 'current_users', 'current_courses',
            'created_at', 'updated_at'
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    amount_paid = serializers.ReadOnlyField()
    balance_due = serializers.ReadOnlyField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'tenant', 'tenant_name', 'amount',
            'tax_amount', 'total_amount', 'currency', 'status',
            'issue_date', 'due_date', 'paid_at', 'amount_paid',
            'balance_due', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'amount_paid', 'balance_due',
            'created_at', 'updated_at'
        ]


class DiscountCodeSerializer(serializers.ModelSerializer):
    is_valid = serializers.ReadOnlyField()
    
    class Meta:
        model = DiscountCode
        fields = [
            'id', 'code', 'name', 'description', 'discount_type',
            'discount_value', 'max_uses', 'used_count', 'max_uses_per_user',
            'is_active', 'valid_from', 'valid_until', 'applicable_courses',
            'tenant', 'is_valid', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'used_count', 'created_at', 'updated_at'
        ]
