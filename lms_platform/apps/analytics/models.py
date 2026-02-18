from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q
import uuid
import json

User = get_user_model()


class LearningAnalytics(models.Model):
    """Track detailed learning analytics for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_analytics')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='learning_analytics')
    
    # Time tracking
    total_time_spent = models.IntegerField(default=0)  # in minutes
    session_count = models.IntegerField(default=0)
    average_session_duration = models.FloatField(default=0.0)  # in minutes
    
    # Progress tracking
    lessons_completed = models.IntegerField(default=0)
    lessons_started = models.IntegerField(default=0)
    completion_rate = models.FloatField(default=0.0)
    
    # Engagement metrics
    video_watch_time = models.IntegerField(default=0)  # in seconds
    quiz_attempts = models.IntegerField(default=0)
    quiz_average_score = models.FloatField(default=0.0)
    assignment_submissions = models.IntegerField(default=0)
    
    # Learning patterns
    most_active_hour = models.IntegerField(default=12)  # 0-23
    learning_streak = models.IntegerField(default=0)  # consecutive days
    last_activity_date = models.DateTimeField(auto_now=True)
    
    # Performance indicators
    knowledge_retention_score = models.FloatField(default=0.0)
    skill_improvement_rate = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learning_analytics'
        unique_together = ['user', 'course']
        indexes = [
            models.Index(fields=['user', 'course']),
            models.Index(fields=['course', 'completion_rate']),
            models.Index(fields=['last_activity_date']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.course.title}"

    def update_session_data(self, session_duration, video_watch_time=0):
        """Update session-based analytics"""
        self.total_time_spent += session_duration
        self.session_count += 1
        self.average_session_duration = self.total_time_spent / self.session_count
        self.video_watch_time += video_watch_time
        self.last_activity_date = timezone.now()
        self.save()

    def calculate_completion_rate(self):
        """Calculate course completion rate"""
        total_lessons = self.course.total_lessons
        if total_lessons > 0:
            self.completion_rate = (self.lessons_completed / total_lessons) * 100
        self.save()


class CourseAnalytics(models.Model):
    """Track course-level analytics"""
    course = models.OneToOneField('courses.Course', on_delete=models.CASCADE, related_name='course_analytics')
    
    # Enrollment metrics
    total_enrollments = models.IntegerField(default=0)
    active_enrollments = models.IntegerField(default=0)
    completion_rate = models.FloatField(default=0.0)
    dropout_rate = models.FloatField(default=0.0)
    
    # Engagement metrics
    average_completion_time = models.IntegerField(default=0)  # in days
    average_session_duration = models.FloatField(default=0.0)
    total_watch_time = models.IntegerField(default=0)  # in minutes
    
    # Performance metrics
    average_rating = models.FloatField(default=0.0)
    review_count = models.IntegerField(default=0)
    certificate_issued = models.IntegerField(default=0)
    
    # Revenue metrics
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    average_revenue_per_student = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    # Popularity metrics
    enrollment_trend = models.JSONField(default=list)  # Last 30 days
    completion_trend = models.JSONField(default=list)  # Last 30 days
    revenue_trend = models.JSONField(default=list)  # Last 30 days
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_analytics'

    def __str__(self):
        return f"Analytics for {self.course.title}"

    def update_enrollment_metrics(self):
        """Update enrollment-related metrics"""
        from apps.enrollments.models import Enrollment
        
        enrollments = Enrollment.objects.filter(course=self.course)
        self.total_enrollments = enrollments.count()
        self.active_enrollments = enrollments.filter(is_active=True).count()
        
        completed_enrollments = enrollments.filter(status='completed').count()
        if self.total_enrollments > 0:
            self.completion_rate = (completed_enrollments / self.total_enrollments) * 100
            self.dropout_rate = ((self.total_enrollments - completed_enrollments) / self.total_enrollments) * 100
        
        self.save()

    def calculate_revenue_metrics(self):
        """Calculate revenue-related metrics"""
        from apps.payments.models import Payment
        
        payments = Payment.objects.filter(course=self.course, status='completed')
        self.total_revenue = payments.aggregate(total=Sum('amount'))['total'] or 0
        
        if self.active_enrollments > 0:
            self.average_revenue_per_student = self.total_revenue / self.active_enrollments
        
        self.save()


class UserActivityLog(models.Model):
    """Track all user activities for detailed analytics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    
    # Activity details
    activity_type = models.CharField(max_length=50)  # login, lesson_start, lesson_complete, etc.
    activity_description = models.TextField()
    
    # Related objects
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, null=True, blank=True)
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE, null=True, blank=True)
    quiz = models.ForeignKey('enrollments.Assignment', on_delete=models.CASCADE, null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Timing
    duration = models.IntegerField(null=True, blank=True)  # in seconds
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_activity_logs'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['activity_type', 'created_at']),
            models.Index(fields=['course', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.activity_type}"


class LearningPath(models.Model):
    """AI-powered learning paths for personalized education"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    # Target audience
    skill_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ])
    target_roles = models.JSONField(default=list)  # ['developer', 'designer', 'manager']
    
    # Path structure
    courses = models.ManyToManyField('courses.Course', related_name='learning_paths', through='LearningPathCourse')
    estimated_duration = models.IntegerField(default=0)  # in hours
    difficulty_progression = models.JSONField(default=list)  # [1, 2, 3, 4, 5]
    
    # AI-generated metadata
    required_skills = models.JSONField(default=list)
    acquired_skills = models.JSONField(default=list)
    prerequisites = models.JSONField(default=list)
    
    # Performance metrics
    enrollment_count = models.IntegerField(default=0)
    completion_count = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0.0)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='learning_paths')
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learning_paths'
        ordering = ['name']

    def __str__(self):
        return self.name

    def calculate_success_rate(self):
        """Calculate the success rate of this learning path"""
        if self.enrollment_count > 0:
            self.success_rate = (self.completion_count / self.enrollment_count) * 100
        self.save()


class LearningPathCourse(models.Model):
    """Through model for learning path courses with order and prerequisites"""
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    is_mandatory = models.BooleanField(default=True)
    min_completion_percentage = models.IntegerField(default=100)
    
    class Meta:
        db_table = 'learning_path_courses'
        unique_together = ['learning_path', 'course']
        ordering = ['order']


class UserLearningPath(models.Model):
    """Track user progress through learning paths"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_paths')
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='user_enrollments')
    
    # Progress tracking
    current_course = models.ForeignKey('courses.Course', on_delete=models.SET_NULL, null=True, blank=True)
    completed_courses = models.ManyToManyField('courses.Course', related_name='completed_by_users', blank=True)
    completion_percentage = models.FloatField(default=0.0)
    
    # Timing
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    estimated_completion_date = models.DateTimeField(null=True, blank=True)
    
    # Performance
    average_score = models.FloatField(default=0.0)
    skill_assessment_score = models.FloatField(default=0.0)
    
    class Meta:
        db_table = 'user_learning_paths'
        unique_together = ['user', 'learning_path']

    def __str__(self):
        return f"{self.user.email} - {self.learning_path.name}"

    def update_progress(self):
        """Update user progress through the learning path"""
        total_courses = self.learning_path.courses.count()
        completed_count = self.completed_courses.count()
        
        if total_courses > 0:
            self.completion_percentage = (completed_count / total_courses) * 100
        
        if self.completion_percentage >= 100 and not self.completed_at:
            self.completed_at = timezone.now()
            self.learning_path.completion_count += 1
            self.learning_path.save()
        
        self.save()


class RecommendationEngine(models.Model):
    """AI-powered course recommendations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='recommendations')
    
    # Recommendation details
    score = models.FloatField(default=0.0)  # 0.0 to 1.0
    reason = models.TextField()
    recommendation_type = models.CharField(max_length=20, choices=[
        ('collaborative', 'Collaborative Filtering'),
        ('content_based', 'Content-Based'),
        ('popularity', 'Popularity-Based'),
        ('trending', 'Trending'),
        ('personalized', 'Personalized AI'),
    ])
    
    # Context
    context_data = models.JSONField(default=dict)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Interaction tracking
    clicked = models.BooleanField(default=False)
    enrolled = models.BooleanField(default=False)
    clicked_at = models.DateTimeField(null=True, blank=True)
    enrolled_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'recommendations'
        indexes = [
            models.Index(fields=['user', 'score']),
            models.Index(fields=['course', 'score']),
            models.Index(fields=['recommendation_type']),
        ]

    def __str__(self):
        return f"Recommendation: {self.course.title} for {self.user.email}"


class AILearningInsight(models.Model):
    """AI-generated insights about learning patterns"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_insights')
    insight_type = models.CharField(max_length=50, choices=[
        ('learning_pattern', 'Learning Pattern'),
        ('knowledge_gap', 'Knowledge Gap'),
        ('improvement_suggestion', 'Improvement Suggestion'),
        ('motivation_alert', 'Motivation Alert'),
        ('achievement_milestone', 'Achievement Milestone'),
    ])
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    actionable_recommendations = models.JSONField(default=list)
    
    # Confidence and priority
    confidence_score = models.FloatField(default=0.0)  # 0.0 to 1.0
    priority_level = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], default='medium')
    
    # Related data
    related_courses = models.ManyToManyField('courses.Course', blank=True)
    related_lessons = models.ManyToManyField('courses.Lesson', blank=True)
    metadata = models.JSONField(default=dict)
    
    # Status
    is_read = models.BooleanField(default=False)
    is_actioned = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    actioned_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'ai_learning_insights'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.title}"
