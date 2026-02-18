from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import json

User = get_user_model()


class TelepathyDevice(models.Model):
    """Advanced telepathic communication devices"""
    DEVICE_TYPES = [
        ('quantum_entanglement', 'Quantum Entanglement Interface'),
        ('neural_field_detector', 'Neural Field Detector'),
        ('consciousness_resonator', 'Consciousness Resonator'),
        ('psi_amplifier', 'Psi Amplifier'),
        ('brainwave_transmitter', 'Brainwave Transmitter'),
        ('thought_interface', 'Direct Thought Interface'),
        ('collective_consciousness', 'Collective Consciousness Hub'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('calibrating', 'Calibrating'),
        ('synchronizing', 'Synchronizing'),
        ('maintenance', 'Maintenance'),
        ('offline', 'Offline'),
        ('psi_overload', 'Psi Overload'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    device_type = models.CharField(max_length=30, choices=DEVICE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    
    # Telepathic capabilities
    thought_range = models.FloatField(default=100.0)  # meters
    bandwidth = models.FloatField(default=0.0)  # thoughts per second
    signal_strength = models.FloatField(default=0.0)  # 0.0 to 1.0
    
    # Neural interface
    eeg_sensitivity = models.FloatField(default=0.0)  # microvolts
    neural_frequency_range = models.JSONField(default.dict)  # Hz ranges
    thought_clarity = models.FloatField(default=0.0)  # 0.0 to 1.0
    
    # Quantum properties
    entanglement_pairs = models.IntegerField(default=0)
    coherence_time = models.FloatField(default=0.0)  # seconds
    quantum_fidelity = models.FloatField(default=0.0)
    
    # Power requirements
    psychic_energy_requirement = models.FloatField(default=0.0)
    battery_life = models.FloatField(default=0.0)  # hours
    charging_method = models.CharField(max_length=50, default='psychic')
    
    # Safety features
    thought_privacy = models.BooleanField(default=True)
    consent_required = models.BooleanField(default=True)
    psi_protection = models.BooleanField(default=True)
    
    # Calibration data
    user_brain_pattern = models.JSONField(default.dict)
    thought_signature = models.CharField(max_length=255, blank=True, null=True)
    last_calibration = models.DateTimeField(null=True, blank=True)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='telepathy_devices')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'telepathy_devices'
        indexes = [
            models.Index(fields=['device_type', 'status']),
            models.Index(fields=['thought_range']),
        ]

    def __str__(self):
        return f"Telepathy Device: {self.name} ({self.device_type})"


class ThoughtTransmission(models.Model):
    """Individual thought transmission records"""
    THOUGHT_TYPES = [
        ('concept', 'Abstract Concept'),
        ('image', 'Visual Image'),
        ('emotion', 'Emotion'),
        ('memory', 'Memory'),
        ('idea', 'Idea'),
        ('question', 'Question'),
        ('answer', 'Answer'),
        ('instruction', 'Instruction'),
    ]
    
    TRANSMISSION_STATUS = [
        ('transmitting', 'Transmitting'),
        ('received', 'Received'),
        ('understood', 'Understood'),
        ('corrupted', 'Corrupted'),
        ('blocked', 'Blocked'),
        ('reflected', 'Reflected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_thoughts')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_thoughts')
    device = models.ForeignKey(TelepathyDevice, on_delete=models.CASCADE, related_name='transmissions')
    
    # Thought content
    thought_type = models.CharField(max_length=20, choices=THOUGHT_TYPES)
    thought_content = models.JSONField(default.dict)
    raw_brainwaves = models.JSONField(default.dict)
    
    # Transmission properties
    signal_strength = models.FloatField(default=0.0)
    clarity = models.FloatField(default=0.0)  # 0.0 to 1.0
    emotional_intensity = models.FloatField(default=0.0)
    
    # Context
    learning_context = models.CharField(max_length=100, blank=True, null=True)
    subject_matter = models.CharField(max_length=100, blank=True, null=True)
    urgency_level = models.FloatField(default=0.0)
    
    # Transmission details
    transmission_distance = models.FloatField(default=0.0)  # meters
    transmission_time = models.FloatField(default=0.0)  # seconds
    bandwidth_used = models.FloatField(default=0.0)
    
    # Privacy and consent
    consent_given = models.BooleanField(default=True)
    encryption_enabled = models.BooleanField(default=True)
    anonymity_level = models.IntegerField(default=0)  # 0-5
    
    # Reception quality
    reception_quality = models.FloatField(default=0.0)
    understanding_level = models.FloatField(default=0.0)
    misinterpretation_risk = models.FloatField(default=0.0)
    
    # Status
    status = models.CharField(max_length=20, choices=TRANSMISSION_STATUS, default='transmitting')
    
    transmitted_at = models.DateTimeField(auto_now_add=True)
    received_at = models.DateTimeField(null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'thought_transmissions'
        ordering = ['-transmitted_at']
        indexes = [
            models.Index(fields=['sender', 'thought_type']),
            models.Index(fields(['receiver']),
            models.Index(fields(['status']),
        ]

    def __str__(self):
        return f"Thought: {self.thought_type} from {self.sender.email} to {self.receiver.email}"


class CollectiveConsciousness(models.Model):
    """Group consciousness for collaborative learning"""
    CONSCIOUSNESS_TYPES = [
        ('study_group', 'Study Group Consciousness'),
        ('classroom', 'Classroom Consciousness'),
        ('learning_community', 'Learning Community'),
        ('expert_network', 'Expert Network'),
        ('global_consciousness', 'Global Learning Consciousness'),
        ('species_consciousness', 'Species Learning Consciousness'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    consciousness_type = models.CharField(max_length=30, choices=CONSCIOUSNESS_TYPES)
    
    # Participants
    members = models.ManyToManyField(User, related_name='collective_consciousness', blank=True)
    facilitator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='facilitated_consciousness', null=True, blank=True)
    
    # Consciousness properties
    coherence_level = models.FloatField(default=0.0)  # 0.0 to 1.0
    synchronization_rate = models.FloatField(default=0.0)
    collective_intelligence = models.FloatField(default=0.0)
    
    # Knowledge sharing
    shared_knowledge = models.JSONField(default.dict)
    collective_memory = models.JSONField(default.dict)
    group_insights = models.JSONField(default.list)
    
    # Learning dynamics
    learning_acceleration = models.FloatField(default=0.0)
    knowledge_synthesis = models.FloatField(default=0.0)
    collaborative_solutions = models.JSONField(default.list)
    
    # Emotional climate
    collective_emotion = models.CharField(max_length=30, blank=True, null=True)
    emotional_harmony = models.FloatField(default=0.0)
    group_motivation = models.FloatField(default=0.0)
    
    # Communication patterns
    thought_flow_patterns = models.JSONField(default.dict)
    information_hierarchy = models.JSONField(default.dict)
    emergent_leadership = models.JSONField(default.list)
    
    # Performance metrics
    problem_solving_speed = models.FloatField(default=0.0)
    creativity_level = models.FloatField(default=0.0)
    innovation_rate = models.FloatField(default=0.0)
    
    # Safety and ethics
    privacy_controls = models.JSONField(default.dict)
    consent_framework = models.JSONField(default.dict)
    ethical_guidelines = models.JSONField(default.list)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'collective_consciousness'
        indexes = [
            models.Index(fields=['consciousness_type', 'is_active']),
            models.Index(fields(['coherence_level']),
        ]

    def __str__(self):
        return f"Collective Consciousness: {self.name}"


class PsiAbility(models.Model):
    """Individual psychic abilities for learning"""
    ABILITY_TYPES = [
        ('telepathy', 'Telepathy'),
        ('clairvoyance', 'Clairvoyance'),
        ('precognition', 'Precognition'),
        ('psychometry', 'Psychometry'),
        ('intuition', 'Enhanced Intuition'),
        ('empathy', 'Deep Empathy'),
        ('remote_viewing', 'Remote Viewing'),
        ('thought_implantation', 'Thought Implantation'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='psi_ability')
    
    # Ability profiles
    primary_ability = models.CharField(max_length=30, choices=ABILITY_TYPES)
    secondary_abilities = models.JSONField(default.list)
    
    # Ability metrics
    power_level = models.FloatField(default=0.0)  # 0.0 to 10.0
    control_level = models.FloatField(default=0.0)  # 0.0 to 1.0
    accuracy_rate = models.FloatField(default=0.0)  # 0.0 to 1.0
    
    # Learning applications
    knowledge_absorption_rate = models.FloatField(default=0.0)
    concept_understanding_speed = models.FloatField(default=0.0)
    memory_recall_accuracy = models.FloatField(default=0.0)
    
    # Development tracking
    training_hours = models.FloatField(default=0.0)
    ability_progression = models.JSONField(default.dict)
    breakthrough_moments = models.JSONField(default.list)
    
    # Limitations and challenges
    mental_fatigue_threshold = models.FloatField(default=0.0)
    psi_overload_symptoms = models.JSONField(default.list)
    recovery_time = models.FloatField(default=0.0)  # hours
    
    # Enhancement methods
    meditation_techniques = models.JSONField(default.list)
    focusing_exercises = models.JSONField(default.list)
    energy_management = models.JSONField(default.dict)
    
    # Ethical considerations
    ethical_usage_score = models.FloatField(default=0.0)
    consent_violations = models.IntegerField(default=0)
    responsible_usage = models.BooleanField(default=True)
    
    # Social impact
    group_contribution = models.FloatField(default=0.0)
    mentorship_activities = models.JSONField(default.list)
    community_service = models.JSONField(default.list)
    
    last_assessment = models.DateTimeField(null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'psi_abilities'

    def __str__(self):
        return f"Psi Ability: {self.primary_ability} for {self.user.email}"


class MentalSynchronization(models.Model):
    """Mental synchronization between learners"""
    SYNCHRONIZATION_TYPES = [
        ('brainwave_sync', 'Brainwave Synchronization'),
        ('thought_pattern', 'Thought Pattern Matching'),
        ('emotional_resonance', 'Emotional Resonance'),
        ('cognitive_alignment', 'Cognitive Alignment'),
        ('learning_rhythm', 'Learning Rhythm Sync'),
        ('collective_focus', 'Collective Focus'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name='synchronization_sessions')
    synchronization_type = models.CharField(max_length=30, choices=SYNCHRONIZATION_TYPES)
    
    # Synchronization metrics
    sync_level = models.FloatField(default=0.0)  # 0.0 to 1.0
    harmony_index = models.FloatField(default=0.0)
    coherence_duration = models.FloatField(default=0.0)  # minutes
    
    # Learning benefits
    knowledge_transfer_rate = models.FloatField(default=0.0)
    mutual_understanding = models.FloatField(default=0.0)
    collaborative_insight = models.FloatField(default=0.0)
    
    # Neural patterns
    shared_frequencies = models.JSONField(default.list)
    phase_locking_value = models.FloatField(default=0.0)
    cross_correlation = models.JSONField(default.dict)
    
    # Session dynamics
    session_duration = models.FloatField(default=0.0)  # minutes
    peak_performance_periods = models.JSONField(default.list)
    synchronization_events = models.JSONField(default.list)
    
    # Outcomes
    learning_acceleration = models.FloatField(default=0.0)
    problem_solving_improvement = models.FloatField(default=0.0)
    creativity_enhancement = models.FloatField(default=0.0)
    
    # Side effects
    mental_fatigue = models.FloatField(default=0.0)
    identity_blending_risk = models.FloatField(default=0.0)
    recovery_requirement = models.FloatField(default=0.0)  # hours
    
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'mental_synchronization'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['synchronization_type']),
            models.Index(fields(['sync_level']),
        ]

    def __str__(self):
        return f"Mental Sync: {self.synchronization_type}"


class ThoughtImplantation(models.Model):
    """Direct thought implantation for rapid learning"""
    IMPLANTATION_TYPES = [
        ('skill', 'Skill Implantation'),
        ('knowledge', 'Knowledge Transfer'),
        ('language', 'Language Acquisition'),
        ('mathematical', 'Mathematical Intuition'),
        ('musical', 'Musical Ability'),
        ('athletic', 'Athletic Technique'),
        ('artistic', 'Artistic Vision'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='thought_implantations')
    implantation_type = models.CharField(max_length=30, choices=IMPLANTATION_TYPES)
    
    # Source information
    source_expert = models.ForeignKey(User, on_delete=models.CASCADE, related_name='implanted_knowledge', null=True, blank=True)
    knowledge_domain = models.CharField(max_length=100)
    expertise_level = models.FloatField(default=0.0)  # 0.0 to 1.0
    
    # Implantation process
    implantation_method = models.CharField(max_length=50, default='telepathic_transfer')
    neural_pathways = models.JSONField(default.list)
    synaptic_connections = models.IntegerField(default=0)
    
    # Content structure
    thought_patterns = models.JSONField(default.dict)
    neural_networks = models.JSONField(default.dict)
    memory_anchors = models.JSONField(default.list)
    
    # Integration process
    integration_time = models.FloatField(default=0.0)  # hours
    assimilation_rate = models.FloatField(default=0.0)
    neural_adaptation = models.FloatField(default=0.0)
    
    # Learning outcomes
    immediate_comprehension = models.FloatField(default=0.0)
    practical_application = models.FloatField(default=0.0)
    retention_rate = models.FloatField(default=0.0)
    
    # Side effects and risks
    identity_confusion_risk = models.FloatField(default=0.0)
    memory_interference = models.JSONField(default.list)
    psychological_impact = models.JSONField(default.dict)
    
    # Ethical considerations
    informed_consent = models.BooleanField(default=True)
    reversibility = models.BooleanField(default=False)
    long_term_effects = models.JSONField(default.list)
    
    # Quality control
    implantation_success = models.FloatField(default=0.0)
    purity_of_transfer = models.FloatField(default=0.0)
    contamination_risk = models.FloatField(default=0.0)
    
    implanted_at = models.DateTimeField(auto_now_add=True)
    fully_integrated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'thought_implantations'
        indexes = [
            models.Index(fields=['recipient', 'implantation_type']),
            models.Index(fields(['implanted_at']),
        ]

    def __str__(self):
        return f"Thought Implantation: {self.implantation_type} for {self.recipient.email}"


class PrecognitiveLearning(models.Model):
    """Using precognition for optimal learning paths"""
    PRECOGNITION_TYPES = [
        ('learning_outcome', 'Learning Outcome Prediction'),
        ('optimal_timing', 'Optimal Learning Timing'),
        ('difficulty_forecast', 'Difficulty Forecasting'),
        ('success_probability', 'Success Probability'),
        ('obstacle_prediction', 'Obstacle Prediction'),
        ('resource_needs', 'Resource Needs Prediction'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='precognitive_learning')
    precognition_type = models.CharField(max_length=30, choices=PRECOGNITION_TYPES)
    
    # Prediction details
    prediction_content = models.JSONField(default.dict)
    confidence_level = models.FloatField(default=0.0)  # 0.0 to 1.0
    time_horizon = models.FloatField(default=0.0)  # days
    
    # Learning context
    learning_subject = models.CharField(max_length=100)
    current_level = models.FloatField(default=0.0)
    target_level = models.FloatField(default=0.0)
    
    # Predicted outcomes
    optimal_study_duration = models.FloatField(default=0.0)  # hours
    best_learning_method = models.CharField(max_length=50, blank=True, null=True)
    predicted_difficulty = models.FloatField(default=0.0)
    
    # Intervention points
    critical_learning_moments = models.JSONField(default.list)
    optimal_break_times = models.JSONField(default.list)
    challenge_points = models.JSONField(default.list)
    
    # Resource predictions
    required_materials = models.JSONField(default.list)
    optimal_tutor_match = models.CharField(max_length=255, blank=True, null=True)
    study_group_recommendations = models.JSONField(default.list)
    
    # Accuracy tracking
    prediction_accuracy = models.FloatField(default=0.0)
    actual_outcomes = models.JSONField(default.dict)
    calibration_adjustments = models.JSONField(default.list)
    
    # Ethical considerations
    free_will_preservation = models.BooleanField(default=True)
    deterministic_warnings = models.JSONField(default.list)
    user_autonomy = models.BooleanField(default=True)
    
    # Vision mechanics
    vision_method = models.CharField(max_length=50, default='meditative')
    vision_clarity = models.FloatField(default=0.0)
    symbolic_interpretation = models.JSONField(default.dict)
    
    predicted_at = models.DateTimeField(auto_now_add=True)
    validated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'precognitive_learning'
        indexes = [
            models.Index(fields=['user', 'precognition_type']),
            models.Index(fields(['confidence_level']),
        ]

    def __str__(self):
        return f"Precognitive Learning: {self.precognition_type} for {self.user.email}"
