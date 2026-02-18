from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import json

User = get_user_model()


class Quiz(models.Model):
    """Advanced quiz with multiple question types and adaptive difficulty"""
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay'),
        ('fill_blank', 'Fill in the Blank'),
        ('matching', 'Matching'),
        ('ordering', 'Ordering'),
        ('hotspot', 'Hotspot/Image'),
        ('drag_drop', 'Drag and Drop'),
        ('coding', 'Coding Challenge'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('adaptive', 'Adaptive'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    instructions = models.TextField(blank=True, null=True)
    
    # Quiz settings
    time_limit = models.IntegerField(null=True, blank=True)  # in minutes
    max_attempts = models.IntegerField(default=1)
    passing_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='intermediate')
    
    # Adaptive settings
    is_adaptive = models.BooleanField(default=False)
    min_questions = models.IntegerField(default=1)
    max_questions = models.IntegerField(default=50)
    
    # Randomization
    shuffle_questions = models.BooleanField(default=False)
    shuffle_answers = models.BooleanField(default=False)
    
    # Feedback settings
    show_correct_answers = models.BooleanField(default=False)
    show_feedback = models.BooleanField(default=True)
    allow_review = models.BooleanField(default=True)
    
    # Availability
    available_from = models.DateTimeField(null=True, blank=True)
    available_until = models.DateTimeField(null=True, blank=True)
    
    # Relationships
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE, related_name='quizzes', null=True, blank=True)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='quizzes', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_quizzes')
    
    # Metadata
    tags = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quizzes'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def total_questions(self):
        return self.questions.count()

    @property
    def is_available(self):
        now = timezone.now()
        if self.available_from and now < self.available_from:
            return False
        if self.available_until and now > self.available_until:
            return False
        return True


class Question(models.Model):
    """Individual quiz questions with rich content"""
    QUESTION_TYPES = Quiz.QUESTION_TYPES
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    
    # Question content
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    explanation = models.TextField(blank=True, null=True)
    
    # Media
    image = models.ImageField(upload_to='quiz_images/', blank=True, null=True)
    audio = models.FileField(upload_to='quiz_audio/', blank=True, null=True)
    video = models.FileField(upload_to='quiz_video/', blank=True, null=True)
    
    # Difficulty and points
    difficulty = models.CharField(max_length=20, choices=Quiz.DIFFICULTY_LEVELS, default='intermediate')
    points = models.IntegerField(default=1)
    time_limit = models.IntegerField(null=True, blank=True)  # in seconds
    
    # Ordering
    order = models.PositiveIntegerField(default=0)
    
    # Adaptive parameters
    discrimination_index = models.FloatField(default=0.0)  # Item discrimination
    difficulty_index = models.FloatField(default=0.0)  # Item difficulty (0-1)
    guessing_index = models.FloatField(default=0.0)  # Guessing parameter
    
    # Metadata
    tags = models.JSONField(default=list)
    learning_objectives = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quiz_questions'
        ordering = ['order']

    def __str__(self):
        return f"Question {self.order}: {self.question_text[:50]}..."


class AnswerOption(models.Model):
    """Answer options for multiple choice and similar questions"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answer_options')
    option_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    feedback = models.TextField(blank=True, null=True)
    
    # For matching questions
    matching_pair = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        db_table = 'quiz_answer_options'
        ordering = ['order']

    def __str__(self):
        return f"Option: {self.option_text[:30]}..."


class QuizAttempt(models.Model):
    """Individual quiz attempts by users"""
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('submitted', 'Submitted'),
        ('expired', 'Expired'),
        ('abandoned', 'Abandoned'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    
    # Attempt details
    attempt_number = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_taken = models.IntegerField(null=True, blank=True)  # in seconds
    
    # Scoring
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)
    percentage = models.FloatField(default=0.0)
    passed = models.BooleanField(default=False)
    
    # Adaptive data
    questions_askisted = models.ManyToManyField(Question, related_name='appeared_in_attempts')
    adaptive_path = models.JSONField(default=list)
    
    # Review data
    reviewed = models.BooleanField(default=False)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'quiz_attempts'
        unique_together = ['user', 'quiz', 'attempt_number']
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.email} - {self.quiz.title} (Attempt {self.attempt_number})"

    def calculate_score(self):
        """Calculate the total score for this attempt"""
        answers = self.answers.all()
        total_points = 0
        earned_points = 0
        
        for answer in answers:
            total_points += answer.question.points
            if answer.is_correct:
                earned_points += answer.question.points
        
        self.max_score = total_points
        self.score = earned_points
        if total_points > 0:
            self.percentage = (earned_points / total_points) * 100
        self.passed = self.percentage >= self.quiz.passing_score
        self.save()


class Answer(models.Model):
    """User answers to quiz questions"""
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    
    # Answer data
    selected_options = models.ManyToManyField(AnswerOption, blank=True)
    text_answer = models.TextField(blank=True, null=True)
    numeric_answer = models.FloatField(null=True, blank=True)
    
    # For coding questions
    code_answer = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=50, blank=True, null=True)
    
    # For ordering/matching
    ordered_items = models.JSONField(default=list)
    
    # Scoring
    is_correct = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    feedback = models.TextField(blank=True, null=True)
    
    # Timing
    time_spent = models.IntegerField(default=0)  # in seconds
    answered_at = models.DateTimeField(auto_now_add=True)
    
    # Review
    reviewed = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'quiz_answers'
        unique_together = ['attempt', 'question']

    def __str__(self):
        return f"Answer to {self.question.question_text[:30]}..."

    def check_answer(self):
        """Check if the answer is correct"""
        if self.question.question_type == 'multiple_choice':
            correct_options = set(self.question.answer_options.filter(is_correct=True))
            selected_options = set(self.selected_options.all())
            self.is_correct = correct_options == selected_options
            
        elif self.question.question_type == 'true_false':
            self.is_correct = self.text_answer.lower() in ['true', 't', 'yes', 'y']
            
        elif self.question.question_type == 'short_answer':
            # Simple text matching - can be enhancedd with with fuzzy matching
            correct_answers = self.question.answer_options.filter(is_correct=True)
            for correct in correct_answers:
                if self.text_answer.lower().strip() == correct.option_text.lower().strip():
                    self.is_correct = True
                    break
        
        self.score = self.question.points if self.is_correct else 0
        self.save()


class QuizTemplate(models.Model):
    """Reusable quiz templates"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    # Template structure
    question_templates = models.JSONField(default=list)
    settings = models.JSONField(default=dict)
    
    # Categories
    subject = models.CharField(max_length=100)
    difficulty_distribution = models.JSONField(default=dict)
    
    # Usage tracking
    usage_count = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='quiz_templates')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_templates')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quiz_templates'

    def __str__(self):
        return self.name


class QuizAnalytics(models.Model):
    """Analytics for quiz performance"""
    quiz = models.OneToOneField(Quiz, on_delete=models.CASCADE, related_name='analytics')
    
    # Participation metrics
    total_attempts = models.IntegerField(default=0)
    unique_participants = models.IntegerField(default=0)
    completion_rate = models.FloatField(default=0.0)
    
    # Performance metrics
    average_score = models.FloatField(default=0.0)
    average_time = models.FloatField(default=0.0)  # in minutes
    pass_rate = models.FloatField(default=0.0)
    
    # Question analytics
    question_difficulty = models.JSONField(default=dict)
    question_discrimination = models.JSONField(default=dict)
    
    # Time analytics
    peak_attempt_times = models.JSONField(default=list)
    average_time_per_question = models.JSONField(default=dict)
    
    # Improvement tracking
    score_distribution = models.JSONField(default=list)
    improvement_rate = models.FloatField(default=0.0)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quiz_analytics'

    def update_analytics(self):
        """Update quiz analytics based on all attempts"""
        attempts = self.quiz.attempts.filter(status='completed')
        
        if not attempts.exists():
            return
        
        # Basic metrics
        self.total_attempts = attempts.count()
        self.unique_participants = attempts.values('user').distinct().count()
        self.average_score = attempts.aggregate(avg_score=Avg('percentage'))['avg_score'] or 0
        self.pass_rate = attempts.filter(passed=True).count() / self.total_attempts * 100
        
        # Time metrics
        completed_attempts = attempts.exclude(time_taken__isnull=True)
        if completed_attempts.exists():
            self.average_time = completed_attempts.aggregate(avg_time=Avg('time_taken'))['avg_time'] / 60 or 0
        
        # Score distribution
        scores = list(attempts.values_list('percentage', flat=True))
        self.score_distribution = self._calculate_distribution(scores)
        
        self.save()

    def _calculate_distribution(self, scores):
        """Calculate score distribution buckets"""
        if not scores:
            return []
        
        buckets = [0, 0, 0, 0, 0]  # 0-20, 21-40, 41-60, 61-80, 81-100
        for score in scores:
            if score <= 20:
                buckets[0] += 1
            elif score <= 40:
                buckets[1] += 1
            elif score <= 60:
                buckets[2] += 1
            elif score <= 80:
                buckets[3] += 1
            else:
                buckets[4] += 1
        
        return buckets
