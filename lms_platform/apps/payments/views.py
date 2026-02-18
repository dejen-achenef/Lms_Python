from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.conf import settings
from django.utils import timezone
import stripe

from .models import Payment, Subscription, Invoice, DiscountCode
from .serializers import (
    PaymentSerializer, PaymentCreateSerializer,
    SubscriptionSerializer, InvoiceSerializer, DiscountCodeSerializer
)
from common.permissions import IsTenantAdmin

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'payment_method', 'course']
    search_fields = ['user__email', 'course__title']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Payment.objects.all()
        elif hasattr(user, 'tenant'):
            if user.role in ['admin', 'teacher']:
                return Payment.objects.filter(course__tenant=user.tenant)
            else:
                return Payment.objects.filter(user=user)
        return Payment.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        course = serializer.validated_data['course']
        stripe_token = serializer.validated_data['stripe_token']
        discount_code = serializer.validated_data.get('discount_code')
        
        # Calculate final amount
        amount = course.price
        if discount_code:
            try:
                discount = DiscountCode.objects.get(code=discount_code, tenant=request.user.tenant)
                if discount.can_use(request.user):
                    discount_amount = discount.apply_discount(amount)
                    amount -= discount_amount
                    discount.record_usage()
                else:
                    return Response(
                        {'error': 'Invalid or expired discount code'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except DiscountCode.DoesNotExist:
                return Response(
                    {'error': 'Invalid discount code'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if amount <= 0:
            return Response(
                {'error': 'Invalid payment amount'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create Stripe charge
            charge = stripe.Charge.create(
                amount=int(amount * 100),  # Convert to cents
                currency='usd',
                description=f'Payment for course: {course.title}',
                source=stripe_token,
                metadata={
                    'user_id': str(request.user.id),
                    'course_id': str(course.id),
                    'tenant_id': str(request.user.tenant.id) if request.user.tenant else None
                }
            )
            
            # Create payment record
            payment = Payment.objects.create(
                user=request.user,
                course=course,
                amount=amount,
                currency='usd',
                status='completed',
                payment_method='stripe',
                stripe_payment_intent_id=charge.id,
                metadata={
                    'stripe_charge_id': charge.id,
                    'discount_code': discount_code if discount_code else None
                },
                completed_at=timezone.now()
            )
            
            # Create enrollment if not exists
            from apps.enrollments.models import Enrollment
            enrollment, created = Enrollment.objects.get_or_create(
                student=request.user,
                course=course,
                defaults={
                    'is_paid': True,
                    'payment_amount': amount
                }
            )
            
            if not created:
                enrollment.is_paid = True
                enrollment.payment_amount = amount
                enrollment.save()
            
            # Send notification
            from apps.notifications.tasks import send_course_enrollment_notification
            send_course_enrollment_notification.delay(str(enrollment.id))
            
            return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
            
        except stripe.error.StripeError as e:
            return Response(
                {'error': f'Payment failed: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        payment = self.get_object()
        
        if payment.status != 'completed':
            return Response(
                {'error': 'Payment cannot be refunded'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        refund_amount = request.data.get('amount', payment.amount)
        refund_reason = request.data.get('reason', 'Customer request')
        
        try:
            # Create Stripe refund
            refund = stripe.Refund.create(
                charge=payment.stripe_payment_intent_id,
                amount=int(refund_amount * 100),  # Convert to cents
                reason='requested_by_customer',
                metadata={'reason': refund_reason}
            )
            
            # Update payment record
            payment.process_refund(refund_amount, refund_reason)
            
            return Response({
                'message': 'Refund processed successfully',
                'refund_amount': refund_amount,
                'refund_id': refund.id
            })
            
        except stripe.error.StripeError as e:
            return Response(
                {'error': f'Refund failed: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, IsTenantAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'plan_type', 'billing_cycle']
    search_fields = ['tenant__name']
    ordering_fields = ['created_at', 'ends_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Subscription.objects.all()
        elif hasattr(user, 'tenant'):
            return Subscription.objects.filter(tenant=user.tenant)
        return Subscription.objects.none()

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        subscription = self.get_object()
        
        if subscription.status != 'active':
            return Response(
                {'error': 'Subscription is not active'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if subscription.stripe_subscription_id:
                # Cancel Stripe subscription
                stripe.Subscription.delete(subscription.stripe_subscription_id)
            
            # Update local subscription
            subscription.status = 'cancelled'
            subscription.cancelled_at = timezone.now()
            subscription.save()
            
            return Response({'message': 'Subscription cancelled successfully'})
            
        except stripe.error.StripeError as e:
            return Response(
                {'error': f'Cancellation failed: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['invoice_number', 'tenant__name']
    ordering_fields = ['issue_date', 'due_date']
    ordering = ['-issue_date']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Invoice.objects.all()
        elif hasattr(user, 'tenant'):
            return Invoice.objects.filter(tenant=user.tenant)
        return Invoice.objects.none()


class DiscountCodeViewSet(viewsets.ModelViewSet):
    serializer_class = DiscountCodeSerializer
    permission_classes = [IsAuthenticated, IsTenantAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['discount_type', 'is_active']
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['created_at', 'valid_until']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return DiscountCode.objects.all()
        elif hasattr(user, 'tenant'):
            return DiscountCode.objects.filter(tenant=user.tenant)
        return DiscountCode.objects.none()

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)

    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        discount_code = self.get_object()
        user = request.user
        
        is_valid = discount_code.is_valid and discount_code.can_use(user)
        
        return Response({
            'is_valid': is_valid,
            'discount_value': discount_code.discount_value,
            'discount_type': discount_code.discount_type,
            'used_count': discount_code.used_count,
            'remaining_uses': (
                discount_code.max_uses - discount_code.used_count 
                if discount_code.max_uses else None
            )
        })
