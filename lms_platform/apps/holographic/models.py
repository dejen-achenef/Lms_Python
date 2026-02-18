from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import json

User = get_user_model()


class HolographicProjector(models.Model):
    """Advanced holographic projection systems"""
    PROJECTOR_TYPES = [
        ('laser_based', 'Laser-Based Projection'),
        ('light_field', 'Light Field Display'),
        ('volumetric', 'Volumetric Display'),
        ('plasma', 'Plasma Display'),
        ('quantum_dot', 'Quantum Dot Projection'),
        ('photonic_crystal', 'Photonic Crystal Display'),
        ('metamaterial', 'Metamaterial Projection'),
    ]
    
    STATUS_CHOICES = [
        ('online', 'Online'),
        ('calibrating', 'Calibrating'),
        ('maintenance', 'Maintenance'),
        ('offline', 'Offline'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    projector_type = models.CharField(max_length=30, choices=PROJECTOR_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    
    # Display specifications
    resolution = models.CharField(max_length=20)  # e.g., "8K", "16K"
    refresh_rate = models.IntegerField(default=120)  # Hz
    color_depth = models.IntegerField(default=48)  # bits
    brightness = models.IntegerField(default=10000)  # nits
    
    # 3D capabilities
    volumetric_depth = models.FloatField(default=10.0)  # meters
    viewing_angle = models.FloatField(default=360.0)  # degrees
    parallax_layers = models.IntegerField(default=100)
    
    # Holographic quality
    hologram_fidelity = models.FloatField(default=0.0)  # 0.0 to 1.0
    spatial_resolution = models.FloatField(default=0.0)  # pixels per cubic meter
    temporal_coherence = models.FloatField(default=0.0)
    
    # Environmental requirements
    room_dimensions = models.JSONField(default=dict)  # {length, width, height}
    lighting_conditions = models.CharField(max_length=50, default='controlled')
    temperature_range = models.JSONField(default=dict)  # {min, max}
    
    # Connection interfaces
    hdmi_ports = models.IntegerField(default=4)
    displayport_ports = models.IntegerField(default=2)
    thunderbolt_ports = models.IntegerField(default=2)
    wireless_protocols = models.JSONField(default=list)
    
    # Calibration data
    calibration_matrix = models.JSONField(default=dict)
    distortion_correction = models.JSONField(default=dict)
    last_calibration = models.DateTimeField(null=True, blank=True)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='holographic_projectors')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'holographic_projectors'
        indexes = [
            models.Index(fields=['projector_type', 'status']),
            models.Index(fields=['hologram_fidelity']),
        ]

    def __str__(self):
        return f"Holographic Projector: {self.name} ({self.projector_type})"


class HolographicClassroom(models.Model):
    """Virtual holographic classroom environments"""
    CLASSROOM_TYPES = [
        ('traditional', 'Traditional Classroom'),
        ('laboratory', 'Science Laboratory'),
        ('lecture_hall', 'Lecture Hall'),
        ('simulation_room', 'Simulation Room'),
        ('virtual_reality', 'Virtual Reality Space'),
        ('mixed_reality', 'Mixed Reality Environment'),
        ('augmented_reality', 'Augmented Reality Space'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    classroom_type = models.CharField(max_length=30, choices=CLASSROOM_TYPES)
    
    # Physical configuration
    max_capacity = models.IntegerField(default=30)
    room_dimensions = models.JSONField(default=dict)
    ceiling_height = models.FloatField(default=3.0)  # meters
    
    # Holographic equipment
    projectors = models.ManyToManyField(HolographicProjector, related_name='classrooms')
    spatial_audio_system = models.BooleanField(default=True)
    haptic_feedback_system = models.BooleanField(default=True)
    
    # Environment simulation
    weather_simulation = models.BooleanField(default=True)
    time_of_day_control = models.BooleanField(default=True)
    gravity_simulation = models.FloatField(default=1.0)  # Earth gravities
    
    # Interactive elements
    interactive_surfaces = models.JSONField(default=list)
    gesture_recognition = models.BooleanField(default=True)
    voice_control = models.BooleanField(default=True)
    eye_tracking = models.BooleanField(default=True)
    
    # Content library
    available_environments = models.JSONField(default=list)
    object_library = models.JSONField(default=dict)
    material_properties = models.JSONField(default=dict)
    
    # Safety features
    emergency_stop = models.BooleanField(default=True)
    collision_detection = models.BooleanField(default=True)
    safety_boundaries = models.JSONField(default=dict)
    
    # Accessibility
    wheelchair_accessible = models.BooleanField(default=True)
    visual_impairment_support = models.BooleanField(default=True)
    hearing_impairment_support = models.BooleanField(default=True)
    
    is_active = models.BooleanField(default=True)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='holographic_classrooms')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'holographic_classrooms'
        indexes = [
            models.Index(fields=['classroom_type', 'is_active']),
            models.Index(fields=['max_capacity']),
        ]

    def __str__(self):
        return f"Holographic Classroom: {self.name}"


class HolographicContent(models.Model):
    """3D holographic educational content"""
    CONTENT_TYPES = [
        ('3d_model', '3D Model'),
        ('molecular_structure', 'Molecular Structure'),
        ('historical_scene', 'Historical Scene'),
        ('biological_process', 'Biological Process'),
        ('mathematical_visualization', 'Mathematical Visualization'),
        ('physics_simulation', 'Physics Simulation'),
        ('geographic_location', 'Geographic Location'),
        ('architectural_design', 'Architectural Design'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    content_type = models.CharField(max_length=30, choices=CONTENT_TYPES)
    
    # 3D model data
    model_file = models.FileField(upload_to='holographic_models/')
    texture_files = models.JSONField(default=list)
    animation_files = models.JSONField(default=list)
    
    # Technical specifications
    polygon_count = models.IntegerField(default=0)
    texture_resolution = models.CharField(max_length=20, default='4K')
    file_size = models.BigIntegerField(default=0)  # bytes
    
    # Interactive properties
    is_interactive = models.BooleanField(default=False)
    interaction_points = models.JSONField(default=list)
    physics_properties = models.JSONField(default=dict)
    
    # Educational metadata
    subject_area = models.CharField(max_length=100)
    difficulty_level = models.CharField(max_length=20, default='intermediate')
    learning_objectives = models.JSONField(default=list)
    
    # Display settings
    scale_factor = models.FloatField(default=1.0)
    rotation_speed = models.FloatField(default=0.0)
    auto_rotate = models.BooleanField(default=False)
    
    # Accessibility
    audio_descriptions = models.JSONField(default=dict)
    braille_labels = models.BooleanField(default=False)
    
    # Quality metrics
    visual_quality = models.FloatField(default=0.0)  # 0.0 to 1.0
    educational_effectiveness = models.FloatField(default=0.0)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='holographic_content')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='holographic_content')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'holographic_content'
        indexes = [
            models.Index(fields=['content_type', 'subject_area']),
            models.Index(fields['difficulty_level']),
        ]

    def __str__(self):
        return f"Holographic Content: {self.title}"


class HolographicSession(models.Model):
    """Live holographic learning sessions"""
    SESSION_TYPES = [
        ('lecture', 'Holographic Lecture'),
        ('laboratory', 'Virtual Laboratory'),
        ('field_trip', 'Virtual Field Trip'),
        ('simulation', 'Interactive Simulation'),
        ('collaboration', 'Collaborative Session'),
        ('assessment', 'Holographic Assessment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    session_type = models.CharField(max_length=30, choices=SESSION_TYPES)
    
    # Session configuration
    classroom = models.ForeignKey(HolographicClassroom, on_delete=models.CASCADE, related_name='sessions')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='holographic_sessions_taught')
    
    # Schedule
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    
    # Participants
    participants = models.ManyToManyField(User, related_name='holographic_sessions_attended', blank=True)
    max_participants = models.IntegerField(default=30)
    
    # Content
    holographic_content = models.ManyToManyField(HolographicContent, related_name='sessions')
    custom_environments = models.JSONField(default=list)
    
    # Interaction settings
    allow_participant_interaction = models.BooleanField(default=True)
    enable_voice_chat = models.BooleanField(default=True)
    enable_gesture_control = models.BooleanField(default=True)
    
    # Recording
    is_recorded = models.BooleanField(default=False)
    recording_file = models.FileField(upload_to='holographic_recordings/', null=True, blank=True)
    
    # Performance metrics
    engagement_score = models.FloatField(default=0.0)
    learning_outcome_score = models.FloatField(default=0.0)
    technical_quality = models.FloatField(default=0.0)
    
    # Status
    status = models.CharField(max_length=20, default='scheduled', choices=[
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('technical_issue', 'Technical Issue'),
    ])
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_holographic_sessions')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='holographic_sessions')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'holographic_sessions'
        ordering = ['-scheduled_start']
        indexes = [
            models.Index(fields=['session_type', 'status']),
            models.Index(fields=['scheduled_start']),
            models.Index(fields=['instructor']),
        ]

    def __str__(self):
        return f"Holographic Session: {self.title}"


class HolographicAvatar(models.Model):
    """Personalized holographic avatars for users"""
    AVATAR_TYPES = [
        ('realistic', 'Realistic Human'),
        ('stylized', 'Stylized Character'),
        ('abstract', 'Abstract Form'),
        ('robotic', 'Robotic Avatar'),
        ('animal', 'Animal Form'),
        ('mythical', 'Mythical Creature'),
        ('custom', 'Custom Design'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='holographic_avatar')
    
    # Avatar appearance
    avatar_type = models.CharField(max_length=30, choices=AVATAR_TYPES)
    height = models.FloatField(default=1.7)  # meters
    body_type = models.CharField(max_length=50, default='average')
    
    # Customization options
    skin_tone = models.CharField(max_length=20, blank=True, null=True)
    hair_color = models.CharField(max_length=20, blank=True, null=True)
    eye_color = models.CharField(max_length=20, blank=True, null=True)
    clothing_style = models.JSONField(default=dict)
    
    # 3D model data
    avatar_model = models.FileField(upload_to='avatar_models/')
    texture_map = models.ImageField(upload_to='avatar_textures/', null=True, blank=True)
    rigging_data = models.JSONField(default=dict)
    
    # Animation capabilities
    facial_expressions = models.JSONField(default=list)
    body_animations = models.JSONField(default=list)
    gesture_library = models.JSONField(default=dict)
    
    # Voice synthesis
    voice_profile = models.JSONField(default=dict)
    speech_patterns = models.JSONField(default=dict)
    accent = models.CharField(max_length=50, blank=True, null=True)
    
    # Behavioral traits
    personality_traits = models.JSONField(default=dict)
    movement_style = models.CharField(max_length=50, default='natural')
    interaction_style = models.CharField(max_length=50, default='friendly')
    
    # Privacy settings
    show_real_identity = models.BooleanField(default=False)
    anonymity_level = models.IntegerField(default=1)  # 1-5
    
    # Performance metrics
    rendering_complexity = models.FloatField(default=0.0)
    animation_smoothness = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'holographic_avatars'

    def __str__(self):
        return f"Avatar for {self.user.email}"


class HolographicInteraction(models.Model):
    """User interactions within holographic environments"""
    INTERACTION_TYPES = [
        ('gesture', 'Gesture Interaction'),
        ('voice', 'Voice Command'),
        ('gaze', 'Gaze Tracking'),
        ('touch', 'Touch Interaction'),
        ('motion', 'Body Motion'),
        ('brain_interface', 'Brain Interface'),
        ('emotional', 'Emotional Response'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='holographic_interactions')
    session = models.ForeignKey(HolographicSession, on_delete=models.CASCADE, related_name='interactions', null=True, blank=True)
    
    # Interaction data
    interaction_type = models.CharField(max_length=30, choices=INTERACTION_TYPES)
    interaction_data = models.JSONField(default=dict)
    
    # Spatial information
    position_3d = models.JSONField(default=dict)  # {x, y, z}
    orientation = models.JSONField(default=dict)  # {pitch, yaw, roll}
    velocity = models.JSONField(default=dict)  # {vx, vy, vz}
    
    # Target information
    target_object = models.CharField(max_length=255, blank=True, null=True)
    target_position = models.JSONField(default=dict)
    
    # Timing
    interaction_start = models.DateTimeField(auto_now_add=True)
    interaction_end = models.DateTimeField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)  # seconds
    
    # Accuracy and precision
    accuracy_score = models.FloatField(default=0.0)
    precision_score = models.FloatField(default=0.0)
    
    # Learning context
    learning_context = models.CharField(max_length=100, blank=True, null=True)
    educational_outcome = models.JSONField(default=dict)
    
    # Emotional response
    emotional_state = models.CharField(max_length=50, blank=True, null=True)
    engagement_level = models.FloatField(default=0.0)
    
    class Meta:
        db_table = 'holographic_interactions'
        indexes = [
            models.Index(fields=['user', 'interaction_type']),
            models.Index(fields=['session']),
            models.Index(fields=['interaction_start']),
        ]

    def __str__(self):
        return f"Holographic Interaction: {self.interaction_type} by {self.user.email}"


class HolographicEnvironment(models.Model):
    """Dynamic holographic environments"""
    ENVIRONMENT_TYPES = [
        ('historical', 'Historical Setting'),
        ('natural', 'Natural Environment'),
        ('urban', 'Urban Landscape'),
        ('space', 'Space Environment'),
        ('underwater', 'Underwater World'),
        ('microscopic', 'Microscopic World'),
        ('fantasy', 'Fantasy Realm'),
        ('abstract', 'Abstract Space'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    environment_type = models.CharField(max_length=30, choices=ENVIRONMENT_TYPES)
    
    # Environment description
    description = models.TextField()
    time_period = models.CharField(max_length=100, blank=True, null=True)
    geographic_location = models.CharField(max_length=100, blank=True, null=True)
    
    # 3D environment data
    environment_model = models.FileField(upload_to='holographic_environments/')
    skybox_texture = models.ImageField(upload_to='skybox_textures/', null=True, blank=True)
    lighting_setup = models.JSONField(default=dict)
    
    # Dynamic elements
    weather_systems = models.JSONField(default=list)
    day_night_cycle = models.BooleanField(default=True)
    seasonal_changes = models.BooleanField(default=False)
    
    # Interactive objects
    interactive_objects = models.JSONField(default=list)
    physics_simulation = models.JSONField(default=dict)
    
    # Ambient effects
    ambient_sounds = models.JSONField(default=dict)
    particle_effects = models.JSONField(default=list)
    atmospheric_effects = models.JSONField(default=dict)
    
    # Educational applications
    subject_areas = models.JSONField(default=list)
    learning_activities = models.JSONField(default=list)
    
    # Performance requirements
    rendering_complexity = models.FloatField(default=0.0)
    recommended_hardware = models.JSONField(default=dict)
    
    # Accessibility
        mobility_options = models.JSONField(default=dict)
    sensory_adaptations = models.JSONField(default=dict)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_holographic_environments')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='holographic_environments')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'holographic_environments'
        indexes = [
            models.Index(fields=['environment_type']),
            models.Index(fields(['subject_areas']),
        ]

    def __str__(self):
        return f"Holographic Environment: {self.name}"
