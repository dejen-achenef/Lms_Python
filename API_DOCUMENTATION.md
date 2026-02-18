# API Documentation

## Overview

This document provides comprehensive API documentation for the LMS SaaS Platform. The API follows RESTful conventions and uses JWT authentication.

## Base URL

- **Development**: `http://localhost:8000/api/v1/`
- **Production**: `https://yourdomain.com/api/v1/`

## Authentication

The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Authentication Flow

1. **Register** a new user or **Login** with existing credentials
2. Receive `access_token` and `refresh_token`
3. Use `access_token` for API requests (expires in 1 hour)
4. Use `refresh_token` to get new `access_token` (expires in 7 days)

## Endpoints

### Authentication

#### Register User
```http
POST /auth/register/
```

**Request Body:**
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePassword123!",
    "password_confirm": "SecurePassword123!",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student"
}
```

**Response:**
```json
{
    "user": {
        "id": "uuid",
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "student",
        "is_active": true
    },
    "tokens": {
        "refresh": "refresh_token_here",
        "access": "access_token_here"
    }
}
```

#### Login
```http
POST /auth/login/
```

**Request Body:**
```json
{
    "email": "john@example.com",
    "password": "SecurePassword123!"
}
```

#### Refresh Token
```http
POST /auth/refresh_token/
```

**Request Body:**
```json
{
    "refresh_token": "refresh_token_here"
}
```

#### Logout
```http
POST /auth/logout/
```

**Request Body:**
```json
{
    "refresh_token": "refresh_token_here"
}
```

### Users

#### Get Current User Profile
```http
GET /users/me/
```

#### Update User Profile
```http
PATCH /users/me/
```

**Request Body:**
```json
{
    "first_name": "John",
    "last_name": "Smith",
    "phone_number": "+1234567890",
    "bio": "Software developer and learner"
}
```

#### Change Password
```http
POST /users/change_password/
```

**Request Body:**
```json
{
    "old_password": "OldPassword123!",
    "new_password": "NewPassword123!",
    "new_password_confirm": "NewPassword123!"
}
```

### Tenants

#### List Tenants (Admin only)
```http
GET /tenants/
```

#### Create Tenant (Superuser only)
```http
POST /tenants/
```

**Request Body:**
```json
{
    "name": "Academy School",
    "subdomain": "academy",
    "plan_type": "pro",
    "max_users": 100,
    "max_courses": 50
}
```

#### Get Tenant Settings
```http
GET /tenants/{tenant_id}/settings/
```

#### Update Tenant Settings
```http
PATCH /tenants/{tenant_id}/settings/
```

### Courses

#### List Courses
```http
GET /courses/
```

**Query Parameters:**
- `status`: Filter by status (`draft`, `published`, `archived`)
- `difficulty`: Filter by difficulty (`beginner`, `intermediate`, `advanced`)
- `is_free`: Filter by free/paid courses
- `category`: Filter by category ID
- `search`: Search in title and description
- `ordering`: Sort by field (`title`, `created_at`, `price`)

**Response:**
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/v1/courses/?page=2",
    "previous": null,
    "results": [
        {
            "id": "uuid",
            "title": "Python Programming",
            "description": "Learn Python from scratch",
            "short_description": "Python basics for beginners",
            "thumbnail": "http://example.com/media/thumbnail.jpg",
            "difficulty": "beginner",
            "status": "published",
            "language": "en",
            "is_free": false,
            "price": "99.99",
            "estimated_hours": 40,
            "instructor": "uuid",
            "instructor_name": "John Doe",
            "category": "uuid",
            "category_name": "Programming",
            "enrolled_students_count": 150,
            "average_rating": 4.5,
            "total_modules": 8,
            "total_lessons": 45,
            "is_full": false,
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]
}
```

#### Create Course (Teacher/Admin)
```http
POST /courses/
```

**Request Body:**
```json
{
    "title": "Advanced JavaScript",
    "description": "Master advanced JavaScript concepts",
    "short_description": "Advanced JS for experienced developers",
    "difficulty": "advanced",
    "price": 149.99,
    "is_free": false,
    "estimated_hours": 60,
    "category": "uuid"
}
```

#### Get Course Details
```http
GET /courses/{course_id}/
```

#### Update Course (Instructor/Admin)
```http
PATCH /courses/{course_id}/
```

#### Publish Course
```http
POST /courses/{course_id}/publish/
```

#### Archive Course
```http
POST /courses/{course_id}/archive/
```

#### Enroll in Course
```http
POST /courses/{course_id}/enroll/
```

#### Get Course Progress
```http
GET /courses/{course_id}/progress/
```

**Response:**
```json
{
    "enrollment_id": "uuid",
    "completion_percentage": 65,
    "completed_lessons": 29,
    "total_lessons": 45,
    "lesson_progress": [
        {
            "lesson_id": "uuid",
            "lesson_title": "Introduction to Python",
            "module_id": "uuid",
            "module_title": "Getting Started",
            "is_completed": true,
            "completion_percentage": 100,
            "watch_time": 1800,
            "last_position": 1800
        }
    ]
}
```

#### Get Course Modules
```http
GET /courses/{course_id}/modules/
```

#### Course Reviews
```http
GET /courses/{course_id}/reviews/
POST /courses/{course_id}/reviews/
```

**Request Body (POST):**
```json
{
    "rating": 5,
    "comment": "Excellent course! Very comprehensive.",
    "is_public": true
}
```

### Modules

#### List Modules
```http
GET /modules/?course_id={course_id}
```

#### Create Module
```http
POST /modules/
```

**Request Body:**
```json
{
    "title": "Getting Started",
    "description": "Introduction to the course",
    "course": "uuid",
    "order": 1,
    "is_published": true
}
```

### Lessons

#### List Lessons
```http
GET /lessons/?module_id={module_id}
```

#### Create Lesson
```http
POST /lessons/
```

**Request Body:**
```json
{
    "title": "Introduction to Python",
    "description": "Learn the basics of Python",
    "content": "Lesson content here...",
    "lesson_type": "video",
    "video_url": "https://example.com/video.mp4",
    "video_duration": 1800,
    "module": "uuid",
    "order": 1,
    "is_mandatory": true,
    "is_published": true
}
```

#### Get Lesson Details
```http
GET /lessons/{lesson_id}/
```

**Response:**
```json
{
    "id": "uuid",
    "title": "Introduction to Python",
    "description": "Learn the basics of Python",
    "content": "Lesson content here...",
    "lesson_type": "video",
    "video_url": "https://example.com/video.mp4",
    "video_duration": 1800,
    "resources": ["http://example.com/resource1.pdf"],
    "is_mandatory": true,
    "is_published": true,
    "allow_comments": true,
    "module": "uuid",
    "progress": {
        "is_completed": false,
        "completion_percentage": 45,
        "watch_time": 810,
        "last_position": 810
    },
    "bookmarks": [
        {
            "id": "uuid",
            "position": 900,
            "note": "Important concept here",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]
}
```

#### Update Lesson Progress
```http
POST /lessons/{lesson_id}/progress/
```

**Request Body:**
```json
{
    "completion_percentage": 75,
    "watch_time": 1350,
    "last_position": 1350
}
```

#### Mark Lesson as Completed
```http
POST /lessons/{lesson_id}/complete/
```

#### Lesson Bookmarks
```http
GET /lessons/{lesson_id}/bookmarks/
POST /lessons/{lesson_id}/bookmarks/
```

**Request Body (POST):**
```json
{
    "position": 900,
    "note": "Important concept about variables"
}
```

### Categories

#### List Categories
```http
GET /categories/
```

#### Create Category
```http
POST /categories/
```

**Request Body:**
```json
{
    "name": "Programming",
    "description": "Programming and development courses",
    "parent": null
}
```

### Payments

#### Create Payment
```http
POST /payments/payments/
```

**Request Body:**
```json
{
    "course": "uuid",
    "amount": 99.99,
    "stripe_token": "tok_visa",
    "discount_code": "SAVE20"
}
```

#### List User Payments
```http
GET /payments/payments/
```

#### Process Refund
```http
POST /payments/payments/{payment_id}/refund/
```

**Request Body:**
```json
{
    "amount": 50.00,
    "reason": "Customer request"
}
```

#### Discount Codes
```http
GET /payments/discount-codes/
POST /payments/discount-codes/
```

**Request Body (POST):**
```json
{
    "code": "SAVE20",
    "name": "20% Off",
    "description": "Get 20% off on any course",
    "discount_type": "percentage",
    "discount_value": 20,
    "max_uses": 100,
    "valid_from": "2024-01-01T00:00:00Z",
    "valid_until": "2024-12-31T23:59:59Z"
}
```

#### Validate Discount Code
```http
POST /payments/discount-codes/{code_id}/validate/
```

## Error Handling

The API returns standard HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `429` - Rate Limited
- `500` - Internal Server Error

**Error Response Format:**
```json
{
    "error": "Error message",
    "details": {
        "field_name": ["Error details for this field"]
    }
}
```

## Rate Limiting

- General API endpoints: 10 requests per second
- Login endpoint: 1 request per second
- File upload endpoints: 5 requests per minute

## Pagination

List endpoints support pagination with `page` and `page_size` parameters:

```
GET /courses/?page=2&page_size=20
```

Default page size is 20, maximum is 100.

## File Uploads

Use `multipart/form-data` for file uploads:

```http
POST /courses/
Content-Type: multipart/form-data

title=New Course
thumbnail=@image.jpg
```

## SDK Examples

### Python (requests)

```python
import requests

# Login
response = requests.post('http://localhost:8000/api/v1/auth/login/', json={
    'email': 'user@example.com',
    'password': 'password123'
})
tokens = response.json()['tokens']
access_token = tokens['access']

# Get courses
headers = {'Authorization': f'Bearer {access_token}'}
response = requests.get('http://localhost:8000/api/v1/courses/', headers=headers)
courses = response.json()
```

### JavaScript (fetch)

```javascript
// Login
const loginResponse = await fetch('/api/v1/auth/login/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        email: 'user@example.com',
        password: 'password123'
    })
});
const {tokens} = await loginResponse.json();

// Get courses
const coursesResponse = await fetch('/api/v1/courses/', {
    headers: {'Authorization': `Bearer ${tokens.access}`}
});
const courses = await coursesResponse.json();
```

## Testing

Use the provided test suite to verify API functionality:

```bash
# Run all tests
python manage.py test

# Run specific tests
python manage.py test tests.test_views

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## Support

For API support:
- Check the error messages for detailed information
- Review the authentication requirements
- Verify request formats and required fields
- Contact support at api-support@yourdomain.com
