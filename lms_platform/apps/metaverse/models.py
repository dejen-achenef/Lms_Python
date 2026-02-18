from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import json

User = get_user_model()


class MetaverseCampus(models.Model):
    """Virtual reality metaverse campus environments"""
    CAMPUS_TYPES = [
        ('university', 'Virtual University'),
        ('research_institute', 'Research Institute'),
        ('innovation_hub', 'Innovation Hub'),
        ('library_complex', 'Library Complex'),
        ('laboratory_city', 'Laboratory City'),
        ('art_academy', 'Art Academy'),
        ('medical_center', 'Medical Center'),
        ('space_station', 'Space Station Campus'),
    ]
    
    ENVIRONMENTS = [
        ('earth_like', 'Earth-like Environment'),
        ('mars_colony', 'Mars Colony'),
        ('underwater', 'Underwater Campus'),
        ('orbital', 'Orbital Station'),
        ('fantasy_realm', 'Fantasy Realm'),
        ('cyberpunk_city', 'Cyberpunk City'),
        ('quantum_reality', 'Quantum Reality'),
        ('dimensional_portal', 'Dimensional Portal'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    campus_type = models.CharField(max_length=30, choices=CAMPUS_TYPES)
    environment_type = models.CharField(max_length=30, choices=ENVIRONMENTS)
    
    # Campus specifications
    virtual_area = models.FloatField(default=1000000.0)  # square meters
    max_population = models.IntegerField(default=10000)
    building_count = models.IntegerField(default=50)
    
    # Physics and reality
    gravity_setting = models.FloatField(default=1.0)  # Earth gravities
    time_dilation = models.FloatField(default=1.0)  # Time flow rate
    weather_system = models.BooleanField(default=True)
    day_night_cycle = models.BooleanField(default=True)
    
    # Technological features
    ai_inhabitants = models.IntegerField(default=100)
    smart_buildings = models.BooleanField(default=True)
    holographic_displays = models.BooleanField(default=True)
    teleportation_pads = models.IntegerField(default=20)
    
    # Learning facilities
    lecture_halls = models.IntegerField(default=10)
    laboratories = models.IntegerField(default=20)
    libraries = models.IntegerField(default=5)
    simulation_rooms = models.IntegerField(default=15)
    
    # Social spaces
    student_lounge = models.BooleanField(default=True)
    cafeteria = models.BooleanField(default=True)
    recreation_areas = models.IntegerField(default=10)
    sports_facilities = models.BooleanField(default=True)
    
    # Accessibility
    multi_language_support = models.BooleanField(default=True)
    disability_access = models.BooleanField(default=True)
    mobile_compatible = models.BooleanField(default=True)
    vr_requirements = models.JSONField(default.dict)
    
    # Economic system
    virtual_currency = models.CharField(max_length=20, default='Metacoin')
    marketplace = models.BooleanField(default=True)
    student_jobs = models.BooleanField(default=True)
    
    # Governance
    student_government = models.BooleanField(default=True)
    democratic_voting = models.BooleanField(default=True)
    community_rules = models.JSONField(default.dict)
    
    is_active = models.BooleanField(default=True)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='metaverse_campuses')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'metaverse_campuses'
        indexes = [
            models.Index(fields=['campus_type', 'environment_type']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"Metaverse Campus: {self.name}"


class VirtualAvatar(models.Model):
    """Advanced virtual avatars for metaverse interaction"""
    AVATAR_TYPES = [
        ('realistic_human', 'Realistic Human'),
        ('stylized_character', 'Stylized Character'),
        ('abstract_entity', 'Abstract Entity'),
        ('robotic_avatar', 'Robotic Avatar'),
        ('mythical_being', 'Mythical Being'),
        ('energy_form', 'Energy Form'),
        ('shapeshifter', 'Shapeshifter'),
        ('custom_species', 'Custom Species'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='virtual_avatar')
    
    # Avatar appearance
    avatar_type = models.CharField(max_length=30, choices=AVATAR_TYPES)
    height = models.FloatField(default=1.7)  # meters
    body_type = models.CharField(max_length=50, default='athletic')
    
    # Customization options
    skin_texture = models.CharField(max_length=100, blank=True, null=True)
    eye_color = models.CharField(max_length=20, blank=True, null=True)
    hair_style = models.CharField(max_length=100, blank=True, null=True)
    clothing_style = models.JSONField(default.dict)
    accessories = models.JSONField(default.list)
    
    # 3D model data
    avatar_model = models.FileField(upload_to='avatar_models/')
    texture_maps = models.JSONField(default.dict)
    animation_rig = models.JSONField(default.dict)
    
    # Animation capabilities
    facial_expressions = models.JSONField(default.list)
    body_animations = models.JSONField(default.list)
    gesture_library = models.JSONField(default.dict)
    locomotion_style = models.CharField(max_length=50, default='natural')
    
    # Voice and communication
    voice_profile = models.JSONField(default.dict)
    speech_synthesis = models.BooleanField(default=True)
    real_time_translation = models.BooleanField(default=True)
    
    # Special abilities
    flight_capability = models.BooleanField(default=False)
    teleportation = models.BooleanField(default=False)
    shape_shifting = models.BooleanField(default=False)
    special_powers = models.JSONField(default.list)
    
    # Intelligence and personality
    ai_personality = models.JSONField(default.dict)
    learning_algorithm = models.CharField(max_length=50, default='neural_network')
    autonomy_level = models.FloatField(default=0.0)  # 0.0 to 1.0
    
    # Social features
    social_interactions = models.JSONField(default.dict)
    relationship_network = models.JSONField(default.dict)
    reputation_score = models.FloatField(default=0.0)
    
    # Privacy settings
    identity_protection = models.BooleanField(default=False)
    data_sharing = models.JSONField(default.dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'virtual_avatars'

    def __str__(self):
        return f"Virtual Avatar: {self.user.email}"


class ImmersiveClassroom(models.Model):
    """Fully immersive virtual classrooms"""
    ROOM_TYPES = [
        ('traditional_lecture', 'Traditional Lecture Hall'),
        ('spherical_classroom', 'Spherical Classroom'),
        ('outdoor_amphitheater', 'Outdoor Amphitheater'),
        ('zero_gravity', 'Zero Gravity Classroom'),
        ('underwater_lecture', 'Underwater Lecture Hall'),
        ('space_observatory', 'Space Observatory Classroom'),
        ('time_chamber', 'Time Chamber Classroom'),
        ('dimensional_portal', 'Dimensional Portal Room'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    room_type = models.CharField(max_length=30, choices=ROOM_TYPES)
    campus = models.ForeignKey(MetaverseCampus, on_delete=models.CASCADE, related_name='classrooms')
    
    # Room specifications
    max_capacity = models.IntegerField(default=50)
    dimensions = models.JSONField(default.dict)  # {length, width, height}
    ceiling_height = models.FloatField(default=5.0)  # meters
    
    # Environmental controls
    weather_simulation = models.BooleanField(default=True)
    gravity_control = models.FloatField(default=1.0)
    time_flow_rate = models.FloatField(default=1.0)
    atmosphere_composition = models.JSONField(default.dict)
    
    # Display systems
    full_circle_projection = models.BooleanField(default=True)
    holographic_teacher = models.BooleanField(default=False)
    interactive_walls = models.BooleanField(default=True)
    floating_displays = models.IntegerField(default=10)
    
    # Learning tools
    virtual_whiteboards = models.IntegerField(default=5)
    three_d_model_viewers = models.IntegerField(default=3)
    simulation_pods = models.IntegerField(default=20)
    experiment_stations = models.IntegerField(default=10)
    
    # Sensory immersion
    haptic_feedback = models.BooleanField(default=True)
    scent_simulation = models.BooleanField(default=True)
    temperature_control = models.BooleanField(default=True)
    ambient_sounds = models.JSONField(default.dict)
    
    # Interactive elements
    manipulable_objects = models.JSONField(default.list)
    physics_simulation = models.BooleanField(default=True)
    real_time_collaboration = models.BooleanField(default=True)
    
    # Accessibility
    wheelchair_accessible = models.BooleanField(default=True)
    visual_impairment_mode = models.BooleanField(default=True)
    hearing_impairment_mode = models.BooleanField(default=True)
    
    # Recording and analytics
    session_recording = models.BooleanField(default=True)
    attention_tracking = models.BooleanField(default=True)
    engagement_metrics = models.BooleanField(default=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'immersive_classrooms'
        indexes = [
            models.Index(fields=['room_type', 'is_active']),
            models.Index(fields(['campus']),
        ]

    def __str__(self):
        return f"Immersive Classroom: {self.name}"


class MetaverseCourse(models.Model):
    """Courses designed for metaverse delivery"""
    COURSE_FORMATS = [
        ('fully_immersive', 'Fully Immersive'),
        ('hybrid_reality', 'Hybrid Reality'),
        ('simulation_based', 'Simulation-Based'),
        ('experiential', 'Experiential Learning'),
        ('social_collaborative', 'Social Collaborative'),
        ('gamified_adventure', 'Gamified Adventure'),
        ('narrative_journey', 'Narrative Journey'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    course_format = models.CharField(max_length=30, choices=COURSE_FORMATS)
    
    # Course structure
    modules = models.JSONField(default.list)
    learning_objectives = models.JSONField(default.list)
    prerequisite_skills = models.JSONField(default.list)
    
    # Metaverse elements
    virtual_locations = models.JSONField(default.list)
    interactive_elements = models.JSONField(default.list)
    narrative_arc = models.JSONField(default.dict)
    
    # Immersion level
    immersion_depth = models.FloatField(default=0.0)  # 0.0 to 1.0
    reality_blending = models.FloatField(default=0.0)
    presence_factor = models.FloatField(default=0.0)
    
    # Learning activities
    virtual_experiments = models.JSONField(default.list)
    role_playing_scenarios = models.JSONField(default.list)
    collaborative_projects = models.JSONField(default.list)
    exploration_tasks = models.JSONField(default.list)
    
    # Assessment methods
    performance_based = models.BooleanField(default=True)
    simulation_assessments = models.BooleanField(default=True)
    peer_evaluation = models.BooleanField(default=True)
    ai_tutoring = models.BooleanField(default=True)
    
    # Social features
    study_groups = models.BooleanField(default=True)
    discussion_forums = models.BooleanField(default=True)
    peer_mentoring = models.BooleanField(default=True)
    community_projects = models.BooleanField(default=True)
    
    # Technical requirements
    vr_headset_required = models.BooleanField(default=False)
    minimum_specs = models.JSONField(default.dict)
    bandwidth_requirement = models.FloatField(default=0.0)  # Mbps
    
    # Gamification
    experience_points = models.BooleanField(default=True)
    achievement_system = models.BooleanField(default=True)
    leaderboards = models.BooleanField(default=True)
    virtual_rewards = models.JSONField(default.list)
    
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='metaverse_courses')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='metaverse_courses')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'metaverse_courses'
        indexes = [
            models.Index(fields=['course_format']),
            models.Index(fields(['instructor']),
        ]

    def __str__(self):
        return f"Metaverse Course: {self.title}"


class VirtualLab(models.Model):
    """Advanced virtual laboratories for hands-on learning"""
    LAB_TYPES = [
        ('chemistry', 'Chemistry Laboratory'),
        ('physics', 'Physics Laboratory'),
        ('biology', 'Biology Laboratory'),
        ('engineering', 'Engineering Workshop'),
        ('computer_science', 'Computer Science Lab'),
        ('medical_simulation', 'Medical Simulation'),
        ('space_exploration', 'Space Exploration Lab'),
        ('quantum_research', 'Quantum Research Lab'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    lab_type = models.CharField(max_length=30, choices=LAB_TYPES)
    campus = models.ForeignKey(MetaverseCampus, on_delete=models.CASCADE, related_name='virtual_labs')
    
    # Lab specifications
    max_students = models.IntegerField(default=20)
    safety_level = models.IntegerField(default=1)  # 1-5
    experiment_complexity = models.FloatField(default=0.0)
    
    # Equipment and tools
    virtual_equipment = models.JSONField(default.list)
    measurement_instruments = models.JSONField(default.list)
    simulation_software = models.JSONField(default.list)
    
    # Safety features
    virtual_safety_protocols = models.JSONField(default.list)
    emergency_procedures = models.JSONField(default.dict)
    hazard_detection = models.BooleanField(default=True)
    
    # Experiment capabilities
    chemical_reactions = models.JSONField(default.list)
    physics_simulations = models.JSONField(default.list)
    biological_processes = models.JSONField(default.list)
    
    # Real-time simulation
    molecular_dynamics = models.BooleanField(default=False)
    quantum_mechanics = models.BooleanField(default=False)
    relativistic_effects = models.BooleanField(default=False)
    
    # Data collection
    virtual_sensors = models.JSONField(default.list)
    data_logging = models.BooleanField(default=True)
    real_time_analysis = models.BooleanField(default=True)
    
    # Collaboration
    shared_workspaces = models.IntegerField(default=5)
    team_experiments = models.BooleanField(default=True)
    peer_review = models.BooleanField(default=True)
    
    # Advanced features
    time_acceleration = models.BooleanField(default=False)
        scale_manipulation = models.BooleanField(default=False)
    force_field_simulation = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'virtual_labs'
        indexes = [
            models.Index(fields=['lab_type', 'is_active']),
            models.Index(fields(['campus']),
        ]

    def __str__(self):
        return f"Virtual Lab: {self.name} ({self.lab_type})"


class MetaverseSocialSpace(models.Model):
    """Social spaces for community building"""
    SPACE_TYPES = [
        ('student_lounge', 'Student Lounge'),
        ('cafeteria', 'Virtual Cafeteria'),
        ('library', 'Digital Library'),
        ('recreation_center', 'Recreation Center'),
        ('art_gallery', 'Art Gallery'),
        ('music_venue', 'Music Venue'),
        ('sports_arena', 'Sports Arena'),
        ('garden', 'Zen Garden'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    space_type = models.CharField(max_length=30, choices=SPACE_TYPES)
    campus = models.ForeignKey(MetaverseCampus, on_delete=models.CASCADE, related_name='social_spaces')
    
    # Space characteristics
    atmosphere = models.CharField(max_length=50, default='relaxed')
    ambient_music = models.BooleanField(default=True)
    dynamic_lighting = models.BooleanField(default=True)
    
    # Social features
    chat_systems = models.JSONField(default.list)
    activity_zones = models.JSONField(default.list)
    interaction_objects = models.JSONField(default.list)
    
    # Entertainment
    games_available = models.JSONField(default.list)
    entertainment_options = models.JSONField(default.list)
    event_scheduling = models.BooleanField(default=True)
    
    # Privacy settings
    private_areas = models.BooleanField(default=True)
    voice_chat_zones = models.BooleanField(default=True)
    video_conferencing = models.BooleanField(default=True)
    
    # Community features
    bulletin_boards = models.BooleanField(default=True)
    student_clubs = models.BooleanField(default=True)
    mentorship_programs = models.BooleanField(default=True)
    
    # Accessibility
    quiet_zones = models.BooleanField(default=True)
    accessibility_features = models.JSONField(default.list)
    
    max_occupancy = models.IntegerField(default=100)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'metaverse_social_spaces'
        indexes = [
            models.Index(fields=['space_type', 'is_active']),
            models.Index(fields(['campus']),
        ]

    def __str__(self):
        return f"Social Space: {self.name}"


class MetaverseEvent(models.Model):
    """Events and activities in the metaverse"""
    EVENT_TYPES = [
        ('lecture', 'Virtual Lecture'),
        ('conference', 'Conference'),
        ('workshop', 'Workshop'),
        ('exhibition', 'Exhibition'),
        ('competition', 'Competition'),
        ('social_gathering', 'Social Gathering'),
        ('graduation', 'Graduation Ceremony'),
        ('festival', 'Virtual Festival'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    
    # Event details
    campus = models.ForeignKey(MetaverseCampus, on_delete=models.CASCADE, related_name='events')
    venue = models.CharField(max_length=255, blank=True, null=True)
    
    # Schedule
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration = models.FloatField(default=0.0)  # hours
    
    # Participants
    max_attendees = models.IntegerField(null=True, blank=True)
    registered_attendees = models.ManyToManyField(User, related_name='metaverse_events', blank=True)
    
    # Virtual features
    virtual_speakers = models.JSONField(default.list)
    interactive_elements = models.JSONField(default.list)
    networking_opportunities = models.BooleanField(default=True)
    
    # Recording
    will_be_recorded = models.BooleanField(default=False)
    recording_available = models.BooleanField(default=False)
    recording_file = models.FileField(upload_to='event_recordings/', null=True, blank=True)
    
    # Accessibility
    multi_language_support = models.BooleanField(default=False)
    sign_language_interpreter = models.BooleanField(default=False)
    closed_captions = models.BooleanField(default=True)
    
    # Gamification
    event_achievements = models.JSONField(default.list)
    networking_points = models.BooleanField(default=True)
    participation_rewards = models.JSONField(default.list)
    
    # Social features
    live_chat = models.BooleanField(default=True)
    q_and_a_session = models.BooleanField(default=True)
    social_media_integration = models.BooleanField(default=True)
    
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'metaverse_events'
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['event_type', 'start_time']),
            models.Index(fields(['campus']),
        ]

    def __str__(self):
        return f"Metaverse Event: {self.title}"
