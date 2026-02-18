from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import json

User = get_user_model()


class DNASynthesisMachine(models.Model):
    """Advanced DNA synthesis machines for data storage"""
    SYNTHESIS_TYPES = [
        ('enzymatic', 'Enzymatic DNA Synthesis'),
        ('chemical', 'Chemical DNA Synthesis'),
        ('biological', 'Biological DNA Synthesis'),
        ('quantum_dna', 'Quantum DNA Synthesis'),
        ('neural_dna', 'Neural DNA Synthesis'),
        ('hybrid', 'Hybrid Synthesis Method'),
    ]
    
    STATUS_CHOICES = [
        ('online', 'Online'),
        ('synthesizing', 'Synthesizing'),
        ('sequencing', 'Sequencing'),
        ('maintenance', 'Maintenance'),
        ('offline', 'Offline'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    synthesis_type = models.CharField(max_length=30, choices=SYNTHESIS_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    
    # Technical specifications
    synthesis_speed = models.FloatField(default=0.0)  # bases per second
    max_sequence_length = models.IntegerField(default=10000)  # bases
    accuracy_rate = models.FloatField(default=0.0)  # 0.0 to 1.0
    
    # Storage capacity
    data_density = models.FloatField(default=0.0)  # petabytes per gram
    storage_duration = models.FloatField(default=0.0)  # years
    temperature_requirement = models.FloatField(default=-20.0)  # Celsius
    
    # Chemical requirements
    nucleotide_consumption = models.JSONField(default.dict)
    enzyme_usage = models.JSONField(default.dict)
    energy_consumption = models.FloatField(default=0.0)  # watts
    
    # Error correction
    error_correction_method = models.CharField(max_length=50, default='reed_solomon')
    redundancy_factor = models.FloatField(default=3.0)
    
    # Quality control
    quality_metrics = models.JSONField(default.dict)
    contamination_detection = models.BooleanField(default=True)
    
    # Safety protocols
    biocontainment_level = models.IntegerField(default=2)  # BSL 1-4
    sterilization_procedures = models.JSONField(default.list)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='dna_synthesis_machines')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dna_synthesis_machines'
        indexes = [
            models.Index(fields=['synthesis_type', 'status']),
            models.Index(fields=['data_density']),
        ]

    def __str__(self):
        return f"DNA Synthesis Machine: {self.name} ({self.synthesis_type})"


class DNAStorageSequence(models.Model):
    """DNA sequences used for storing learning data"""
    SEQUENCE_TYPES = [
        ('educational_content', 'Educational Content'),
        ('user_memory', 'User Memory Data'),
        ('learning_patterns', 'Learning Patterns'),
        ('knowledge_graph', 'Knowledge Graph'),
        ('skill_data', 'Skill Acquisition Data'),
        ('experiential_data', 'Experiential Learning Data'),
    ]
    
    ENCODING_METHODS = [
        ('binary', 'Binary Encoding'),
        ('quaternary', 'Quaternary Encoding'),
        ('ternary', 'Ternary Encoding'),
        ('dna_fountain', 'DNA Fountain'),
        ('golden_gate', 'Golden Gate Assembly'),
        ('crispr_based', 'CRISPR-based Encoding'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sequence_name = models.CharField(max_length=255)
    sequence_type = models.CharField(max_length=30, choices=SEQUENCE_TYPES)
    encoding_method = models.CharField(max_length=30, choices=ENCODING_METHODS)
    
    # DNA sequence data
    dna_sequence = models.TextField()  # ATCG sequence
    sequence_length = models.IntegerField(default=0)  # bases
    gc_content = models.FloatField(default=0.0)  # 0.0 to 1.0
    
    # Data information
    original_data_size = models.BigIntegerField(default=0)  # bytes
    compressed_data_size = models.BigIntegerField(default=0)  # bytes
    compression_ratio = models.FloatField(default=0.0)
    
    # Storage properties
    storage_medium = models.CharField(max_length=50, default='synthetic_dna')
    storage_temperature = models.FloatField(default=-20.0)  # Celsius
    estimated_stability = models.FloatField(default=1000.0)  # years
    
    # Error correction
    error_correction_blocks = models.JSONField(default.list)
    parity_sequences = models.JSONField(default.list)
    checksum = models.CharField(max_length=64, blank=True, null=True)
    
    # Access control
    encryption_key = models.CharField(max_length=255, blank=True, null=True)
    access_permissions = models.JSONField(default.dict)
    biosecurity_level = models.IntegerField(default=1)
    
    # Metadata
    content_description = models.TextField()
    subject_areas = models.JSONField(default.list)
    difficulty_level = models.CharField(max_length=20, blank=True, null=True)
    
    # Synthesis information
    synthesis_machine = models.ForeignKey(DNASynthesisMachine, on_delete=models.CASCADE, related_name='sequences')
    synthesis_date = models.DateTimeField()
    synthesis_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Quality metrics
    sequence_accuracy = models.FloatField(default=0.0)
    read_reliability = models.FloatField(default=0.0)
    degradation_rate = models.FloatField(default=0.0)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dna_sequences')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='dna_sequences')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dna_storage_sequences'
        indexes = [
            models.Index(fields=['sequence_type', 'encoding_method']),
            models.Index(fields(['synthesis_date']),
        ]

    def __str__(self):
        return f"DNA Sequence: {self.sequence_name} ({self.sequence_type})"


class BiometricMemoryTransfer(models.Model):
    """Direct memory transfer using biometric DNA interfaces"""
    TRANSFER_TYPES = [
        ('skill_upload', 'Skill Upload to DNA'),
        ('memory_download', 'Memory Download from DNA'),
        ('knowledge_sync', 'Knowledge Synchronization'),
        ('experience_transfer', 'Experience Transfer'),
        ('intuition_imprinting', 'Intuition Imprinting'),
        ('muscle_memory', 'Muscle Memory Transfer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='biometric_transfers')
    transfer_type = models.CharField(max_length=30, choices=TRANSFER_TYPES)
    
    # DNA interface
    dna_sequence = models.ForeignKey(DNAStorageSequence, on_delete=models.CASCADE, related_name='biometric_transfers')
    interface_device = models.CharField(max_length=100)
    
    # Transfer parameters
    transfer_rate = models.FloatField(default=0.0)  # MB/s
    transfer_efficiency = models.FloatField(default=0.0)  # 0.0 to 1.0
    neural_bandwidth = models.FloatField(default=0.0)  # Hz
    
    # Biological integration
    integration_method = models.CharField(max_length=50, default='viral_vector')
    expression_level = models.FloatField(default=0.0)  # 0.0 to 1.0
    cellular_target = models.CharField(max_length=100, blank=True, null=True)
    
    # Memory characteristics
    memory_type = models.CharField(max_length=50, blank=True, null=True)
    emotional_context = models.JSONField(default.dict)
    sensory_data = models.JSONField(default.dict)
    
    # Learning outcomes
    knowledge_retention = models.FloatField(default=0.0)
    skill_proficiency = models.FloatField(default=0.0)
    integration_time = models.FloatField(default=0.0)  # hours
    
    # Safety monitoring
    biological_rejection = models.FloatField(default=0.0)
    immune_response = models.JSONField(default.dict)
    side_effects = models.JSONField(default.list)
    
    # Ethical considerations
    consent_verified = models.BooleanField(default=True)
    ethical_approval = models.CharField(max_length=100, blank=True, null=True)
    
    # Transfer timeline
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    stabilization_period = models.FloatField(default=24.0)  # hours
    
    class Meta:
        db_table = 'biometric_memory_transfers'
        ordering = ['-initiated_at']
        indexes = [
            models.Index(fields=['user', 'transfer_type']),
            models.Index(fields(['initiated_at']),
        ]

    def __str__(self):
        return f"Biometric Transfer: {self.transfer_type} for {self.user.email}"


class GeneticLearningProfile(models.Model):
    """Genetic profile for personalized learning based on DNA"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='genetic_learning_profile')
    
    # Genetic markers for learning
    memory_gene_variants = models.JSONField(default.dict)
    intelligence_markers = models.JSONField(default.dict)
    creativity_genes = models.JSONField(default.dict)
    learning_speed_genes = models.JSONField(default.dict)
    
    # Neurotransmitter profiles
    dopamine_receptors = models.JSONField(default.dict)
    serotonin_system = models.JSONField(default.dict)
    acetylcholine_pathways = models.JSONField(default.dict)
    norepinephrine_balance = models.JSONField(default.dict)
    
    # Cognitive predispositions
    visual_learning_aptitude = models.FloatField(default=0.0)
    auditory_learning_aptitude = models.FloatField(default=0.0)
    kinesthetic_learning_aptitude = models.FloatField(default=0.0)
    reading_compatibility = models.FloatField(default=0.0)
    
    # Memory characteristics
    short_term_capacity = models.FloatField(default=0.0)
    long_term_retention = models.FloatField(default=0.0)
    episodic_memory_strength = models.FloatField(default=0.0)
    procedural_memory_efficiency = models.FloatField(default=0.0)
    
    # Attention and focus
    attention_span = models.FloatField(default=0.0)
    focus_stability = models.FloatField(default=0.0)
    multitasking_ability = models.FloatField(default=0.0)
    distraction_resistance = models.FloatField(default=0.0)
    
    # Emotional learning factors
    emotional_regulation = models.FloatField(default=0.0)
    stress_resilience = models.FloatField(default=0.0)
    social_learning_aptitude = models.FloatField(default=0.0)
    empathy_capacity = models.FloatField(default=0.0)
    
    # Learning optimization
    optimal_study_duration = models.FloatField(default=45.0)  # minutes
    best_learning_times = models.JSONField(default.list)
    preferred_difficulty_progression = models.JSONField(default.dict)
    
    # Health considerations
    learning_disorder_markers = models.JSONField(default.dict)
    cognitive_decline_risk = models.FloatField(default=0.0)
    neuroplasticity_potential = models.FloatField(default=0.0)
    
    # Privacy and ethics
    genetic_data_consent = models.BooleanField(default=True)
    data_usage_permissions = models.JSONField(default.dict)
    
    # Analysis metadata
    analysis_date = models.DateTimeField(auto_now_add=True)
    analysis_method = models.CharField(max_length=100)
    confidence_score = models.FloatField(default=0.0)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'genetic_learning_profiles'

    def __str__(self):
        return f"Genetic Learning Profile: {self.user.email}"


class DNADataRetrieval(models.Model):
    """Advanced DNA data retrieval and sequencing"""
    RETRIEVAL_METHODS = [
        ('nanopore', 'Nanopore Sequencing'),
        ('illumina', 'Illumina Sequencing'),
        ('pacbio', 'PacBio Sequencing'),
        ('oxford_nanopore', 'Oxford Nanopore'),
        ('quantum_sequencing', 'Quantum Sequencing'),
        ('direct_read', 'Direct DNA Reading'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dna_sequence = models.ForeignKey(DNAStorageSequence, on_delete=models.CASCADE, related_name='retrievals')
    retrieval_method = models.CharField(max_length=30, choices=RETRIEVAL_METHODS)
    
    # Retrieval parameters
    retrieval_speed = models.FloatField(default=0.0)  # bases per second
    accuracy_rate = models.FloatField(default=0.0)
    coverage_depth = models.FloatField(default=0.0)
    
    # Data reconstruction
    error_correction_applied = models.BooleanField(default=True)
    data_integrity_check = models.BooleanField(default=True)
    reconstruction_quality = models.FloatField(default=0.0)
    
    # Retrieved data
    retrieved_data = models.BinaryField(null=True, blank=True)
    data_size = models.BigIntegerField(default=0)
    compression_ratio = models.FloatField(default=0.0)
    
    # Performance metrics
    retrieval_time = models.FloatField(default=0.0)  # seconds
    cost_per_megabyte = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    energy_consumption = models.FloatField(default=0.0)
    
    # Quality assessment
    sequence_fidelity = models.FloatField(default=0.0)
    data_corruption = models.FloatField(default=0.0)
    missing_data_percentage = models.FloatField(default=0.0)
    
    # Context
    retrieval_purpose = models.CharField(max_length=100, blank=True, null=True)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dna_retrievals')
    
    # Security
    access_granted = models.BooleanField(default=False)
    access_token = models.CharField(max_length=255, blank=True, null=True)
    
    retrieved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'dna_data_retrievals'
        indexes = [
            models.Index(fields=['dna_sequence', 'retrieval_method']),
            models.Index(fields(['retrieved_at']),
        ]

    def __str__(self):
        return f"DNA Retrieval: {self.dna_sequence.sequence_name}"


class EvolutionaryLearning(models.Model):
    """Evolutionary algorithms applied to learning using DNA principles"""
    EVOLUTION_TYPES = [
        ('genetic_algorithm', 'Genetic Algorithm'),
        ('evolutionary_strategy', 'Evolutionary Strategy'),
        ('differential_evolution', 'Differential Evolution'),
        ('neuroevolution', 'Neuroevolution'),
        ('genetic_programming', 'Genetic Programming'),
        ('coevolution', 'Coevolution'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evolutionary_learning')
    evolution_type = models.CharField(max_length=30, choices=EVOLUTION_TYPES)
    
    # Evolution parameters
    population_size = models.IntegerField(default=100)
    mutation_rate = models.FloatField(default=0.01)
    crossover_rate = models.FloatField(default=0.7)
    selection_pressure = models.FloatField(default=2.0)
    
    # Learning objectives
    fitness_function = models.TextField()
    optimization_goals = models.JSONField(default.list)
    constraints = models.JSONField(default.dict)
    
    # Genetic representation
    chromosome_length = models.IntegerField(default=0)
    gene_encoding = models.JSONField(default.dict)
    phenotype_mapping = models.JSONField(default.dict)
    
    # Evolution progress
    generation_count = models.IntegerField(default=0)
    best_fitness = models.FloatField(default=0.0)
    average_fitness = models.FloatField(default=0.0)
    convergence_rate = models.FloatField(default=0.0)
    
    # Learning outcomes
    evolved_strategies = models.JSONField(default.list)
    optimal_solutions = models.JSONField(default.dict)
    performance_improvement = models.FloatField(default=0.0)
    
    # Biological inspiration
    biological_metaphor = models.CharField(max_length=100, blank=True, null=True)
    natural_system = models.CharField(max_length=100, blank=True, null=True)
    
    # Applications
    learning_optimization = models.JSONField(default.dict)
    curriculum_evolution = models.JSONField(default.dict)
    personalization_evolution = models.JSONField(default.dict)
    
    # Computational resources
    computation_time = models.FloatField(default=0.0)  # hours
    energy_consumed = models.FloatField(default=0.0)  # kWh
    generations_per_second = models.FloatField(default=0.0)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'evolutionary_learning'
        indexes = [
            models.Index(fields=['user', 'evolution_type']),
            models.Index(fields(['generation_count']),
        ]

    def __str__(self):
        return f"Evolutionary Learning: {self.evolution_type} for {self.user.email}"


class SyntheticBiologyLearning(models.Model):
    """Synthetic biology approaches to enhance learning"""
    BIOLOGY_TYPES = [
        ('optogenetics', 'Optogenetic Enhancement'),
        ('synthetic_neurotransmitters', 'Synthetic Neurotransmitters'),
        ('engineered_receptors', 'Engineered Receptors'),
        ('artificial_synapses', 'Artificial Synapses'),
        ('neural_progenitors', 'Neural Progenitor Cells'),
        ('gene_therapy', 'Gene Therapy for Learning'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='synthetic_biology_learning')
    biology_type = models.CharField(max_length=30, choices=BIOLOGY_TYPES)
    
    # Biological intervention
    intervention_description = models.TextField()
    target_cells = models.JSONField(default.list)
    molecular_mechanism = models.JSONField(default.dict)
    
    # Enhancement parameters
    enhancement_level = models.FloatField(default=0.0)
    duration_of_effect = models.FloatField(default=0.0)  # days
    reversibility = models.BooleanField(default=True)
    
    # Learning improvements
    memory_formation_speed = models.FloatField(default=0.0)
    information_processing_rate = models.FloatField(default=0.0)
    neural_plasticity = models.FloatField(default=0.0)
    
    # Safety assessment
    biological_safety = models.FloatField(default=0.0)
    side_effect_profile = models.JSONField(default.dict)
    long_term_effects = models.JSONField(default.list)
    
    # Ethical considerations
    informed_consent = models.BooleanField(default=True)
    ethical_review_board = models.CharField(max_length=100, blank=True, null=True)
    regulatory_compliance = models.BooleanField(default=True)
    
    # Clinical trial data
    trial_phase = models.CharField(max_length=20, blank=True, null=True)
    participant_count = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0.0)
    
    # Manufacturing
    synthesis_method = models.CharField(max_length=100, blank=True, null=True)
    purity_level = models.FloatField(default=0.0)
    storage_requirements = models.JSONField(default.dict)
    
    # Cost and accessibility
    treatment_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    insurance_coverage = models.BooleanField(default=False)
    availability_status = models.CharField(max_length=20, default='experimental')
    
    administered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'synthetic_biology_learning'
        indexes = [
            models.Index(fields=['user', 'biology_type']),
            models.Index(fields(['enhancement_level']),
        ]

    def __str__(self):
        return f"Synthetic Biology: {self.biology_type} for {self.user.email}"
