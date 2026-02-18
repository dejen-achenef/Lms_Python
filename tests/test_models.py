from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from apps.tenants.models import Tenant
from apps.courses.models import Course, Module, Lesson, Category
from apps.enrollments.models import Enrollment, Assignment
from apps.payments.models import Payment, DiscountCode
from apps.notifications.models import Notification

User = get_user_model()


class TenantModelTest(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test School",
            subdomain="testschool",
            plan_type="basic",
            max_users=50,
            max_courses=10
        )

    def test_tenant_creation(self):
        self.assertEqual(self.tenant.name, "Test School")
        self.assertEqual(self.tenant.subdomain, "testschool")
        self.assertTrue(self.tenant.is_active)
        self.assertFalse(self.tenant.is_enterprise)

    def test_tenant_str_method(self):
        self.assertEqual(str(self.tenant), "Test School")

    def test_user_count_property(self):
        # Create users for this tenant
        User.objects.create_user(
            username="user1",
            email="user1@test.com",
            password="testpass123",
            tenant=self.tenant
        )
        User.objects.create_user(
            username="user2",
            email="user2@test.com",
            password="testpass123",
            tenant=self.tenant
        )
        
        self.assertEqual(self.tenant.user_count, 2)


class CourseModelTest(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test School",
            subdomain="testschool"
        )
        self.instructor = User.objects.create_user(
            username="instructor",
            email="instructor@test.com",
            password="testpass123",
            role="teacher",
            tenant=self.tenant
        )
        self.category = Category.objects.create(
            name="Programming",
            tenant=self.tenant
        )
        self.course = Course.objects.create(
            title="Python Programming",
            description="Learn Python from scratch",
            short_description="Python basics",
            instructor=self.instructor,
            tenant=self.tenant,
            category=self.category,
            price=99.99,
            is_free=False,
            estimated_hours=40
        )

    def test_course_creation(self):
        self.assertEqual(self.course.title, "Python Programming")
        self.assertEqual(self.course.instructor, self.instructor)
        self.assertEqual(self.course.tenant, self.tenant)
        self.assertFalse(self.course.is_free)
        self.assertEqual(self.course.price, 99.99)

    def test_course_str_method(self):
        self.assertEqual(str(self.course), "Python Programming")

    def test_enrolled_students_count(self):
        # Create students and enroll them
        student1 = User.objects.create_user(
            username="student1",
            email="student1@test.com",
            password="testpass123",
            role="student",
            tenant=self.tenant
        )
        student2 = User.objects.create_user(
            username="student2",
            email="student2@test.com",
            password="testpass123",
            role="student",
            tenant=self.tenant
        )
        
        Enrollment.objects.create(student=student1, course=self.course)
        Enrollment.objects.create(student=student2, course=self.course)
        
        self.assertEqual(self.course.enrolled_students_count, 2)

    def test_average_rating(self):
        # Add reviews
        from apps.courses.models import CourseReview
        CourseReview.objects.create(
            user=student1,
            course=self.course,
            rating=5,
            comment="Great course!"
        )
        CourseReview.objects.create(
            user=student2,
            course=self.course,
            rating=4,
            comment="Good course!"
        )
        
        self.assertEqual(self.course.average_rating, 4.5)


class LessonProgressTest(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test School",
            subdomain="testschool"
        )
        self.student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123",
            role="student",
            tenant=self.tenant
        )
        self.instructor = User.objects.create_user(
            username="instructor",
            email="instructor@test.com",
            password="testpass123",
            role="teacher",
            tenant=self.tenant
        )
        self.course = Course.objects.create(
            title="Test Course",
            description="Test Description",
            short_description="Test",
            instructor=self.instructor,
            tenant=self.tenant,
            price=0,
            is_free=True,
            estimated_hours=10
        )
        self.module = Module.objects.create(
            title="Test Module",
            course=self.course,
            order=1
        )
        self.lesson = Lesson.objects.create(
            title="Test Lesson",
            module=self.module,
            order=1,
            lesson_type="video"
        )

    def test_lesson_progress_creation(self):
        from apps.courses.models import LessonProgress
        
        progress = LessonProgress.objects.create(
            user=self.student,
            lesson=self.lesson,
            completion_percentage=50,
            watch_time=1800  # 30 minutes
        )
        
        self.assertEqual(progress.user, self.student)
        self.assertEqual(progress.lesson, self.lesson)
        self.assertEqual(progress.completion_percentage, 50)
        self.assertFalse(progress.is_completed)

    def test_mark_completed(self):
        from apps.courses.models import LessonProgress
        
        progress = LessonProgress.objects.create(
            user=self.student,
            lesson=self.lesson
        )
        
        progress.mark_completed()
        
        self.assertTrue(progress.is_completed)
        self.assertEqual(progress.completion_percentage, 100)
        self.assertIsNotNone(progress.completed_at)


class PaymentModelTest(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test School",
            subdomain="testschool"
        )
        self.student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123",
            role="student",
            tenant=self.tenant
        )
        self.instructor = User.objects.create_user(
            username="instructor",
            email="instructor@test.com",
            password="testpass123",
            role="teacher",
            tenant=self.tenant
        )
        self.course = Course.objects.create(
            title="Paid Course",
            description="Test Description",
            short_description="Test",
            instructor=self.instructor,
            tenant=self.tenant,
            price=99.99,
            is_free=False,
            estimated_hours=10
        )

    def test_payment_creation(self):
        payment = Payment.objects.create(
            user=self.student,
            course=self.course,
            amount=99.99,
            status='completed',
            payment_method='stripe'
        )
        
        self.assertEqual(payment.user, self.student)
        self.assertEqual(payment.course, self.course)
        self.assertEqual(payment.amount, 99.99)
        self.assertEqual(payment.status, 'completed')

    def test_refund_processing(self):
        payment = Payment.objects.create(
            user=self.student,
            course=self.course,
            amount=99.99,
            status='completed',
            payment_method='stripe'
        )
        
        payment.process_refund(50.00, "Partial refund")
        
        self.assertEqual(payment.refund_amount, 50.00)
        self.assertEqual(payment.refund_reason, "Partial refund")
        self.assertEqual(payment.status, 'completed')  # Still completed, not fully refunded


class DiscountCodeTest(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test School",
            subdomain="testschool"
        )
        self.discount_code = DiscountCode.objects.create(
            code="SAVE20",
            name="20% Off",
            discount_type="percentage",
            discount_value=20,
            max_uses=100,
            tenant=self.tenant
        )

    def test_discount_code_creation(self):
        self.assertEqual(self.discount_code.code, "SAVE20")
        self.assertEqual(self.discount_code.discount_type, "percentage")
        self.assertEqual(self.discount_code.discount_value, 20)

    def test_apply_discount_percentage(self):
        amount = 100.00
        discount_amount = self.discount_code.apply_discount(amount)
        self.assertEqual(discount_amount, 20.00)

    def test_apply_discount_fixed(self):
        fixed_discount = DiscountCode.objects.create(
            code="SAVE10",
            name="$10 Off",
            discount_type="fixed",
            discount_value=10,
            tenant=self.tenant
        )
        
        amount = 100.00
        discount_amount = fixed_discount.apply_discount(amount)
        self.assertEqual(discount_amount, 10.00)

    def test_record_usage(self):
        initial_count = self.discount_code.used_count
        self.discount_code.record_usage()
        self.assertEqual(self.discount_code.used_count, initial_count + 1)
