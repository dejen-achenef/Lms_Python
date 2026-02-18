from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import json

User = get_user_model()


class NeuralDevice(models.Model):
    """Neural interface devices for direct brain-computer interaction"""
    DEVICE_TYPES = [
        ('eeg_headset', 'EEG Headset'),
        ('brain implant', 'Brain Implant'),
        ('neural_lace', 'Neural Lace'),
        ('optogenetic', 'Optogenetic Interface'),
        ('ultrasonic', 'Ultrasonic Neural Interface'),
        ('magnetic', 'Magnetic Neural Stimulation'),
        ('quantum_neural', 'Quantum Neural Interface'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('calibrating', 'Calibrating'),
        ('maintenance', 'Maintenance'),
        ('offline', 'Offline'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='neural_devices')
    device_type = models.CharField(max_length=30, choices=DEVICE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    
    # Device specifications
    electrode_count = models.IntegerField(default=0)
    sampling_rate = models.IntegerField(default=0)  # Hz
    signal_resolution = models.FloatField(default=0.0)  # bits
    
    # Brain regions monitored
    monitored_regions = models.JSONField(default=list)  # Frontal, parietal, temporal, occipital
    stimulation_regions = models.JSONField(default=list)
    
    # Connection details
    bluetooth_address = models.CharField(max_length=50, blank=True, null=True)
    neural_protocol = models.CharField(max_length=20, default='BCI_v2.0')
    
    # Calibration data
    baseline_patterns = models.JSONField(default=dict)
    personal_frequencies = models.JSONField(default=dict)
    
    # Safety parameters
    max_stimulation_amplitude = models.FloatField(default=0.0)  # μA
    safety_limits = models.JSONField(default=dict)
    
    # Performance metrics
    signal_quality = models.FloatField(default=0.0)  # 0.0 to 1.0
    latency = models.FloatField(default=0.0)  # milliseconds
    
    last_sync = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'neural_devices'
        indexes = [
            models.Index(fields=['user', 'device_type']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Neural Device: {self.device_type} for {self.user.email}"


class BrainWavePattern(models.Model):
    """Brain wave patterns for learning states"""
    WAVE_TYPES = [
        ('delta', 'Delta Waves (0.5-4 Hz)'),
        ('theta', 'Theta Waves (4-8 Hz)'),
        ('alpha', 'Alpha Waves (8-13 Hz)'),
        ('beta', 'Beta Waves (13-30 Hz)'),
        ('gamma', 'Gamma Waves (30-100 Hz)'),
        ('high_gamma', 'High Gamma (>100 Hz)'),
    ]
    
    LEARNING_STATES = [
        ('focused', 'Focused Attention'),
        ('relaxed', 'Relaxed Learning'),
        ('creative', 'Creative Thinking'),
        ('meditative', 'Meditative State'),
        ('problem_solving', 'Problem Solving'),
        ('memory_consolidation', 'Memory Consolidation'),
        ('flow_state', 'Flow State'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='brain_wave_patterns')
    device = models.ForeignKey(NeuralDevice, on_delete=models.CASCADE, related_name='wave_patterns')
    
    # Pattern data
    wave_type = models.CharField(max_length=20, choices=WAVE_TYPES)
    learning_state = models.CharField(max_length=30, choices=LEARNING_STATES)
    
    # Frequency characteristics
    dominant_frequency = models.FloatField(default=0.0)  # Hz
    frequency_spectrum = models.JSONField(default=dict)
    amplitude = models.FloatField(default=0.0)  # μV
    
    # Spatial information
    brain_regions = models.JSONField(default=list)
    coherence_map = models.JSONField(default=dict)
    
    # Temporal dynamics
    pattern_duration = models.FloatField(default=0.0)  # seconds
    onset_time = models.DateTimeField()
    offset_time = models.DateTimeField(null=True, blank=True)
    
    # Learning correlation
    learning_effectiveness = models.FloatField(default=0.0)
    information_retention = models.FloatField(default=0.0)
    
    # Context
    current_activity = models.CharField(max_length=100, blank=True, null=True)
    environmental_factors = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'brain_wave_patterns'
        indexes = [
            models.Index(fields=['user', 'wave_type']),
            models.Index(fields=['learning_state']),
            models.Index(fields=['onset_time']),
        ]

    def __str__(self):
        return f"Brain Pattern: {self.wave_type} - {self.learning_state}"


class NeuralLearningSession(models.Model):
    """Direct neural learning sessions"""
    SESSION_TYPES = [
        ('knowledge_upload', 'Knowledge Upload'),
        ('skill_download', 'Skill Download'),
        ('memory_consolidation', 'Memory Consolidation'),
        ('cognitive_enhancement', 'Cognitive Enhancement'),
        ('language_acquisition', 'Language Acquisition'),
        ('mathematical_intuition', 'Mathematical Intuition'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='neural_learning_sessions')
    device = models.ForeignKey(NeuralDevice, on_delete=models.CASCADE, related_name='learning_sessions')
    
    # Session configuration
    session_type = models.CharField(max_length=30, choices=SESSION_TYPES)
    target_knowledge = models.JSONField(default=dict)
    
    # Neural stimulation parameters
    stimulation_protocol = models.JSONField(default=dict)
    stimulation_intensity = models.FloatField(default=0.0)
    stimulation_pattern = models.JSONField(default=list)
    
    # Learning metrics
    knowledge_transfer_rate = models.FloatField(default=0.0)  # bits/second
    comprehension_level = models.FloatField(default=0.0)  # 0.0 to 1.0
    retention_score = models.FloatField(default=0.0)  # 0.0 to 1.0
    
    # Brain activity
    neural_activity_map = models.JSONField(default=dict)
    plasticity_indicators = models.JSONField(default=dict)
    
    # Session timing
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    optimal_duration = models.FloatField(default=0.0)  # minutes
    
    # Outcomes
    learning_outcomes = models.JSONField(default=dict)
    side_effects = models.JSONField(default=list)
    
    # Feedback
    user_feedback = models.IntegerField(null=True, blank=True)  # 1-10 rating
    subjective_experience = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'neural_learning_sessions'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'session_type']),
            models.Index(fields=['started_at']),
        ]

    def __str__(self):
        return f"Neural Learning: {self.session_type} for {self.user.email}"


class CognitiveEnhancement(models.Model):
    """AI-powered cognitive enhancement through neural interface"""
    ENHANCEMENT_TYPES = [
        ('memory', 'Memory Enhancement'),
        ('attention', 'Attention Enhancement'),
        ('creativity', 'Creativity Boost'),
        ('problem_solving', 'Problem Solving Skills'),
        ('learning_speed', 'Learning Speed'),
        ('emotional_intelligence', 'Emotional Intelligence'),
        ('intuition', 'Intuitive Capabilities'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cognitive_enhancements')
    
    # Enhancement parameters
    enhancement_type = models.CharField(max_length=30, choices=ENHANCEMENT_TYPES)
    target_cognitive_function = models.CharField(max_length=100)
    
    # Neural protocols
    stimulation_protocol = models.JSONField(default=dict)
    neurofeedback_parameters = models.JSONField(default=dict)
    
    # Enhancement metrics
    baseline_performance = models.FloatField(default=0.0)
    enhanced_performance = models.FloatField(default=0.0)
    improvement_percentage = models.FloatField(default=0.0)
    
    # Duration and persistence
    enhancement_duration = models.FloatField(default=0.0)  # hours
    decay_rate = models.FloatField(default=0.0)  # per hour
    
    # Safety monitoring
    neural_fatigue = models.FloatField(default=0.0)
    stress_indicators = models.JSONField(default=dict)
    safety_score = models.FloatField(default=1.0)  # 0.0 to 1.0
    
    # Personalization
    optimal_stimulation_pattern = models.JSONField(default=dict)
    individual_response_profile = models.JSONField(default=dict)
    
    started_at = models.DateTimeField(auto_now_add=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'cognitive_enhancements'
        indexes = [
            models.Index(fields=['user', 'enhancement_type']),
            models.Index(fields=['started_at']),
        ]

    def __str__(self):
        return f"Cognitive Enhancement: {self.enhancement_type} for {self.user.email}"


class NeuralData(models.Model):
    """Raw and processed neural data"""
    DATA_TYPES = [
        ('raw_eeg', 'Raw EEG Data'),
        ('processed_signals', 'Processed Signals'),
        ('spike_trains', 'Neural Spike Trains'),
        ('local_field_potentials', 'Local Field Potentials'),
        ('calcium_imaging', 'Calcium Imaging Data'),
        ('fmri_data', 'fMRI Data'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='neural_data')
    device = models.ForeignKey(NeuralDevice, on_delete=models.CASCADE, related_name='neural_data')
    
    # Data information
    data_type = models.CharField(max_length=30, choices=DATA_TYPES)
    data_format = models.CharField(max_length=20, default='binary')
    
    # Storage
    data_file = models.FileField(upload_to='neural_data/')
    compressed_size = models.BigIntegerField(default=0)  # bytes
    uncompressed_size = models.BigIntegerField(default=0)  # bytes
    
    # Metadata
    sampling_rate = models.IntegerField(default=0)
    channel_count = models.IntegerField(default=0)
    recording_duration = models.FloatField(default=0.0)  # seconds
    
    # Quality metrics
    signal_to_noise_ratio = models.FloatField(default=0.0)
    artifact_removal_applied = models.BooleanField(default=False)
    
    # Processing
    preprocessing_steps = models.JSONField(default=list)
    feature_extraction = models.JSONField(default=dict)
    
    # Privacy and security
    encryption_enabled = models.BooleanField(default=True)
    anonymization_level = models.IntegerField(default=1)  # 1-5
    
    recorded_at = models.DateTimeField()
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'neural_data'
        indexes = [
            models.Index(fields=['user', 'data_type']),
            models.Index(fields=['recorded_at']),
        ]

    def __str__(self):
        return f"Neural Data: {self.data_type} for {self.user.email}"


class NeuralFeedback(models.Model):
    """Real-time neurofeedback for learning optimization"""
    FEEDBACK_TYPES = [
        ('visual', 'Visual Feedback'),
        ('auditory', 'Auditory Feedback'),
        ('haptic', 'Haptic Feedback'),
        ('direct_stimulation', 'Direct Neural Stimulation'),
        ('emotional', 'Emotional Feedback'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='neural_feedback')
    device = models.ForeignKey(NeuralDevice, on_delete=models.CASCADE, related_name='feedback_sessions')
    
    # Feedback configuration
    feedback_type = models.CharField(max_length=30, choices=FEEDBACK_TYPES)
    target_brain_state = models.CharField(max_length=100)
    
    # Feedback parameters
    feedback_intensity = models.FloatField(default=0.0)
    feedback_frequency = models.FloatField(default=0.0)  # Hz
    adaptation_rate = models.FloatField(default=0.0)
    
    # Learning optimization
    optimal_learning_window = models.JSONField(default=dict)
    attention_level = models.FloatField(default=0.0)
    engagement_score = models.FloatField(default=0.0)
    
    # Real-time metrics
    current_brain_state = models.JSONField(default=dict)
    state_stability = models.FloatField(default=0.0)
    transition_smoothness = models.FloatField(default=0.0)
    
    # Effectiveness
    learning_acceleration = models.FloatField(default=0.0)
    retention_improvement = models.FloatField(default=0.0)
    
    # Session data
    session_start = models.DateTimeField(auto_now_add=True)
    session_end = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'neural_feedback'
        indexes = [
            models.Index(fields=['user', 'feedback_type']),
            models.Index(fields=['session_start']),
        ]

    def __str__(self):
        return f"Neural Feedback: {self.feedback_type} for {self.user.email}"


class ConsciousnessSimulation(models.Model):
    """Advanced consciousness simulation for metacognitive learning"""
    CONSCIOUSNESS_LEVELS = [
        ('basic_awareness', 'Basic Awareness'),
        ('self_awareness', 'Self-Awareness'),
        ('metacognition', 'Metacognition'),
        ('transcendent', 'Transcendent Consciousness'),
        ('collective', 'Collective Consciousness'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consciousness_simulations')
    
    # Consciousness parameters
    consciousness_level = models.CharField(max_length=30, choices=CONSCIOUSNESS_LEVELS)
    integration_complexity = models.FloatField(default=0.0)  # Tononi's Phi
    information_content = models.FloatField(default=0.0)  # bits
    
    # Neural correlates
    neural_correlates = models.JSONField(default=dict)
    global_workspace_activity = models.JSONField(default=dict)
    
    # Metacognitive abilities
    self_monitoring = models.FloatField(default=0.0)
    meta_learning = models.FloatField(default=0.0)
    introspective_depth = models.FloatField(default=0.0)
    
    # Learning insights
    learning_insights = models.JSONField(default=list)
    aha_moments = models.JSONField(default=list)
    creative_breakthroughs = models.JSONField(default=list)
    
    # Subjective experience
    subjective_quality = models.TextField(blank=True, null=True)
    emotional_state = models.JSONField(default=dict)
    
    # Simulation parameters
    simulation_accuracy = models.FloatField(default=0.0)
    prediction_confidence = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'consciousness_simulations'
        indexes = [
            models.Index(fields=['user', 'consciousness_level']),
            models.Index(fields=['integration_complexity']),
        ]

    def __str__(self):
        return f"Consciousness Simulation: {self.consciousness_level} for {self.user.email}"


class NeuralNetwork(models.Model):
    """Artificial neural networks that interface with biological neural systems"""
    NETWORK_TYPES = [
        ('spiking_nn', 'Spiking Neural Network'),
        ('liquid_state', 'Liquid State Machine'),
        ('echo_state', 'Echo State Network'),
        ('neuromorphic', 'Neuromorphic Network'),
        ('hybrid_bio_digital', 'Hybrid Bio-Digital Network'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    network_type = models.CharField(max_length=30, choices=NETWORK_TYPES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='neural_networks')
    
    # Network architecture
    neuron_count = models.IntegerField(default=0)
    synapse_count = models.IntegerField(default=0)
    network_depth = models.IntegerField(default=0)
    
    # Biological integration
    biological_interface_points = models.JSONField(default=list)
    synaptic_plasticity_rules = models.JSONField(default=dict)
    
    # Learning capabilities
    learning_rate = models.FloatField(default=0.0)
    adaptation_speed = models.FloatField(default=0.0)
    memory_capacity = models.FloatField(default=0.0)
    
    # Performance metrics
    processing_speed = models.FloatField(default=0.0)  # operations/second
    energy_efficiency = models.FloatField(default=0.0)  # operations/joule
    accuracy = models.FloatField(default=0.0)
    
    # Applications
    learning_applications = models.JSONField(default=list)
    cognitive_tasks = models.JSONField(default=list)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_training = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'neural_networks'
        indexes = [
            models.Index(fields=['user', 'network_type']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"Neural Network: {self.name} ({self.network_type})"
