# Python LMS SaaS Platform

A comprehensive Learning Management System (LMS) built with Django, featuring multi-tenant architecture, video progress tracking, payment integration, and scalable design.

## Features

### Core Features
- **Multi-tenant Architecture**: Each school/company has isolated data
- **User Roles**: Admin, Teacher, Student with different permissions
- **Course Management**: Create, manage, and organize courses with modules and lessons
- **Video Progress Tracking**: Track student progress through video lessons
- **Enrollment System**: Student enrollment with progress monitoring
- **Payment Integration**: Stripe integration for paid courses
- **Assessment System**: Assignments, quizzes, and grading
- **Notifications**: Email, push, and in-app notifications
- **Caching**: Redis-based caching for performance
- **Background Tasks**: Celery for async operations

### Technical Features
- **RESTful API**: Django REST Framework with JWT authentication
- **Database**: PostgreSQL with optimized queries
- **Containerization**: Docker support for easy deployment
- **Testing**: Comprehensive unit tests
- **Scalable Architecture**: Designed for high concurrency
- **Security**: Best practices for authentication and authorization

## Architecture

```
lms_platform/
├── apps/
│   ├── tenants/          # Multi-tenant management
│   ├── users/            # User authentication and profiles
│   ├── courses/          # Course management
│   ├── enrollments/      # Student enrollments and assignments
│   ├── payments/         # Payment processing
│   └── notifications/    # Notification system
├── common/               # Shared utilities and middleware
├── config/               # Django settings and configuration
└── static/               # Static files
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL (for local development)
- Redis (for local development)

### Using Docker (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd lms-platform
```

2. **Environment Configuration**
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://lms_user:lms_password@db:5432/lms_platform
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key
STRIPE_SECRET_KEY=sk_test_your_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

3. **Build and run containers**
```bash
docker-compose up --build
```

4. **Run migrations**
```bash
docker-compose exec web python manage.py migrate
```

5. **Create a superuser**
```bash
docker-compose exec web python manage.py createsuperuser
```

6. **Create a tenant**
```bash
docker-compose exec web python manage.py setup_tenant \
    --name="Demo School" \
    --subdomain="demo" \
    --admin-email="admin@demo.com" \
    --admin-password="admin123"
```

### Local Development Setup

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Set up PostgreSQL and Redis**
Make sure PostgreSQL and Redis are running on your system.

3. **Environment variables**
Create a `.env` file as shown above.

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Create superuser**
```bash
python manage.py createsuperuser
```

6. **Run the development server**
```bash
python manage.py runserver
```

7. **Run Celery worker** (in a separate terminal)
```bash
celery -A lms_platform worker -l info
```

8. **Run Celery beat** (in another separate terminal)
```bash
celery -A lms_platform beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/v1/auth/register/
Content-Type: application/json

{
    "username": "newuser",
    "email": "user@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "first_name": "John",
    "last_name": "Doe"
}
```

#### Login
```http
POST /api/v1/auth/login/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password123"
}
```

#### Logout
```http
POST /api/v1/auth/logout/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "refresh_token": "<refresh_token>"
}
```

### Course Endpoints

#### List Courses
```http
GET /api/v1/courses/
Authorization: Bearer <access_token>
```

#### Create Course (Teacher/Admin)
```http
POST /api/v1/courses/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "title": "Python Programming",
    "description": "Learn Python from scratch",
    "short_description": "Python basics for beginners",
    "price": 99.99,
    "is_free": false,
    "estimated_hours": 40,
    "difficulty": "beginner"
}
```

#### Enroll in Course
```http
POST /api/v1/courses/{course_id}/enroll/
Authorization: Bearer <access_token>
```

#### Track Lesson Progress
```http
POST /api/v1/lessons/{lesson_id}/progress/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "completion_percentage": 75,
    "watch_time": 1800,
    "last_position": 1200
}
```

### Payment Endpoints

#### Create Payment
```http
POST /api/v1/payments/payments/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "course": "course_id",
    "amount": 99.99,
    "stripe_token": "tok_visa",
    "discount_code": "SAVE20"
}
```

## Testing

### Run all tests
```bash
python manage.py test
```

### Run specific test file
```bash
python manage.py test tests.test_models
python manage.py test tests.test_views
```

### Test coverage
```bash
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Deployment

### Production Environment Variables

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@host:5432/dbname
REDIS_URL=redis://host:6379/0

# Stripe Production Keys
STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key
STRIPE_SECRET_KEY=sk_live_your_secret_key

# Email Settings
EMAIL_HOST=your-smtp-server
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-password
```

### Docker Production Deployment

1. **Build production image**
```bash
docker build -t lms-platform:latest .
```

2. **Use production docker-compose**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Collect static files**
```bash
python manage.py collectstatic --noinput
```

3. **Run migrations**
```bash
python manage.py migrate
```

4. **Run with Gunicorn**
```bash
gunicorn lms_platform.config.wsgi:application --bind 0.0.0.0:8000
```

## Monitoring and Maintenance

### Health Checks
- `/api/v1/health/` - Application health status
- `/api/v1/health/db/` - Database connectivity
- `/api/v1/health/redis/` - Redis connectivity

### Logs
- Application logs: `logs/django.log`
- Celery logs: Check Celery worker output

### Database Maintenance
```bash
# Backup database
pg_dump lms_platform > backup.sql

# Restore database
psql lms_platform < backup.sql

# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

## Security Considerations

1. **Environment Variables**: Never commit `.env` files
2. **Database Security**: Use strong passwords and limit access
3. **API Security**: Use HTTPS in production
4. **CORS**: Configure allowed origins properly
5. **Rate Limiting**: Implement rate limiting for API endpoints
6. **Input Validation**: All inputs are validated at serializer level

## Performance Optimization

1. **Database Indexing**: Proper indexes on frequently queried fields
2. **Caching**: Redis caching for frequently accessed data
3. **Pagination**: All list endpoints are paginated
4. **Query Optimization**: Use `select_related` and `prefetch_related`
5. **Static Files**: Use CDN for static file serving

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run tests and ensure they pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Email: support@yourdomain.com
- Documentation: [Link to documentation]

## Roadmap

- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Video streaming optimization
- [ ] AI-powered course recommendations
- [ ] Integration with third-party tools (Zoom, Slack, etc.)
- [ ] Advanced reporting features
- [ ] Multi-language support
- [ ] Offline mode for mobile app
