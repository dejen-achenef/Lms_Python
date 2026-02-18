from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import json

User = get_user_model()


class EmotionSensor(models.Model):
    """Advanced emotion detection sensors"""
    SENSOR_TYPES = [
        ('facial_recognition', 'Facial Recognition Camera'),
        ('voice_analysis', 'Voice Analysis Microphone'),
        ('biometric', 'Biometric Wearables'),
        ('eye_tracking', 'Eye Tracking System'),
        ('galvanic_skin', 'Galvanic Skin Response'),
        ('heart_rate', 'Heart Rate Monitor'),
        ('eeg_emotion', 'EEG Emotion Detection'),
        ('thermal_camera', 'Thermal Imaging Camera'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('calibrating', 'Calibrating'),
        ('maintenance', 'Maintenance'),
        ('offline', 'Offline'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    sensor_type = models.CharField(max_length=30, choices=SENSOR_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    
    # Technical specifications
    sampling_rate = models.IntegerField(default=30)  # Hz
    accuracy = models.FloatField(default=0.0)  # 0.0 to 1.0
    latency = models.FloatField(default=0.0)  # milliseconds
    
    # Detection capabilities
    detectable_emotions = models.JSONField(default=list)
    emotion_intensity_range = models.JSONField(default=dict)
    
    # Connection details
    connection_protocol = models.CharField(max_length=20, default='USB')
    device_address = models.CharField(max_length=100, blank=True, null=True)
    
    # Calibration data
    calibration_coefficients = models.JSONField(default=dict)
    baseline_measurements = models.JSONField(default=dict)
    last_calibration = models.DateTimeField(null=True, blank=True)
    
    # Privacy settings
    data_encryption = models.BooleanField(default=True)
    anonymization_enabled = models.BooleanField(default=True)
    retention_period = models.IntegerField(default=30)  # days
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='emotion_sensors')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'emotion_sensors'
        indexes = [
            models.Index(fields=['sensor_type', 'status']),
            models.Index(fields=['accuracy']),
        ]

    def __str__(self):
        return f"Emotion Sensor: {self.name} ({self.sensor_type})"


class EmotionData(models.Model):
    """Raw and processed emotion data"""
    EMOTION_TYPES = [
        ('happiness', 'Happiness'),
        ('sadness', 'Sadness'),
        ('anger', 'Anger'),
        ('fear', 'Fear'),
        ('surprise', 'Surprise'),
        ('disgust', 'Disgust'),
        ('neutral', 'Neutral'),
        ('contempt', 'Contempt'),
        ('confusion', 'Confusion'),
        ('frustration', 'Frustration'),
        ('excitement', 'Excitement'),
        ('boredom', 'Boredom'),
        ('curiosity', 'Curiosity'),
        ('engagement', 'Engagement'),
        ('flow_state', 'Flow State'),
    ]
    
    DATA_SOURCES = [
        ('facial', 'Facial Expression'),
        ('vocal', 'Voice Analysis'),
        ('physiological', 'Physiological Signals'),
        ('behavioral', 'Behavioral Patterns'),
        ('textual', 'Text Analysis'),
        ('multimodal', 'Multimodal Fusion'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emotion_data')
    sensor = models.ForeignKey(EmotionSensor, on_delete=models.CASCADE, related_name='emotion_data')
    
    # Emotion measurements
    primary_emotion = models.CharField(max_length=30, choices=EMOTION_TYPES)
    emotion_intensity = models.FloatField(default=0.0)  # 0.0 to 1.0
    emotion_confidence = models.FloatField(default=0.0)  # 0.0 to 1.0
    
    # Emotion spectrum
    emotion_vector = models.JSONField(default=dict)  # All emotions with intensities
    valence = models.FloatField(default=0.0)  # -1.0 (negative) to 1.0 (positive)
    arousal = models.FloatField(default=0.0)  # 0.0 (calm) to 1.0 (excited)
    
    # Data source
    data_source = models.CharField(max_length=20, choices=DATA_SOURCES)
    raw_data = models.JSONField(default=dict)
    
    # Context
    learning_context = models.CharField(max_length=100, blank=True, null=True)
    current_activity = models.CharField(max_length=100, blank=True, null=True)
    difficulty_level = models.CharField(max_length=20, blank=True, null=True)
    
    # Environmental factors
    noise_level = models.FloatField(null=True, blank=True)
    lighting_conditions = models.CharField(max_length=50, blank=True, null=True)
    social_context = models.CharField(max_length=50, blank=True, null=True)
    
    # Physiological correlates
    heart_rate = models.IntegerField(null=True, blank=True)
    skin_conductance = models.FloatField(null=True, blank=True)
    pupil_dilation = models.FloatField(null=True, blank=True)
    
    # Temporal data
    timestamp = models.DateTimeField(auto_now_add=True)
    duration = models.FloatField(default=0.0)  # seconds
    
    # Quality metrics
    signal_quality = models.FloatField(default=0.0)
    noise_level = models.FloatField(default=0.0)
    
    class Meta:
        db_table = 'emotion_data'
        indexes = [
            models.Index(fields=['user', 'primary_emotion']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['data_source']),
        ]

    def __str__(self):
        return f"Emotion Data: {self.primary_emotion} for {self.user.email}"


class EmotionalProfile(models.Model):
    """Comprehensive emotional profile for personalization"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='emotional_profile')
    
    # Personality traits (Big Five)
    openness = models.FloatField(default=0.5)  # 0.0 to 1.0
    conscientiousness = models.FloatField(default=0.5)
    extraversion = models.FloatField(default=0.5)
    agreeableness = models.FloatField(default=0.5)
    neuroticism = models.FloatField(default=0.5)
    
    # Emotional intelligence
    self_awareness = models.FloatField(default=0.0)
    self_regulation = models.FloatField(default=0.0)
    motivation = models.FloatField(default=0.0)
    empathy = models.FloatField(default=0.0)
    social_skills = models.FloatField(default=0.0)
    
    # Learning preferences
    optimal_arousal_level = models.FloatField(default=0.7)
    stress_tolerance = models.FloatField(default=0.5)
    frustration_threshold = models.FloatField(default=0.5)
    
    # Emotional patterns
    typical_emotional_states = models.JSONField(default=dict)
    emotional_triggers = models.JSONField(default=list)
    coping_mechanisms = models.JSONField(default=list)
    
    # Motivational factors
    intrinsic_motivation = models.FloatField(default=0.5)
    extrinsic_motivation = models.FloatField(default=0.5)
    achievement_orientation = models.FloatField(default=0.5)
    
    # Social preferences
    social_learning_preference = models.FloatField(default=0.5)
    collaboration_style = models.CharField(max_length=50, default='balanced')
    feedback_sensitivity = models.FloatField(default=0.5)
    
    # Adaptability
    adaptability_score = models.FloatField(default=0.5)
    resilience_score = models.FloatField(default=0.5)
    
    # Privacy settings
    data_sharing_consent = models.BooleanField(default=True)
    emotion_tracking_enabled = models.BooleanField(default=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'emotional_profiles'

    def __str__(self):
        return f"Emotional Profile: {self.user.email}"


class AdaptiveLearningEngine(models.Model):
    """Emotion-aware adaptive learning engine"""
    ADAPTATION_STRATEGIES = [
        ('content_difficulty', 'Content Difficulty Adjustment'),
        ('presentation_style', 'Presentation Style Adaptation'),
        ('pacing', 'Learning Pacing Control'),
        ('motivation_boost', 'Motivation Enhancement'),
        ('stress_reduction', 'Stress Reduction'),
        ('engagement_optimization', 'Engagement Optimization'),
        ('social_adjustment', 'Social Learning Adjustment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adaptive_engines')
    
    # Current learning state
    current_emotional_state = models.CharField(max_length=30, blank=True, null=True)
    cognitive_load = models.FloatField(default=0.0)  # 0.0 to 1.0
    engagement_level = models.FloatField(default=0.0)
    motivation_level = models.FloatField(default=0.0)
    
    # Adaptation parameters
    adaptation_strategy = models.CharField(max_length=50, choices=ADAPTATION_STRATEGIES)
    adaptation_intensity = models.FloatField(default=0.0)
    adaptation_frequency = models.IntegerField(default=60)  # seconds
    
    # Learning optimization
    optimal_difficulty = models.FloatField(default=0.5)
    preferred_content_types = models.JSONField(default=list)
    optimal_session_length = models.IntegerField(default=45)  # minutes
    
    # Emotional regulation
    stress_intervention_threshold = models.FloatField(default=0.8)
    boredom_intervention_threshold = models.FloatField(default=0.3)
    frustration_intervention_threshold = models.FloatField(default=0.7)
    
    # Intervention history
    interventions_applied = models.JSONField(default=list)
    intervention_effectiveness = models.JSONField(default=dict)
    
    # Predictive models
    performance_prediction = models.FloatField(default=0.0)
    dropout_risk = models.FloatField(default=0.0)
    optimal_next_step = models.JSONField(default=dict)
    
    # Machine learning model
    model_version = models.CharField(max_length=20, default='v1.0')
    model_accuracy = models.FloatField(default=0.0)
    last_training = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'adaptive_learning_engines'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields(['adaptation_strategy']),
        ]

    def __str__(self):
        return f"Adaptive Engine: {self.user.email}"


class EmotionalIntervention(models.Model):
    """Automated emotional support interventions"""
    INTERVENTION_TYPES = [
        ('breathing_exercise', 'Breathing Exercise'),
        ('motivational_message', 'Motivational Message'),
        ('break_suggestion', 'Break Suggestion'),
        ('difficulty_adjustment', 'Difficulty Adjustment'),
        ('social_support', 'Social Support Offer'),
        ('gamification', 'Gamification Element'),
        ('music_therapy', 'Music Therapy'),
        ('mindfulness', 'Mindfulness Exercise'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emotional_interventions')
    
    # Intervention details
    intervention_type = models.CharField(max_length=30, choices=INTERVENTION_TYPES)
    trigger_emotion = models.CharField(max_length=30)
    trigger_intensity = models.FloatField(default=0.0)
    
    # Intervention content
    intervention_content = models.JSONField(default=dict)
    personalized_message = models.TextField(blank=True, null=True)
    
    # Delivery method
    delivery_channel = models.CharField(max_length=20, default='in_app')
    delivery_timing = models.CharField(max_length=20, default='immediate')
    
    # Effectiveness tracking
    user_response = models.CharField(max_length=20, blank=True, null=True)
    effectiveness_rating = models.IntegerField(null=True, blank=True)  # 1-5
    emotion_change = models.FloatField(default=0.0)
    
    # Timing
    triggered_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    # Context
    learning_context = models.CharField(max_length=100, blank=True, null=True)
    current_activity = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'emotional_interventions'
        indexes = [
            models.Index(fields=['user', 'intervention_type']),
            models.Index(fields(['triggered_at']),
        ]

    def __str__(self):
        return f"Emotional Intervention: {self.intervention_type} for {self.user.email}"


class EmotionAnalytics(models.Model):
    """Advanced emotion analytics and insights"""
    ANALYSIS_TYPES = [
        ('individual', 'Individual Analysis'),
        ('cohort', 'Cohort Analysis'),
        ('temporal', 'Temporal Analysis'),
        ('predictive', 'Predictive Analysis'),
        ('correlation', 'Correlation Analysis'),
        ('sentiment', 'Sentiment Analysis'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis_type = models.CharField(max_length=30, choices=ANALYSIS_TYPES)
    
    # Analysis scope
    target_users = models.ManyToManyField(User, related_name='emotion_analyses', blank=True)
    time_period_start = models.DateTimeField()
    time_period_end = models.DateTimeField()
    
    # Emotional patterns
    emotion_distributions = models.JSONField(default=dict)
    emotion_transitions = models.JSONField(default=dict)
    emotional_cycles = models.JSONField(default=list)
    
    # Learning correlations
    emotion_performance_correlation = models.JSONField(default=dict)
    engagement_emotion_mapping = models.JSONField(default=dict)
    retention_emotion_analysis = models.JSONField(default=dict)
    
    # Predictive insights
    success_predictors = models.JSONField(default.list)
    risk_indicators = models.JSONField(default.list)
    intervention_opportunities = models.JSONField(default.list)
    
    # Demographic breakdowns
    age_group_analysis = models.JSONField(default.dict)
    gender_analysis = models.JSONField(default.dict)
    cultural_analysis = models.JSONField(default.dict)
    
    # Recommendations
    personalization_recommendations = models.JSONField(default.list)
    content_optimization_suggestions = models.JSONField(default.list)
    engagement_strategies = models.JSONField(default.list)
    
    # Business insights
    learning_effectiveness_score = models.FloatField(default=0.0)
    user_satisfaction_prediction = models.FloatField(default=0.0)
    churn_risk_assessment = models.JSONField(default.dict)
    
    # Raw data summary
    data_points_analyzed = models.IntegerField(default=0)
    confidence_level = models.FloatField(default=0.0)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='emotion_analytics')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'emotion_analytics'
        indexes = [
            models.Index(fields=['analysis_type']),
            models.Index(fields(['time_period_start']),
        ]

    def __str__(self):
        return f"Emotion Analytics: {self.analysis_type}"


class EmotionalFeedback(models.Model):
    """Emotion-aware feedback system"""
    FEEDBACK_TYPES = [
        ('constructive', 'Constructive Feedback'),
        ('encouraging', 'Encouraging Feedback'),
        ('corrective', 'Corrective Feedback'),
        ('motivational', 'Motivational Feedback'),
        ('empathetic', 'Empathetic Feedback'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emotional_feedback')
    
    # Feedback context
    feedback_type = models.CharField(max_length=30, choices=FEEDBACK_TYPES)
    learning_activity = models.CharField(max_length=100)
    performance_metric = models.CharField(max_length=100, blank=True, null=True)
    
    # Emotional context
    user_emotion = models.CharField(max_length=30, blank=True, null=True)
    emotion_intensity = models.FloatField(default=0.0)
    emotional_state_assessment = models.JSONField(default.dict)
    
    # Feedback content
    feedback_message = models.TextField()
    tone = models.CharField(max_length=30, default='supportive')
    personalization_level = models.FloatField(default=0.0)
    
    # Delivery optimization
    optimal_timing = models.DateTimeField(null=True, blank=True)
    delivery_channel = models.CharField(max_length=20, default='in_app')
    presentation_style = models.JSONField(default.dict)
    
    # Effectiveness
    user_engagement = models.FloatField(default=0.0)
    emotional_response = models.CharField(max_length=30, blank=True, null=True)
    learning_impact = models.FloatField(default=0.0)
    
    # AI generation
    ai_generated = models.BooleanField(default=True)
    model_confidence = models.FloatField(default=0.0)
    human_reviewed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'emotional_feedback'
        indexes = [
            models.Index(fields=['user', 'feedback_type']),
            models.Index(fields(['created_at']),
        ]

    def __str__(self):
        return f"Emotional Feedback: {self.feedback_type} for {self.user.email}"


class SocialEmotionalLearning(models.Model):
    """Social-emotional learning competencies"""
    COMPETENCY_AREAS = [
        ('self_awareness', 'Self-Awareness'),
        ('self_management', 'Self-Management'),
        ('social_awareness', 'Social Awareness'),
        ('relationship_skills', 'Relationship Skills'),
        ('responsible_decision_making', 'Responsible Decision-Making'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sel_competencies')
    
    # Competency assessments
    self_awareness_score = models.FloatField(default=0.0)
    self_management_score = models.FloatField(default=0.0)
    social_awareness_score = models.FloatField(default=0.0)
    relationship_skills_score = models.FloatField(default=0.0)
    responsible_decision_making_score = models.FloatField(default=0.0)
    
    # Sub-competencies
    emotional_identification = models.FloatField(default=0.0)
    self_confidence = models.FloatField(default=0.0)
    stress_management = models.FloatField(default=0.0)
    impulse_control = models.FloatField(default=0.0)
    empathy = models.FloatField(default=0.0)
    perspective_taking = models.FloatField(default=0.0)
    communication = models.FloatField(default=0.0)
    teamwork = models.FloatField(default=0.0)
    ethical_responsibility = models.FloatField(default=0.0)
    goal_setting = models.FloatField(default=0.0)
    
    # Progress tracking
    baseline_scores = models.JSONField(default=dict)
    current_scores = models.JSONField(default.dict)
    growth_trajectory = models.JSONField(default.dict)
    
    # Learning activities
    completed_activities = models.JSONField(default.list)
    recommended_activities = models.JSONField(default.list)
    
    # Social interactions
    peer_feedback_scores = models.JSONField(default.dict)
    collaborative_project_scores = models.JSONField(default.dict)
    
    # Reflection and insights
    self_reflections = models.JSONField(default.list)
    insights_gained = models.JSONField(default.list)
    
    last_assessment = models.DateTimeField(null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'social_emotional_learning'

    def __str__(self):
        return f"SEL Competencies: {self.user.email}"
