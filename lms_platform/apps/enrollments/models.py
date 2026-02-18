from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='enrollments')
    
    # Enrollment details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    
    # Progress tracking
    completion_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    total_time_spent = models.IntegerField(default=0)  # in minutes
    
    # Certificate
    certificate_issued = models.BooleanField(default=False)
    certificate_url = models.URLField(blank=True, null=True)
    
    # Payment related
    is_paid = models.BooleanField(default=False)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'enrollments'
        unique_together = ['student', 'course']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['course', 'status']),
            models.Index(fields=['enrollment_date']),
        ]

    def __str__(self):
        return f"{self.student.email} - {self.course.title}"

    @property
    def completed_lessons(self):
        from apps.courses.models import LessonProgress
        return LessonProgress.objects.filter(
            user=self.student,
            lesson__module__course=self.course,
            is_completed=True
        ).count()

    @property
    def total_lessons(self):
        return self.course.total_lessons

    @property
    def progress_percentage(self):
        if self.total_lessons == 0:
            return 0
        return round((self.completed_lessons / self.total_lessons) * 100, 2)

    def update_progress(self):
        self.completion_percentage = self.progress_percentage
        if self.completion_percentage >= 100 and not self.completion_date:
            self.status = 'completed'
            self.completion_date = timezone.now()
        self.save()

    def mark_completed(self):
        self.status = 'completed'
        self.completion_percentage = 100
        self.completion_date = timezone.now()
        self.save()


class Assignment(models.Model):
    ASSIGNMENT_TYPES = [
        ('quiz', 'Quiz'),
        ('essay', 'Essay'),
        ('project', 'Project'),
        ('presentation', 'Presentation'),
        ('coding', 'Coding Exercise'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    instructions = models.TextField(blank=True, null=True)
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_TYPES, default='essay')
    
    # Points and grading
    max_points = models.IntegerField(validators=[MinValueValidator(1)])
    passing_score = models.IntegerField(validators=[MinValueValidator(1)])
    
    # Availability
    available_from = models.DateTimeField()
    due_date = models.DateTimeField()
    late_submission_allowed = models.BooleanField(default=True)
    
    # Relationships
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE, related_name='assignments')
    
    # Settings
    allow_multiple_attempts = models.BooleanField(default=False)
    max_attempts = models.IntegerField(default=1)
    time_limit = models.IntegerField(null=True, blank=True)  # in minutes
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'assignments'
        ordering = ['due_date']

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"

    @property
    def is_overdue(self):
        return timezone.now() > self.due_date

    @property
    def is_available(self):
        return timezone.now() >= self.available_from


class Submission(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
        ('returned', 'Returned'),
        ('late', 'Late'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='submissions')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    
    # Submission content
    content = models.TextField(blank=True, null=True)
    file_attachments = models.JSONField(default=list, blank=True)  # List of file URLs
    
    # Grading
    score = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)
    graded_by = models.ForeignKey(
        'users.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='graded_submissions'
    )
    
    # Status and timestamps
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    attempt_number = models.IntegerField(default=1)
    submitted_at = models.DateTimeField(auto_now_add=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'submissions'
        unique_together = ['student', 'assignment', 'attempt_number']
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.email} - {self.assignment.title}"

    @property
    def is_late(self):
        return self.submitted_at > self.assignment.due_date

    @property
    def percentage_score(self):
        if self.score is None or self.assignment.max_points == 0:
            return 0
        return round((self.score / self.assignment.max_points) * 100, 2)

    @property
    def is_passing(self):
        if self.score is None:
            return False
        return self.score >= self.assignment.passing_score


class Grade(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='grades')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='grades')
    
    # Grade details
    midterm_score = models.IntegerField(null=True, blank=True)
    final_score = models.IntegerField(null=True, blank=True)
    assignment_score = models.IntegerField(null=True, blank=True)
    participation_score = models.IntegerField(null=True, blank=True)
    
    # Final grade
    final_grade = models.IntegerField(null=True, blank=True)
    grade_letter = models.CharField(max_length=2, blank=True, null=True)
    
    # Grading scale (can be customized per tenant)
    grading_scale = models.JSONField(default=dict)  # {'A': 90, 'B': 80, 'C': 70, 'D': 60, 'F': 0}
    
    # Timestamps
    graded_by = models.ForeignKey(
        'users.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_grades'
    )
    graded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'grades'
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student.email} - {self.course.title} ({self.grade_letter or 'N/A'})"

    def calculate_final_grade(self):
        weights = {
            'midterm': 0.30,
            'final': 0.40,
            'assignment': 0.20,
            'participation': 0.10
        }
        
        total = 0
        total_weight = 0
        
        if self.midterm_score is not None:
            total += self.midterm_score * weights['midterm']
            total_weight += weights['midterm']
        
        if self.final_score is not None:
            total += self.final_score * weights['final']
            total_weight += weights['final']
        
        if self.assignment_score is not None:
            total += self.assignment_score * weights['assignment']
            total_weight += weights['assignment']
        
        if self.participation_score is not None:
            total += self.participation_score * weights['participation']
            total_weight += weights['participation']
        
        if total_weight > 0:
            self.final_grade = round(total / total_weight)
            self.assign_grade_letter()
        else:
            self.final_grade = None
            self.grade_letter = None

    def assign_grade_letter(self):
        if not self.final_grade:
            self.grade_letter = None
            return
        
        scale = self.grading_scale or {'A': 90, 'B': 80, 'C': 70, 'D': 60, 'F': 0}
        
        for grade, min_score in sorted(scale.items(), key=lambda x: x[1], reverse=True):
            if self.final_grade >= min_score:
                self.grade_letter = grade
                return
        
        self.grade_letter = 'F'
