from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import json

User = get_user_model()


class AIModel(models.Model):
    """AI models for different recommendation and analysis tasks"""
    MODEL_TYPES = [
        ('recommendation', 'Course Recommendation'),
        ('content_analysis', 'Content Analysis'),
        ('learning_path', 'Learning Path Generation'),
        ('difficulty_assessment', 'Difficulty Assessment'),
        ('engagement_prediction', 'Engagement Prediction'),
        ('knowledge_gap', 'Knowledge Gap Analysis'),
        ('personalization', 'Content Personalization'),
    ]
    
    STATUS_CHOICES = [
        ('training', 'Training'),
        ('ready', 'Ready'),
        ('deployed', 'Deployed'),
        ('deprecated', 'Deprecated'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    model_type = models.CharField(max_length=30, choices=MODEL_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='training')
    
    # Model configuration
    algorithm = models.CharField(max_length=100)
    hyperparameters = models.JSONField(default=dict)
    features = models.JSONField(default=list)
    
    # Performance metrics
    accuracy = models.FloatField(null=True, blank=True)
    precision = models.FloatField(null=True, blank=True)
    recall = models.FloatField(null=True, blank=True)
    f1_score = models.FloatField(null=True, blank=True)
    
    # Deployment info
    version = models.CharField(max_length=20, default='1.0.0')
    model_file_path = models.CharField(max_length=500, blank=True, null=True)
    endpoint_url = models.URLField(blank=True, null=True)
    
    # Training data
    training_data_size = models.IntegerField(default=0)
    last_training_date = models.DateTimeField(null=True, blank=True)
    retraining_interval = models.IntegerField(default=7)  # days
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='ai_models')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_ai_models')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_models'

    def __str__(self):
        return f"{self.name} ({self.model_type})"


class UserProfileData(models.Model):
    """Comprehensive user profile data for AI analysis"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ai_profile')
    
    # Learning preferences
    preferred_content_types = models.JSONField(default=list)
    learning_style = models.CharField(max_length=50, blank=True, null=True)
    difficulty_preference = models.CharField(max_length=20, default='adaptive')
    session_duration_preference = models.IntegerField(default=30)  # minutes
    
    # Skill assessment
    technical_skills = models.JSONField(default=dict)  # {'python': 0.8, 'javascript': 0.6}
    soft_skills = models.JSONField(default=dict)
    subject_interests = models.JSONField(default=list)
    career_goals = models.JSONField(default=list)
    
    # Behavioral patterns
    peak_learning_hours = models.JSONField(default=list)  # [9, 10, 14, 15, 20]
    average_session_length = models.FloatField(default=0.0)
    preferred_device = models.CharField(max_length=20, default='desktop')
    
    # Engagement patterns
    content_engagement_scores = models.JSONField(default=dict)
    interaction_patterns = models.JSONField(default=dict)
    motivation_factors = models.JSONField(default=list)
    
    # AI-generated insights
    learning_velocity = models.FloatField(default=0.0)  # courses per month
    retention_score = models.FloatField(default=0.0)
    collaboration_score = models.FloatField(default=0.0)
    challenge_preference = models.FloatField(default=0.0)
    
    # Predictions
    dropout_risk = models.FloatField(default=0.0)
    success_probability = models.FloatField(default=0.0)
    optimal_course_difficulty = models.FloatField(default=0.5)
    
    last_analyzed = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profile_data'

    def __str__(self):
        return f"AI Profile for {self.user.email}"


class ContentAnalysis(models.Model):
    """AI analysis of course content"""
    course = models.OneToOneField('courses.Course', on_delete=models.CASCADE, related_name='ai_analysis')
    lesson = models.OneToOneField('courses.Lesson', on_delete=models.CASCADE, related_name='ai_analysis', null=True, blank=True)
    
    # Content characteristics
    difficulty_score = models.FloatField(default=0.5)
    complexity_score = models.FloatField(default=0.5)
    engagement_prediction = models.FloatField(default=0.5)
    
    # Topic modeling
    main_topics = models.JSONField(default=list)
    keywords = models.JSONField(default=list)
    concepts_covered = models.JSONField(default=list)
    prerequisites = models.JSONField(default=list)
    
    # Learning objectives
    learning_objectives = models.JSONField(default=list)
    skills_taained = models.JSONField(default=list)
    bloom_taxonomy_level = models.CharField(max_length=20, blank=True, null=True)
    
    # Content quality metrics
    clarity_score = models.FloatField(default=0.0)
    completeness_score = models.FloatField(default=0.0)
    engagement_score = models.FloatField(default=0.0)
    
    # Personalization data
    optimal_audience = models.JSONField(default=list)
    recommended_pacing = models.FloatField(default=1.0)
    supplementary_materials = models.JSONField(default=list)
    
    # Analysis metadata
    analysis_version = models.CharField(max_length=20, default='1.0')
    confidence_score = models.FloatField(default=0.0)
    analyzed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'content_analysis'

    def __str__(self):
        return f"Analysis for {self.course.title if self.course else self.lesson.title}"


class LearningPattern(models.Model):
    """Detected learning patterns for personalization"""
    PATTERN_TYPES = [
        ('temporal', 'Temporal Pattern'),
        ('content', 'Content Preference'),
        ('social', 'Social Learning'),
        ('performance', 'Performance Pattern'),
        ('engagement', 'Engagement Pattern'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_patterns')
    pattern_type = models.CharField(max_length=20, choices=PATTERN_TYPES)
    
    # Pattern data
    pattern_data = models.JSONField(default=dict)
    confidence = models.FloatField(default=0.0)
    frequency = models.FloatField(default=0.0)
    
    # Context
    context_data = models.JSONField(default=dict)
    related_courses = models.ManyToManyField('courses.Course', blank=True)
    
    # Effectiveness
    effectiveness_score = models.FloatField(default=0.0)
    last_observed = models.DateTimeField(auto_now=True)
    
    # Predictions
    next_occurrence_probability = models.FloatField(default=0.0)
    optimal_intervention = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learning_patterns'
        unique_together = ['user', 'pattern_type']

    def __str__(self):
        return f"{self.user.email} - {self.pattern_type} pattern"


class AIRecommendation(models.Model):
    """AI-powered recommendations"""
    RECOMMENDATION_TYPES = [
        ('course', 'Course Recommendation'),
        ('lesson', 'Lesson Recommendation'),
        ('learning_path', 'Learning Path'),
        ('study_method', 'Study Method'),
        ('time_management', 'Time Management'),
        ('collaboration', 'Collaboration Opportunity'),
        ('content_adjustment', 'Content Adjustment'),
        ('intervention', 'Learning Intervention'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_recommendations')
    recommendation_type = models.CharField(max_length=30, choices=RECOMMENDATION_TYPES)
    
    # Recommendation content
    title = models.CharField(max_length=255)
    description = models.TextField()
    action_items = models.JSONField(default=list)
    
    # Related objects
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, null=True, blank=True)
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE, null=True, blank=True)
    
    # Scoring and priority
    relevance_score = models.FloatField(default=0.0)
    confidence_score = models.FloatField(default=0.0)
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='medium')
    
    # Context and reasoning
    reasoning = models.TextField()
    context_data = models.JSONField(default=dict)
    supporting_evidence = models.JSONField(default=list)
    
    # Timing and expiration
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    optimal_timing = models.DateTimeField(null=True, blank=True)
    
    # User interaction
    is_viewed = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    
    viewed_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    dismissed_at = models.DateTimeField(null=True, blank=True)
    
    # Feedback
    user_feedback = models.IntegerField(null=True, blank=True)  # 1-5 rating
    feedback_comments = models.TextField(blank=True, null=True)
    
    # AI model info
    generated_by = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, blank=True)
    model_version = models.CharField(max_length=20, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_recommendations'
        ordering = ['-priority', '-relevance_score']

    def __str__(self):
        return f"Recommendation for {self.user.email}: {self.title}"


class KnowledgeGraph(models.Model):
    """Knowledge graph for content relationships"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Graph structure
    nodes = models.JSONField(default=list)  # [{'id': 'python_basics', 'type': 'concept', 'label': 'Python Basics'}]
    edges = models.JSONField(default=list)  # [{'source': 'python_basics', 'target': 'python_functions', 'type': 'prerequisite'}]
    
    # Metadata
    subject_area = models.CharField(max_length=100)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='knowledge_graphs')
    
    # Analysis data
    centrality_scores = models.JSONField(default=dict)
    clustering_coefficient = models.FloatField(default=0.0)
    graph_density = models.FloatField(default=0.0)
    
    # Version control
    version = models.CharField(max_length=20, default='1.0')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'knowledge_graphs'

    def __str__(self):
        return f"Knowledge Graph: {self.subject_area}"


class AdaptiveLearningPath(models.Model):
    """AI-generated adaptive learning paths"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adaptive_paths')
    base_path = models.ForeignKey('analytics.LearningPath', on_delete=models.CASCADE, null=True, blank=True)
    
    # Path customization
    customization_level = models.FloatField(default=0.0)  # 0.0 = standard, 1.0 = fully customized
    adaptation_reasons = models.JSONField(default=list)
    
    # Path structure
    course_sequence = models.JSONField(default=list)
    estimated_duration = models.IntegerField(default=0)  # hours
    difficulty_progression = models.JSONField(default=list)
    
    # Personalization factors
    learning_style_adaptations = models.JSONField(default=dict)
    pacing_adjustments = models.JSONField(default=dict)
    content_preferences = models.JSONField(default=dict)
    
    # Adaptation history
    adaptations_made = models.JSONField(default=list)
    performance_impact = models.JSONField(default=dict)
    
    # Status
    is_active = models.BooleanField(default=True)
    completion_percentage = models.FloatField(default=0.0)
    predicted_success_rate = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'adaptive_learning_paths'

    def __str__(self):
        return f"Adaptive Path for {self.user.email}"


class AIInsight(models.Model):
    """AI-generated insights for educators and administrators"""
    INSIGHT_TYPES = [
        ('student_performance', 'Student Performance'),
        ('course_effectiveness', 'Course Effectiveness'),
        ('engagement_pattern', 'Engagement Pattern'),
        ('dropout_prediction', 'Dropout Prediction'),
        ('content_gap', 'Content Gap Analysis'),
        ('skill_development', 'Skill Development'),
        ('learning_trend', 'Learning Trend'),
        ('intervention_opportunity', 'Intervention Opportunity'),
    ]
    
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_insights', null=True, blank=True)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='ai_insights', null=True, blank=True)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='ai_insights')
    
    insight_type = models.CharField(max_length=30, choices=INSIGHT_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Data and analysis
    confidence_score = models.FloatField(default=0.0)
    data_points = models.JSONField(default=list)
    analysis_method = models.CharField(max_length=100)
    
    # Recommendations
    recommendations = models.JSONField(default=list)
    action_items = models.JSONField(default=list)
    expected_outcome = models.TextField(blank=True, null=True)
    
    # Priority and urgency
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], default='medium')
    
    # Status
    is_read = models.BooleanField(default=False)
    is_actioned = models.BooleanField(default=False)
    
    read_at = models.DateTimeField(null=True, blank=True)
    actioned_at = models.DateTimeField(null=True, blank=True)
    
    # AI model info
    generated_by = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_insights'
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.insight_type})"


class PredictiveModel(models.Model):
    """Predictive models for various educational outcomes"""
    PREDICTION_TYPES = [
        ('dropout_risk', 'Dropout Risk'),
        ('course_success', 'Course Success'),
        ('optimal_difficulty', 'Optimal Difficulty'),
        ('engagement_level', 'Engagement Level'),
        ('completion_time', 'Completion Time'),
        ('skill_mastery', 'Skill Mastery'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predictions')
    prediction_type = models.CharField(max_length=30, choices=PREDICTION_TYPES)
    
    # Prediction data
    predicted_value = models.FloatField()
    confidence_interval = models.JSONField(default=dict)  # {'lower': 0.3, 'upper': 0.7}
    probability_distribution = models.JSONField(default=dict)
    
    # Context
    context_data = models.JSONField(default=dict)
    related_course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, null=True, blank=True)
    
    # Features importance
    feature_importance = models.JSONField(default=dict)
    key_factors = models.JSONField(default=list)
    
    # Model info
    model_version = models.CharField(max_length=20)
    prediction_date = models.DateTimeField(auto_now_add=True)
    
    # Validation
    actual_outcome = models.FloatField(null=True, blank=True)
    accuracy = models.FloatField(null=True, blank=True)
    
    class Meta:
        db_table = 'predictive_models'
        unique_together = ['user', 'prediction_type', 'prediction_date']

    def __str__(self):
        return f"{self.user.email} - {self.prediction_type}: {self.predicted_value}"
