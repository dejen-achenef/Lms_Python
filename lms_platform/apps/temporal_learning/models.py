from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import json

User = get_user_model()


class TimeMachine(models.Model):
    """Quantum time machine for temporal learning analytics"""
    TIME_MACHINE_TYPES = [
        ('quantum_entanglement', 'Quantum Entanglement Device'),
        ('wormhole_generator', 'Wormhole Generator'),
        ('closed_timelike_curve', 'Closed Timelike Curve'),
        ('tachyon_communication', 'Tachyon Communication'),
        ('parallel_universe', 'Parallel Universe Interface'),
        ('causality_loop', 'Causality Loop Generator'),
        ('temporal_displacement', 'Temporal Displacement Field'),
    ]
    
    STATUS_CHOICES = [
        ('online', 'Online'),
        ('calibrating', 'Calibrating'),
        ('stabilizing', 'Stabilizing'),
        ('maintenance', 'Maintenance'),
        ('offline', 'Offline'),
        ('temporal_anomaly', 'Temporal Anomaly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    time_machine_type = models.CharField(max_length=30, choices=TIME_MACHINE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    
    # Temporal capabilities
    max_temporal_range = models.FloatField(default=100.0)  # years
    temporal_resolution = models.FloatField(default=0.001)  # seconds
    parallel_timeline_access = models.IntegerField(default=10)
    
    # Energy requirements
    power_consumption = models.BigIntegerField(default=0)  # watts
    exotic_matter_required = models.FloatField(default=0.0)  # kilograms
    energy_efficiency = models.FloatField(default=0.0)  # 0.0 to 1.0
    
    # Safety parameters
    paradox_prevention = models.BooleanField(default=True)
    causality_protection = models.BooleanField(default=True)
    temporal_stability = models.FloatField(default=0.0)  # 0.0 to 1.0
    
    # Calibration data
    temporal_coordinates = models.JSONField(default.dict)
    timeline_integrity = models.FloatField(default=0.0)
    last_stabilization = models.DateTimeField(null=True, blank=True)
    
    # Learning applications
    educational_time_periods = models.JSONField(default.list)
    historical_events_access = models.JSONField(default.dict)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='time_machines')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'time_machines'
        indexes = [
            models.Index(fields=['time_machine_type', 'status']),
            models.Index(fields=['temporal_stability']),
        ]

    def __str__(self):
        return f"Time Machine: {self.name} ({self.time_machine_type})"


class TemporalLearningSession(models.Model):
    """Learning sessions across different time periods"""
    SESSION_TYPES = [
        ('historical_observation', 'Historical Observation'),
        ('future_preview', 'Future Preview'),
        ('parallel_comparison', 'Parallel Timeline Comparison'),
        ('causal_analysis', 'Causal Analysis'),
        ('alternative_outcomes', 'Alternative Outcomes'),
        ('skill_acquisition', 'Skill Acquisition from Future'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='temporal_learning_sessions')
    time_machine = models.ForeignKey(TimeMachine, on_delete=models.CASCADE, related_name='learning_sessions')
    
    # Temporal coordinates
    session_type = models.CharField(max_length=30, choices=SESSION_TYPES)
    target_time_period = models.JSONField(default.dict)  # {start_date, end_date, timeline_id}
    observation_point = models.DateTimeField()
    
    # Learning objectives
    learning_goals = models.JSONField(default.list)
    historical_context = models.TextField(blank=True, null=True)
    
    # Temporal parameters
    duration = models.FloatField(default=1.0)  # hours
    time_dilation_factor = models.FloatField(default=1.0)
    observer_invisibility = models.BooleanField(default=True)
    
    # Content accessed
    historical_lectures = models.JSONField(default.list)
    future_knowledge = models.JSONField(default.list)
    parallel_versions = models.JSONField(default.list)
    
    # Learning outcomes
    knowledge_gained = models.JSONField(default.dict)
    skills_acquired = models.JSONField(default.list)
    perspective_shifts = models.JSONField(default.list)
    
    # Temporal ethics
    prime_directive_compliance = models.BooleanField(default=True)
    timeline_integrity_maintained = models.BooleanField(default=True)
    paradox_avoided = models.BooleanField(default=True)
    
    # Experience quality
    temporal_coherence = models.FloatField(default=0.0)
    learning_effectiveness = models.FloatField(default=0.0)
    emotional_impact = models.FloatField(default=0.0)
    
    # Safety monitoring
    temporal_stress = models.FloatField(default=0.0)
    cognitive_dissonance = models.FloatField(default=0.0)
    reality_integration = models.FloatField(default=0.0)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'temporal_learning_sessions'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'session_type']),
            models.Index(fields(['observation_point']),
        ]

    def __str__(self):
        return f"Temporal Learning: {self.session_type} for {self.user.email}"


class HistoricalLearningData(models.Model):
    """Learning data collected from historical time periods"""
    DATA_TYPES = [
        ('lecture_recording', 'Historical Lecture Recording'),
        ('manuscript', 'Ancient Manuscript'),
        ('artifact', 'Historical Artifact'),
        ('conversation', 'Historical Conversation'),
        ('observation', 'Direct Observation'),
        ('experiment', 'Historical Experiment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    temporal_session = models.ForeignKey(TemporalLearningSession, on_delete=models.CASCADE, related_name='historical_data')
    
    # Data information
    data_type = models.CharField(max_length=30, choices=DATA_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Historical context
    time_period = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    historical_figures = models.JSONField(default.list)
    
    # Content data
    content_file = models.FileField(upload_to='historical_data/', null=True, blank=True)
    transcript = models.TextField(blank=True, null=True)
    translation = models.TextField(blank=True, null=True)
    
    # Educational value
    subject_areas = models.JSONField(default.list)
    learning_objectives = models.JSONField(default.list)
    difficulty_level = models.CharField(max_length=20, default='intermediate')
    
    # Authenticity verification
    authenticity_score = models.FloatField(default=0.0)
    verification_method = models.CharField(max_length=50, blank=True, null=True)
    temporal_signature = models.CharField(max_length=255, blank=True, null=True)
    
    # Cultural context
    cultural_significance = models.TextField(blank=True, null=True)
    linguistic_analysis = models.JSONField(default.dict)
    societal_impact = models.TextField(blank=True, null=True)
    
    # Metadata
    tags = models.JSONField(default.list)
    related_events = models.JSONField(default.list)
    
    collected_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'historical_learning_data'
        indexes = [
            models.Index(fields=['data_type', 'time_period']),
            models.Index(fields(['subject_areas']),
        ]

    def __str__(self):
        return f"Historical Data: {self.title} ({self.time_period})"


class FutureKnowledge(models.Model):
    """Knowledge acquired from future time periods"""
    KNOWLEDGE_TYPES = [
        ('scientific_discovery', 'Scientific Discovery'),
        ('technological_innovation', 'Technological Innovation'),
        ('social_development', 'Social Development'),
        ('educational_method', 'Educational Method'),
        ('skill_technique', 'Skill Technique'),
        ('problem_solution', 'Problem Solution'),
    ]
    
    CONFIDENCE_LEVELS = [
        ('certain', 'Certain'),
        ('highly_likely', 'Highly Likely'),
        ('likely', 'Likely'),
        ('possible', 'Possible'),
        ('uncertain', 'Uncertain'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    temporal_session = models.ForeignKey(TemporalLearningSession, on_delete=models.CASCADE, related_name='future_knowledge')
    
    # Knowledge details
    knowledge_type = models.CharField(max_length=30, choices=KNOWLEDGE_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Future context
    future_time_period = models.CharField(max_length=100)
    probability = models.FloatField(default=0.0)
    confidence_level = models.CharField(max_length=20, choices=CONFIDENCE_LEVELS)
    
    # Knowledge content
    knowledge_content = models.JSONField(default.dict)
    implementation_steps = models.JSONField(default.list)
    prerequisites = models.JSONField(default.list)
    
    # Applications
    current_applications = models.JSONField(default.list)
    potential_impact = models.JSONField(default.dict)
    ethical_considerations = models.JSONField(default.list)
    
    # Temporal consistency
    consistency_score = models.FloatField(default=0.0)
    paradox_risk = models.FloatField(default=0.0)
    causality_violation = models.BooleanField(default=False)
    
    # Learning integration
    integration_difficulty = models.FloatField(default=0.0)
    adaptation_required = models.JSONField(default.list)
    
    # Verification
    verification_timeline = models.JSONField(default.dict)
    validation_methods = models.JSONField(default.list)
    
    acquired_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'future_knowledge'
        indexes = [
            models.Index(fields=['knowledge_type', 'future_time_period']),
            models.Index(fields(['probability']),
        ]

    def __str__(self):
        return f"Future Knowledge: {self.title} ({self.future_time_period})"


class ParallelTimeline(models.Model):
    """Access to parallel universes and alternative timelines"""
    TIMELINE_TYPES = [
        ('divergent', 'Divergent Timeline'),
        ('parallel', 'Parallel Universe'),
        ('alternate', 'Alternate Reality'),
        ('mirror', 'Mirror Universe'),
        ('quantum_superposition', 'Quantum Superposition'),
        ('butterfly_effect', 'Butterfly Effect Timeline'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    timeline_type = models.CharField(max_length=30, choices=TIMELINE_TYPES)
    
    # Timeline characteristics
    divergence_point = models.DateTimeField()
    similarity_index = models.FloatField(default=0.0)  # 0.0 to 1.0 compared to prime timeline
    stability_factor = models.FloatField(default=0.0)
    
    # Access parameters
    access_difficulty = models.FloatField(default=0.0)
    energy_requirement = models.FloatField(default=0.0)
    temporal_distance = models.FloatField(default=0.0)
    
    # Learning opportunities
    unique_knowledge = models.JSONField(default.list)
    alternative_solutions = models.JSONField(default.list)
    different_perspectives = models.JSONField(default.list)
    
    # Risks and limitations
    paradox_potential = models.FloatField(default=0.0)
    contamination_risk = models.FloatField(default=0.0)
    observer_effect = models.FloatField(default=0.0)
    
    # Comparative analysis
    key_differences = models.JSONField(default.dict)
    similarities = models.JSONField(default.dict)
    learning_value = models.FloatField(default=0.0)
    
    # Access history
    access_count = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='parallel_timelines')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'parallel_timelines'
        indexes = [
            models.Index(fields=['timeline_type', 'similarity_index']),
            models.Index(fields(['divergence_point']),
        ]

    def __str__(self):
        return f"Parallel Timeline: {self.name} ({self.timeline_type})"


class CausalAnalytics(models.Model):
    """Advanced causal relationship analysis across time"""
    ANALYSIS_TYPES = [
        ('cause_effect', 'Cause and Effect'),
        ('butterfly_effect', 'Butterfly Effect Analysis'),
        ('feedback_loops', 'Feedback Loop Analysis'),
        ('causal_chains', 'Causal Chain Mapping'),
        ('intervention_impact', 'Intervention Impact'),
        ('counterfactual', 'Counterfactual Analysis'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis_type = models.CharField(max_length=30, choices=ANALYSIS_TYPES)
    
    # Analysis scope
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='causal_analytics', null=True, blank=True)
    time_period_start = models.DateTimeField()
    time_period_end = models.DateTimeField()
    timelines_analyzed = models.JSONField(default.list)
    
    # Causal relationships
    causal_graph = models.JSONField(default.dict)
    causal_strengths = models.JSONField(default.dict)
    temporal_delays = models.JSONField(default.dict)
    
    # Key insights
    root_causes = models.JSONField(default.list)
    critical_intervention_points = models.JSONField(default.list)
    leverage_points = models.JSONField(default.list)
    
    # Predictive capabilities
    outcome_predictions = models.JSONField(default.dict)
    intervention_outcomes = models.JSONField(default.dict)
    probability_distributions = models.JSONField(default.dict)
    
    # Learning implications
    learning_optimization_points = models.JSONField(default.list)
    personalization_insights = models.JSONField(default.dict)
    curriculum_recommendations = models.JSONField(default.list)
    
    # Confidence metrics
    analysis_confidence = models.FloatField(default=0.0)
    data_completeness = models.FloatField(default=0.0)
    model_accuracy = models.FloatField(default=0.0)
    
    # Ethical considerations
    ethical_implications = models.JSONField(default.list)
    privacy_concerns = models.JSONField(default.list)
    consent_requirements = models.JSONField(default.list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'causal_analytics'
        indexes = [
            models.Index(fields=['analysis_type']),
            models.Index(fields(['time_period_start']),
        ]

    def __str__(self):
        return f"Causal Analytics: {self.analysis_type}"


class TemporalEthics(models.Model):
    """Ethical framework for temporal learning activities"""
    ETHICAL_PRINCIPLES = [
        ('non_interference', 'Non-Interference Principle'),
        ('temporal_prime_directive', 'Temporal Prime Directive'),
        ('causality_preservation', 'Causality Preservation'),
        ('consent_respect', 'Consent Respect'),
        ('beneficence', 'Beneficence Principle'),
        ('justice', 'Justice Principle'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='temporal_ethics')
    
    # Ethical framework
    ethical_principles = models.JSONField(default=list)
    personal_ethics_score = models.FloatField(default=0.0)
    
    # Compliance tracking
    violations = models.JSONField(default.list)
    ethical_dilemmas = models.JSONField(default.list)
    resolutions = models.JSONField(default.list)
    
    # Consent management
    historical_consents = models.JSONField(default.dict)
    future_consents = models.JSONField(default.dict)
    parallel_consents = models.JSONField(default.dict)
    
    # Impact assessment
    positive_impacts = models.JSONField(default.list)
    negative_impacts = models.JSONField(default.list)
    unintended_consequences = models.JSONField(default.list)
    
    # Responsibility assignment
    accountability_level = models.FloatField(default=0.0)
    responsibility_scope = models.JSONField(default.dict)
    
    # Ethical training
    ethics_training_completed = models.BooleanField(default=False)
    last_ethics_review = models.DateTimeField(null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'temporal_ethics'

    def __str__(self):
        return f"Temporal Ethics: {self.user.email}"


class TemporalKnowledgeIntegration(models.Model):
    """Integration of temporal knowledge into current learning"""
    INTEGRATION_METHODS = [
        ('direct_incorporation', 'Direct Incorporation'),
        ('adaptation', 'Adaptation and Modification'),
        ('synthesis', 'Synthesis with Current Knowledge'),
        ('cautionary_approach', 'Cautionary Approach'),
        ('experimental', 'Experimental Application'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='temporal_integrations')
    
    # Knowledge sources
    historical_knowledge = models.ManyToManyField(HistoricalLearningData, related_name='integrations', blank=True)
    future_knowledge = models.ManyToManyField(FutureKnowledge, related_name='integrations', blank=True)
    parallel_insights = models.ManyToManyField(ParallelTimeline, related_name='integrations', blank=True)
    
    # Integration process
    integration_method = models.CharField(max_length=30, choices=INTEGRATION_METHODS)
    integration_complexity = models.FloatField(default=0.0)
    adaptation_required = models.JSONField(default.list)
    
    # Learning outcomes
    knowledge_synthesis = models.JSONField(default.dict)
    new_understandings = models.JSONField(default.list)
    skill_enhancements = models.JSONField(default.list)
    
    # Application results
    practical_applications = models.JSONField(default.list)
    problem_solving_improvements = models.JSONField(default.list)
    creativity_enhancements = models.JSONField(default.list)
    
    # Challenges faced
    integration_challenges = models.JSONField(default.list)
    conceptual_conflicts = models.JSONField(default.list)
    resolution_strategies = models.JSONField(default.list)
    
    # Long-term effects
    retention_rate = models.FloatField(default=0.0)
    transfer_applicability = models.FloatField(default=0.0)
    innovation_potential = models.FloatField(default=0.0)
    
    # Assessment
    integration_success = models.FloatField(default=0.0)
    educational_value = models.FloatField(default=0.0)
    ethical_compliance = models.FloatField(default=0.0)
    
    integration_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'temporal_knowledge_integration'
        indexes = [
            models.Index(fields=['user', 'integration_method']),
            models.Index(fields(['integration_date']),
        ]

    def __str__(self):
        return f"Temporal Integration: {self.user.email}"
