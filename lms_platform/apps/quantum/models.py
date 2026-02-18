from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import json
import numpy as np

User = get_user_model()


class QuantumComputer(models.Model):
    """Quantum computer integration for AI optimization"""
    QUANTUM_TYPES = [
        ('superconducting', 'Superconducting Qubits'),
        ('trapped_ions', 'Trapped Ions'),
        ('photonic', 'Photonic Quantum'),
        ('topological', 'Topological Quantum'),
        ('neuromorphic', 'Neuromorphic Quantum'),
        ('annealing', 'Quantum Annealing'),
        ('hybrid', 'Hybrid Classical-Quantum'),
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
    quantum_type = models.CharField(max_length=30, choices=QUANTUM_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    
    # Quantum specifications
    qubit_count = models.IntegerField()
    quantum_volume = models.BigIntegerField(default=0)
    coherence_time = models.FloatField(default=0.0)  # microseconds
    gate_fidelity = models.FloatField(default=0.0)  # 0.0 to 1.0
    
    # Connection details
    quantum_api_url = models.URLField()
    quantum_token = models.CharField(max_length=500, blank=True, null=True)
    
    # Performance metrics
    operations_per_second = models.BigIntegerField(default=0)
    error_rate = models.FloatField(default=0.0)
    
    # Temperature and environment
    temperature = models.FloatField(default=0.015)  # Kelvin
    magnetic_field = models.FloatField(default=0.0)  # Tesla
    
    # Quantum algorithms supported
    supported_algorithms = models.JSONField(default=list)
    
    # Calibration data
    last_calibration = models.DateTimeField(null=True, blank=True)
    calibration_results = models.JSONField(default=dict)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='quantum_computers')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quantum_computers'
        indexes = [
            models.Index(fields=['quantum_type', 'status']),
            models.Index(fields=['qubit_count']),
        ]

    def __str__(self):
        return f"Quantum Computer: {self.name} ({self.qubit_count} qubits)"


class QuantumLearningOptimization(models.Model):
    """Quantum-optimized learning paths and recommendations"""
    OPTIMIZATION_TYPES = [
        ('learning_path', 'Learning Path Optimization'),
        ('content_recommendation', 'Content Recommendation'),
        ('knowledge_graph', 'Knowledge Graph Enhancement'),
        ('neural_network', 'Neural Network Training'),
        ('pattern_recognition', 'Pattern Recognition'),
        ('predictive_modeling', 'Predictive Modeling'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quantum_optimizations')
    optimization_type = models.CharField(max_length=30, choices=OPTIMIZATION_TYPES)
    
    # Quantum circuit configuration
    quantum_circuit = models.JSONField(default=dict)
    qubits_used = models.IntegerField(default=0)
    quantum_depth = models.IntegerField(default=0)
    
    # Optimization parameters
    objective_function = models.TextField()
    constraints = models.JSONField(default=dict)
    
    # Results
    optimal_solution = models.JSONField(default=dict)
    optimization_score = models.FloatField(default=0.0)
    convergence_iterations = models.IntegerField(default=0)
    
    # Performance comparison
    classical_time = models.FloatField(null=True, blank=True)  # seconds
    quantum_time = models.FloatField(null=True, blank=True)  # seconds
    speedup_factor = models.FloatField(null=True, blank=True)
    
    # Quantum computer used
    quantum_computer = models.ForeignKey(QuantumComputer, on_delete=models.CASCADE, related_name='optimizations')
    
    # Status
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'quantum_learning_optimizations'
        indexes = [
            models.Index(fields=['user', 'optimization_type']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Quantum Optimization: {self.optimization_type} for {self.user.email}"


class QuantumEntanglementNetwork(models.Model):
    """Quantum entanglement for instant communication"""
    NETWORK_TYPES = [
        ('bell_pairs', 'Bell Pairs'),
        ('ghz_states', 'GHZ States'),
        ('cluster_states', 'Cluster States'),
        ('w_states', 'W States'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    network_type = models.CharField(max_length=30, choices=NETWORK_TYPES)
    
    # Entangled particles
    entangled_nodes = models.JSONField(default=list)  # List of node IDs
    entanglement_fidelity = models.FloatField(default=0.0)
    
    # Communication properties
    quantum_channel_capacity = models.FloatField(default=0.0)  # qubits/second
    decoherence_time = models.FloatField(default=0.0)  # seconds
    
    # Network topology
    topology_graph = models.JSONField(default=dict)
    routing_table = models.JSONField(default=dict)
    
    # Security
    quantum_key_distribution = models.BooleanField(default=True)
    encryption_keys = models.JSONField(default=list)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_entanglement = models.DateTimeField(null=True, blank=True)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='quantum_networks')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quantum_entanglement_networks'

    def __str__(self):
        return f"Quantum Network: {self.name} ({self.network_type})"


class QuantumCircuit(models.Model):
    """Reusable quantum circuits for learning algorithms"""
    CIRCUIT_TYPES = [
        ('variational', 'Variational Quantum Circuit'),
        ('quantum_fourier', 'Quantum Fourier Transform'),
        ('grover', 'Grover\'s Algorithm'),
        ('shor', 'Shor\'s Algorithm'),
        ('qsvm', 'Quantum Support Vector Machine'),
        ('qnn', 'Quantum Neural Network'),
        ('vqe', 'Variational Quantum Eigensolver'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    circuit_type = models.CharField(max_length=30, choices=CIRCUIT_TYPES)
    
    # Circuit definition
    quantum_gates = models.JSONField(default=list)
    circuit_depth = models.IntegerField(default=0)
    qubit_count = models.IntegerField(default=0)
    
    # Parameters
    trainable_parameters = models.JSONField(default=list)
    parameter_values = models.JSONField(default=dict)
    
    # Performance metrics
    fidelity = models.FloatField(default=0.0)
    execution_time = models.FloatField(default=0.0)
    
    # Usage
    usage_count = models.IntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    
    # Learning applications
    learning_applications = models.JSONField(default=list)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quantum_circuits')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='quantum_circuits')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quantum_circuits'
        indexes = [
            models.Index(fields=['circuit_type']),
            models.Index(fields=['qubit_count']),
        ]

    def __str__(self):
        return f"Quantum Circuit: {self.name} ({self.circuit_type})"


class QuantumMeasurement(models.Model):
    """Quantum measurement results and analysis"""
    MEASUREMENT_TYPES = [
        ('computational', 'Computational Basis'),
        ('hadamard', 'Hadamard Basis'),
        ('bell', 'Bell Basis'),
        ('pauli_x', 'Pauli-X Basis'),
        ('pauli_y', 'Pauli-Y Basis'),
        ('pauli_z', 'Pauli-Z Basis'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    circuit = models.ForeignKey(QuantumCircuit, on_delete=models.CASCADE, related_name='measurements')
    measurement_type = models.CharField(max_length=30, choices=MEASUREMENT_TYPES)
    
    # Measurement results
    measurement_outcomes = models.JSONField(default=dict)  # {state: probability}
    measurement_counts = models.JSONField(default=dict)  # {state: count}
    
    # Quantum properties
    superposition_states = models.JSONField(default=list)
    entanglement_entropy = models.FloatField(default=0.0)
    
    # Statistical analysis
    expectation_values = models.JSONField(default=dict)
    variance = models.JSONField(default=dict)
    
    # Learning insights
    learning_patterns = models.JSONField(default=list)
    knowledge_extraction = models.JSONField(default=dict)
    
    # Metadata
    shots = models.IntegerField(default=1000)
    measurement_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'quantum_measurements'
        indexes = [
            models.Index(fields=['circuit', 'measurement_type']),
            models.Index(fields=['measurement_time']),
        ]

    def __str__(self):
        return f"Quantum Measurement: {self.circuit.name} - {self.measurement_type}"


class QuantumErrorCorrection(models.Model):
    """Quantum error correction for reliable computation"""
    CODE_TYPES = [
        ('shor', 'Shor Code'),
        ('steane', 'Steane Code'),
        ('surface', 'Surface Code'),
        ('color', 'Color Code'),
        ('bosonic', 'Bosonic Code'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code_type = models.CharField(max_length=30, choices=CODE_TYPES)
    
    # Error correction parameters
    logical_qubits = models.IntegerField(default=0)
    physical_qubits = models.IntegerField(default=0)
    code_distance = models.IntegerField(default=0)
    
    # Error rates
    bit_flip_rate = models.FloatField(default=0.0)
    phase_flip_rate = models.FloatField(default=0.0)
    depolarizing_rate = models.FloatField(default=0.0)
    
    # Correction performance
    logical_error_rate = models.FloatField(default=0.0)
    correction_threshold = models.FloatField(default=0.0)
    
    # Syndromes and corrections
    syndrome_circuit = models.JSONField(default=dict)
    correction_operations = models.JSONField(default=list)
    
    # Reliability metrics
    mean_time_to_failure = models.FloatField(default=0.0)  # hours
    availability = models.FloatField(default=0.0)  # 0.0 to 1.0
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='quantum_error_correction')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quantum_error_correction'

    def __str__(self):
        return f"Quantum Error Correction: {self.code_type}"


class QuantumSimulation(models.Model):
    """Quantum simulation of learning environments"""
    SIMULATION_TYPES = [
        ('molecular', 'Molecular Dynamics'),
        ('material', 'Material Properties'),
        ('biological', 'Biological Systems'),
        ('neural', 'Neural Processes'),
        ('social', 'Social Dynamics'),
        ('economic', 'Economic Models'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    simulation_type = models.CharField(max_length=30, choices=SIMULATION_TYPES)
    
    # Simulation parameters
    hamiltonian = models.JSONField(default=dict)
    initial_state = models.JSONField(default=dict)
    evolution_time = models.FloatField(default=0.0)
    
    # System properties
    particle_count = models.IntegerField(default=0)
    interaction_strength = models.FloatField(default=0.0)
    temperature = models.FloatField(default=0.0)
    
    # Learning application
    learning_scenario = models.TextField()
    educational_objectives = models.JSONField(default=list)
    
    # Results
    simulation_results = models.JSONField(default=dict)
    learning_insights = models.JSONField(default=list)
    
    # Performance
    simulation_time = models.FloatField(default=0.0)  # seconds
    accuracy = models.FloatField(default=0.0)
    
    # Visualization
    visualization_data = models.JSONField(default=dict)
    interactive_3d_model = models.URLField(blank=True, null=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quantum_simulations')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='quantum_simulations')
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'quantum_simulations'
        indexes = [
            models.Index(fields=['simulation_type']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return f"Quantum Simulation: {self.name} ({self.simulation_type})"


class QuantumAI(models.Model):
    """Quantum-enhanced artificial intelligence"""
    AI_TYPES = [
        ('quantum_ml', 'Quantum Machine Learning'),
        ('quantum_nlp', 'Quantum Natural Language Processing'),
        ('quantum_cv', 'Quantum Computer Vision'),
        ('quantum_rl', 'Quantum Reinforcement Learning'),
        ('quantum_gan', 'Quantum Generative Adversarial Networks'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    ai_type = models.CharField(max_length=30, choices=AI_TYPES)
    
    # Quantum AI architecture
    quantum_layers = models.JSONField(default=list)
    hybrid_architecture = models.JSONField(default=dict)
    
    # Training data
    training_dataset = models.JSONField(default=dict)
    quantum_features = models.JSONField(default=list)
    
    # Model performance
    quantum_accuracy = models.FloatField(default=0.0)
    classical_accuracy = models.FloatField(default=0.0)
    quantum_advantage = models.FloatField(default=0.0)
    
    # Learning capabilities
    learning_rate = models.FloatField(default=0.0)
    convergence_speed = models.FloatField(default=0.0)
    
    # Applications
    educational_applications = models.JSONField(default=list)
    personalization_level = models.FloatField(default=0.0)
    
    # Consciousness simulation (theoretical)
    consciousness_metrics = models.JSONField(default=dict)
    self_awareness_level = models.FloatField(default=0.0)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_training = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quantum_ai_models')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='quantum_ai')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quantum_ai'
        indexes = [
            models.Index(fields=['ai_type']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"Quantum AI: {self.name} ({self.ai_type})"
