from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.tenants.models import Tenant
from apps.courses.models import Course, Category

User = get_user_model()


class AuthenticationTest(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test School",
            subdomain="testschool"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            tenant=self.tenant
        )

    def test_user_registration(self):
        url = reverse('auth-register')
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)

    def test_user_login(self):
        url = reverse('auth-login')
        data = {
            'email': 'test@test.com',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])

    def test_invalid_login(self):
        url = reverse('auth-login')
        data = {
            'email': 'test@test.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CourseViewTest(APITestCase):
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
        self.student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123",
            role="student",
            tenant=self.tenant
        )
        self.category = Category.objects.create(
            name="Programming",
            tenant=self.tenant
        )
        self.course = Course.objects.create(
            title="Python Programming",
            description="Learn Python",
            short_description="Python basics",
            instructor=self.instructor,
            tenant=self.tenant,
            category=self.category,
            price=99.99,
            is_free=False,
            status='published'
        )

    def test_course_list(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('course-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_course_create_as_teacher(self):
        self.client.force_authenticate(user=self.instructor)
        url = reverse('course-list')
        data = {
            'title': 'New Course',
            'description': 'Course description',
            'short_description': 'Short description',
            'price': 49.99,
            'is_free': False,
            'estimated_hours': 20
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Course')

    def test_course_create_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('course-list')
        data = {
            'title': 'New Course',
            'description': 'Course description',
            'short_description': 'Short description'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_enrollment(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('course-enroll', kwargs={'pk': self.course.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('enrollment_id', response.data)
        
        # Check enrollment was created
        from apps.enrollments.models import Enrollment
        enrollment = Enrollment.objects.get(student=self.student, course=self.course)
        self.assertTrue(enrollment.is_active)

    def test_course_progress_tracking(self):
        # First enroll the student
        from apps.enrollments.models import Enrollment
        enrollment = Enrollment.objects.create(student=self.student, course=self.course)
        
        self.client.force_authenticate(user=self.student)
        url = reverse('course-progress', kwargs={'pk': self.course.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('completion_percentage', response.data)
        self.assertIn('completed_lessons', response.data)


class TenantViewTest(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test School",
            subdomain="testschool"
        )
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123",
            role="admin",
            tenant=self.tenant
        )
        self.regular_user = User.objects.create_user(
            username="user",
            email="user@test.com",
            password="testpass123",
            role="student",
            tenant=self.tenant
        )

    def test_tenant_list_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('tenant-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_tenant_create_as_superuser(self):
        # Create superuser
        superuser = User.objects.create_superuser(
            username="superadmin",
            email="super@test.com",
            password="testpass123"
        )
        
        self.client.force_authenticate(user=superuser)
        url = reverse('tenant-list')
        data = {
            'name': 'New School',
            'subdomain': 'newschool',
            'plan_type': 'pro',
            'max_users': 100,
            'max_courses': 20
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New School')

    def test_tenant_stats_as_superuser(self):
        superuser = User.objects.create_superuser(
            username="superadmin",
            email="super@test.com",
            password="testpass123"
        )
        
        self.client.force_authenticate(user=superuser)
        url = reverse('tenant-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_tenants', response.data)
        self.assertIn('active_tenants', response.data)
