from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.tenants.models import Tenant, TenantSettings
from apps.users.models import UserProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a new tenant with admin user and default settings'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, required=True, help='Tenant name')
        parser.add_argument('--subdomain', type=str, required=True, help='Tenant subdomain')
        parser.add_argument('--admin-email', type=str, required=True, help='Admin user email')
        parser.add_argument('--admin-password', type=str, required=True, help='Admin user password')
        parser.add_argument('--admin-first-name', type=str, default='Admin', help='Admin first name')
        parser.add_argument('--admin-last-name', type=str, default='User', help='Admin last name')
        parser.add_argument('--plan', type=str, default='basic', choices=['basic', 'pro', 'enterprise'], help='Subscription plan')
        parser.add_argument('--max-users', type=int, default=50, help='Maximum users')
        parser.add_argument('--max-courses', type=int, default=10, help='Maximum courses')

    def handle(self, *args, **options):
        name = options['name']
        subdomain = options['subdomain']
        admin_email = options['admin_email']
        admin_password = options['admin_password']
        admin_first_name = options['admin_first_name']
        admin_last_name = options['admin_last_name']
        plan = options['plan']
        max_users = options['max_users']
        max_courses = options['max_courses']

        # Check if tenant already exists
        if Tenant.objects.filter(subdomain=subdomain).exists():
            self.stdout.write(
                self.style.ERROR(f'Tenant with subdomain "{subdomain}" already exists')
            )
            return

        # Create tenant
        tenant = Tenant.objects.create(
            name=name,
            subdomain=subdomain,
            plan_type=plan,
            max_users=max_users,
            max_courses=max_courses
        )

        # Create tenant settings
        TenantSettings.objects.create(tenant=tenant)

        # Create admin user
        admin_user = User.objects.create_user(
            username=admin_email,
            email=admin_email,
            password=admin_password,
            first_name=admin_first_name,
            last_name=admin_last_name,
            role='admin',
            tenant=tenant,
            is_staff=True,
            is_superuser=False
        )

        # Create user profile
        UserProfile.objects.create(user=admin_user)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created tenant "{name}" with admin user "{admin_email}"'
            )
        )
        self.stdout.write(f'Tenant ID: {tenant.id}')
        self.stdout.write(f'Admin User ID: {admin_user.id}')
        self.stdout.write(f'Login URL: http://localhost:8000/api/v1/auth/login/')
