from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='categories')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_categories'
        verbose_name_plural = 'Categories'
        unique_together = ['name', 'tenant', 'parent']
        ordering = ['name']

    def __str__(self):
        return self.name


class Course(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    short_description = models.CharField(max_length=500)
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    
    # Course details
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    language = models.CharField(max_length=10, default='en')
    
    # Pricing
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Duration and workload
    estimated_hours = models.IntegerField(validators=[MinValueValidator(1)])
    max_students = models.IntegerField(null=True, blank=True)
    
    # Relationships
    instructor = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='courses_taught')
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='courses')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'courses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['instructor', 'status']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.title

    @property
    def enrolled_students_count(self):
        return self.enrollments.filter(is_active=True).count()

    @property
    def average_rating(self):
        ratings = self.reviews.aggregate(models.Avg('rating'))['rating__avg']
        return round(ratings, 2) if ratings else 0

    @property
    def total_modules(self):
        return self.modules.count()

    @property
    def total_lessons(self):
        return self.modules.aggregate(total=models.Count('lessons'))['total'] or 0

    @property
    def is_full(self):
        if self.max_students is None:
            return False
        return self.enrolled_students_count >= self.max_students


class Module(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    is_published = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_modules'
        ordering = ['order']
        unique_together = ['course', 'order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    @property
    def total_lessons(self):
        return self.lessons.count()

    @property
    def completed_lessons(self, user):
        return self.lessons.filter(progress__user=user, progress__is_completed=True).count()


class Lesson(models.Model):
    LESSON_TYPES = [
        ('video', 'Video'),
        ('text', 'Text'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('live', 'Live Session'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES, default='video')
    order = models.PositiveIntegerField()
    
    # Video specific fields
    video_url = models.URLField(blank=True, null=True)
    video_duration = models.IntegerField(null=True, blank=True)  # in seconds
    
    # Resources
    resources = models.JSONField(default=list, blank=True)  # List of file URLs
    
    # Settings
    is_mandatory = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=True)
    
    # Relationships
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lessons'
        ordering = ['order']
        unique_together = ['module', 'order']

    def __str__(self):
        return f"{self.module.title} - {self.title}"


class LessonProgress(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    
    # Progress tracking
    is_completed = models.BooleanField(default=False)
    completion_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    watch_time = models.IntegerField(default=0)  # in seconds
    
    # Video specific
    last_position = models.IntegerField(default=0)  # last watched position in seconds
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lesson_progress'
        unique_together = ['user', 'lesson']
        indexes = [
            models.Index(fields=['user', 'is_completed']),
            models.Index(fields=['lesson', 'is_completed']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.lesson.title}"

    def mark_completed(self):
        if not self.is_completed:
            self.is_completed = True
            self.completion_percentage = 100
            self.completed_at = timezone.now()
            self.save()


class CourseReview(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='reviews')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    is_public = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_reviews'
        unique_together = ['user', 'course']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.course.title} ({self.rating} stars)"


class CourseBookmark(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='bookmarks')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='bookmarks')
    position = models.IntegerField(default=0)  # bookmark position in seconds
    note = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'course_bookmarks'
        unique_together = ['user', 'lesson']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.lesson.title}"
