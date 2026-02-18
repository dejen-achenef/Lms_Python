from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import json

User = get_user_model()


class WormholeGenerator(models.Model):
    """Advanced wormhole generators for instant global access"""
    GENERATOR_TYPES = [
        ('gravitational', 'Gravitational Wormhole'),
        ('quantum_entanglement', 'Quantum Entanglement Portal'),
        ('exotic_matter', 'Exotic Matter Wormhole'),
        ('string_theory', 'String Theory Portal'),
        ('m_brane', 'M-Brane Wormhole'),
        ('causality_violation', 'Causality Violation Portal'),
        ('dimensional_breach', 'Dimensional Breach Device'),
    ]
    
    STATUS_CHOICES = [
        ('online', 'Online'),
        ('stabilizing', 'Stabilizing'),
        ('active', 'Active'),
        ('unstable', 'Unstable'),
        ('critical', 'Critical'),
        ('collapsed', 'Collapsed'),
        ('maintenance', 'Maintenance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    generator_type = models.CharField(max_length=30, choices=GENERATOR_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    
    # Wormhole specifications
    max_portal_diameter = models.FloatField(default=10.0)  # meters
    portal_stability = models.FloatField(default=0.0)  # 0.0 to 1.0
    energy_requirement = models.BigIntegerField(default=0)  # watts
    
    # Spatial properties
    connection_distance = models.FloatField(default=0.0)  # light-years
    spatial_coordinates = models.JSONField(default.dict)  # {x, y, z, t}
    destination_coordinates = models.JSONField(default.dict)
    
    # Temporal properties
    time_dilation_factor = models.FloatField(default=1.0)
    causality_preservation = models.BooleanField(default=True)
    temporal_stability = models.FloatField(default=0.0)
    
    # Exotic matter requirements
    exotic_matter_type = models.CharField(max_length=50, default='negative_energy')
    exotic_matter_quantity = models.FloatField(default=0.0)  # kilograms
    containment_field_strength = models.FloatField(default=0.0)
    
    # Safety systems
    radiation_shielding = models.BooleanField(default=True)
    gravitational_stabilization = models.BooleanField(default=True)
    emergency_closure = models.BooleanField(default=True)
    
    # Network configuration
    bandwidth_capacity = models.BigIntegerField(default=0)  # terabits per second
    latency = models.FloatField(default=0.0)  # seconds (ideally 0)
    connection_quality = models.FloatField(default=0.0)
    
    # Physical location
    underground_depth = models.FloatField(default=1000.0)  # meters
    geographic_coordinates = models.JSONField(default.dict)
    seismic_stability = models.FloatField(default=0.0)
    
    # Control systems
    ai_control = models.BooleanField(default=True)
    autonomous_operation = models.BooleanField(default=True)
    remote_access = models.BooleanField(default=True)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='wormhole_generators')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'wormhole_generators'
        indexes = [
            models.Index(fields=['generator_type', 'status']),
            models.Index(fields=['connection_distance']),
        ]

    def __str__(self):
        return f"Wormhole Generator: {self.name} ({self.generator_type})"


class WormholePortal(models.Model):
    """Individual wormhole portal endpoints"""
    PORTAL_TYPES = [
        ('entrance', 'Entrance Portal'),
        ('exit', 'Exit Portal'),
        ('bidirectional', 'Bidirectional Portal'),
        ('multidirectional', 'Multidirectional Portal'),
        ('temporary', 'Temporary Portal'),
        ('permanent', 'Permanent Portal'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    generator = models.ForeignKey(WormholeGenerator, on_delete=models.CASCADE, related_name='portals')
    portal_type = models.CharField(max_length=30, choices=PORTAL_TYPES)
    
    # Portal properties
    portal_name = models.CharField(max_length=255)
    diameter = models.FloatField(default=5.0)  # meters
    shape = models.CharField(max_length=20, default='circular')
    
    # Location
    location_name = models.CharField(max_length=255)
    address = models.CharField(max_length=500, blank=True, null=True)
    coordinates = models.JSONField(default.dict)
    
    # Connection details
    connected_portal = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='connected_portals')
    connection_id = models.CharField(max_length=100, unique=True)
    
    # Access control
    access_level = models.CharField(max_length=20, default='public')
    authorized_users = models.ManyToManyField(User, related_name='accessible_portals', blank=True)
    security_clearance = models.IntegerField(default=1)  # 1-10
    
    # Operational parameters
    operating_hours = models.JSONField(default.dict)
    maintenance_schedule = models.JSONField(default.dict)
    
    # Safety features
    safety_sensors = models.JSONField(default.list)
    emergency_protocols = models.JSONField(default.dict)
    
    # Usage statistics
    daily_usage = models.IntegerField(default=0)
    total_transfers = models.BigIntegerField(default=0)
    peak_capacity = models.FloatField(default=0.0)
    
    # Learning applications
    educational_access = models.BooleanField(default=True)
    virtual_classroom_connection = models.BooleanField(default=True)
    resource_sharing = models.BooleanField(default=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'wormhole_portals'
        indexes = [
            models.Index(fields=['portal_type', 'is_active']),
            models.Index(fields=['generator']),
        ]

    def __str__(self):
        return f"Wormhole Portal: {self.portal_name}"


class InstantaneousTransfer(models.Model):
    """Record of instantaneous transfers through wormholes"""
    TRANSFER_TYPES = [
        ('data', 'Data Transfer'),
        ('physical_object', 'Physical Object Transfer'),
        ('energy', 'Energy Transfer'),
        ('information', 'Information Transfer'),
        ('consciousness', 'Consciousness Transfer'),
        ('quantum_state', 'Quantum State Transfer'),
    ]
    
    STATUS_CHOICES = [
        ('initiated', 'Transfer Initiated'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('lost', 'Lost in Transit'),
        ('corrupted', 'Data Corruption'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transfer_type = models.CharField(max_length=30, choices=TRANSFER_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    
    # Portal information
    entrance_portal = models.ForeignKey(WormholePortal, on_delete=models.CASCADE, related_name='outgoing_transfers')
    exit_portal = models.ForeignKey(WormholePortal, on_delete=models.CASCADE, related_name='incoming_transfers')
    
    # Transfer details
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_transfers')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_transfers', null=True, blank=True)
    
    # Content information
    content_description = models.CharField(max_length=500, blank=True, null=True)
    data_size = models.BigIntegerField(default=0)  # bytes
    object_mass = models.FloatField(default=0.0)  # kilograms
    
    # Transfer metrics
    transfer_time = models.FloatField(default=0.0)  # seconds (should be near 0)
    bandwidth_used = models.BigIntegerField(default=0)  # bits per second
    energy_consumed = models.FloatField(default=0.0)  # joules
    
    # Quality metrics
    transfer_integrity = models.FloatField(default=1.0)  # 0.0 to 1.0
    data_corruption = models.FloatField(default=0.0)
    spatial_distortion = models.FloatField(default=0.0)
    
    # Learning context
    educational_purpose = models.CharField(max_length=100, blank=True, null=True)
    course_material = models.BooleanField(default=False)
    collaborative_learning = models.BooleanField(default=False)
    
    # Security
    encryption_enabled = models.BooleanField(default=True)
    access_verified = models.BooleanField(default=True)
    security_clearance = models.IntegerField(default=1)
    
    # Temporal effects
    time_displacement = models.FloatField(default=0.0)  # seconds
    causality_violation = models.BooleanField(default=False)
    paradox_risk = models.FloatField(default=0.0)
    
    # Error handling
    error_code = models.CharField(max_length=50, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    retry_attempts = models.IntegerField(default=0)
    
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'instantaneous_transfers'
        ordering = ['-initiated_at']
        indexes = [
            models.Index(fields=['transfer_type', 'status']),
            models.Index(fields=['entrance_portal']),
            models.Index(fields=['initiated_at']),
        ]

    def __str__(self):
        return f"Transfer: {self.transfer_type} - {self.status}"


class GlobalLearningNetwork(models.Model):
    """Global learning network connected via wormholes"""
    NETWORK_TYPES = [
        ('educational', 'Educational Network'),
        ('research', 'Research Network'),
        ('collaborative', 'Collaborative Network'),
        ('resource_sharing', 'Resource Sharing Network'),
        ('emergency_response', 'Emergency Response Network'),
        ('cultural_exchange', 'Cultural Exchange Network'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    network_type = models.CharField(max_length=30, choices=NETWORK_TYPES)
    
    # Network configuration
    connected_portals = models.ManyToManyField(WormholePortal, related_name='networks')
    member_institutions = models.JSONField(default.list)
    
    # Network properties
    total_bandwidth = models.BigIntegerField(default=0)  # terabits per second
    latency = models.FloatField(default=0.0)  # seconds
    reliability = models.FloatField(default=0.0)  # 0.0 to 1.0
    
    # Geographic coverage
    coverage_area = models.FloatField(default=0.0)  # square kilometers
    connected_countries = models.JSONField(default.list)
    population_served = models.IntegerField(default=0)
    
    # Learning resources
    shared_courses = models.JSONField(default.list)
    collaborative_projects = models.JSONField(default.list)
    knowledge_base = models.JSONField(default.dict)
    
    # Network services
    real_time_collaboration = models.BooleanField(default=True)
    resource_sharing = models.BooleanField(default=True)
    emergency_education = models.BooleanField(default=True)
    
    # Quality of service
    service_level_agreement = models.JSONField(default.dict)
    uptime_guarantee = models.FloatField(default=99.999)
    performance_metrics = models.JSONField(default.dict)
    
    # Governance
    network_administrators = models.ManyToManyField(User, related_name='administered_networks', blank=True)
    governance_model = models.JSONField(default.dict)
    
    # Security
    network_security = models.JSONField(default.dict)
    threat_detection = models.BooleanField(default=True)
    incident_response = models.JSONField(default.dict)
    
    # Analytics
    usage_statistics = models.JSONField(default.dict)
    performance_analytics = models.JSONField(default.dict)
    learning_outcomes = models.JSONField(default.dict)
    
    is_active = models.BooleanField(default=True)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='global_learning_networks')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'global_learning_networks'
        indexes = [
            models.Index(fields=['network_type', 'is_active']),
            models.Index(fields(['total_bandwidth']),
        ]

    def __str__(self):
        return f"Global Network: {self.name} ({self.network_type})"


class DimensionalClassroom(models.Model):
    """Classrooms that exist across multiple dimensions"""
    CLASSROOM_TYPES = [
        ('multidimensional', 'Multidimensional Classroom'),
        ('parallel_reality', 'Parallel Reality Classroom'),
        ('time_shifted', 'Time-Shifted Classroom'),
        ('space_folded', 'Space-Folded Classroom'),
        ('quantum_entangled', 'Quantum Entangled Classroom'),
        ('consciousness_based', 'Consciousness-Based Classroom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    classroom_type = models.CharField(max_length=30, choices=CLASSROOM_TYPES)
    
    # Dimensional properties
    dimension_count = models.IntegerField(default=3)
    accessible_dimensions = models.JSONField(default.list)
    dimensional_coordinates = models.JSONField(default.dict)
    
    # Spatial properties
    apparent_size = models.FloatField(default=100.0)  # square meters
    actual_size = models.FloatField(default=1000000.0)  # square meters
    space_efficiency = models.FloatField(default=0.0)
    
    # Temporal properties
    time_flow_rate = models.FloatField(default=1.0)
    time_zones = models.JSONField(default.list)
    temporal_stability = models.FloatField(default=0.0)
    
    # Learning capabilities
    simultaneous_sessions = models.IntegerField(default=10)
    cross_dimensional_collaboration = models.BooleanField(default=True)
    reality_overlay = models.BooleanField(default=True)
    
    # Student capacity
    max_students_per_dimension = models.IntegerField(default=30)
    total_student_capacity = models.IntegerField(default=300)
    
    # Technology integration
    holographic_displays = models.BooleanField(default=True)
    neural_interface = models.BooleanField(default=False)
    consciousness_projection = models.BooleanField(default=False)
    
    # Environmental controls
    atmosphere_per_dimension = models.JSONField(default.dict)
    gravity_settings = models.JSONField(default.dict)
    environmental_simulation = models.BooleanField(default=True)
    
    # Portal connections
    connected_portals = models.ManyToManyField(WormholePortal, related_name='dimensional_classrooms', blank=True)
    
    # Learning features
    adaptive_reality = models.BooleanField(default=True)
    personalized_environment = models.BooleanField(default=True)
    context_aware_content = models.BooleanField(default=True)
    
    # Safety protocols
    dimensional_stability = models.FloatField(default=0.0)
    emergency_protocols = models.JSONField(default.dict)
    safety_monitors = models.JSONField(default.list)
    
    is_active = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_dimensional_classrooms')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='dimensional_classrooms')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dimensional_classrooms'
        indexes = [
            models.Index(fields=['classroom_type', 'is_active']),
            models.Index(fields(['dimension_count']),
        ]

    def __str__(self):
        return f"Dimensional Classroom: {self.name}"


class WormholeSecuritySystem(models.Model):
    """Advanced security for wormhole networks"""
    SECURITY_LEVELS = [
        ('level_1', 'Level 1 - Basic Security'),
        ('level_2', 'Level 2 - Enhanced Security'),
        ('level_3', 'Level 3 - Advanced Security'),
        ('level_4', 'Level 4 - Quantum Security'),
        ('level_5', 'Level 5 - Dimensional Security'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    security_level = models.CharField(max_length=20, choices=SECURITY_LEVELS)
    
    # Protected resources
    protected_portals = models.ManyToManyField(WormholePortal, related_name='security_systems', blank=True)
    protected_networks = models.ManyToManyField(GlobalLearningNetwork, related_name='security_systems', blank=True)
    
    # Security measures
    quantum_encryption = models.BooleanField(default=True)
    dimensional_locks = models.BooleanField(default=False)
    temporal_protection = models.BooleanField(default=False)
    
    # Authentication systems
    biometric_authentication = models.BooleanField(default=True)
    consciousness_verification = models.BooleanField(default=False)
    quantum_key_distribution = models.BooleanField(default=True)
    
    # Threat detection
    intrusion_detection = models.BooleanField(default=True)
    anomaly_detection = models.BooleanField(default=True)
    paradox_prevention = models.BooleanField(default=True)
    
    # Access control
    access_levels = models.JSONField(default.dict)
    permission_matrix = models.JSONField(default.dict)
    role_based_access = models.BooleanField(default=True)
    
    # Monitoring systems
    surveillance_network = models.JSONField(default.dict)
    activity_logging = models.BooleanField(default=True)
    real_time_monitoring = models.BooleanField(default=True)
    
    # Incident response
    automatic_response = models.BooleanField(default=True)
    containment_protocols = models.JSONField(default.dict)
    recovery_procedures = models.JSONField(default.dict)
    
    # Compliance
    regulatory_compliance = models.BooleanField(default=True)
    security_audits = models.JSONField(default.dict)
    certification_status = models.CharField(max_length=50, blank=True, null=True)
    
    # AI security
    ai_security_monitor = models.BooleanField(default=True)
    machine_learning_detection = models.BooleanField(default=True)
    predictive_threat_analysis = models.BooleanField(default=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'wormhole_security_systems'

    def __str__(self):
        return f"Security System: {self.name} ({self.security_level})"
