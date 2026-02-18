from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import RegexValidator
import uuid
import json
import hashlib

User = get_user_model()


class SecurityAuditLog(models.Model):
    """Comprehensive security audit logging"""
    ACTION_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('password_change', 'Password Change'),
        ('password_reset', 'Password Reset'),
        ('mfa_enable', 'MFA Enable'),
        ('mfa_disable', 'MFA Disable'),
        ('api_access', 'API Access'),
        ('data_export', 'Data Export'),
        ('admin_action', 'Admin Action'),
        ('permission_change', 'Permission Change'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('security_breach', 'Security Breach'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='security_logs')
    
    # Action details
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    action_description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='low')
    
    # Request information
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    request_method = models.CharField(max_length=10, blank=True, null=True)
    request_path = models.TextField(blank=True, null=True)
    
    # Geographic information
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Device and browser information
    device_type = models.CharField(max_length=50, blank=True, null=True)
    browser = models.CharField(max_length=100, blank=True, null=True)
    operating_system = models.CharField(max_length=100, blank=True, null=True)
    
    # Security context
    session_id = models.CharField(max_length=255, blank=True, null=True)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    authentication_method = models.CharField(max_length=50, blank=True, null=True)
    
    # Risk assessment
    risk_score = models.FloatField(default=0.0)
    is_anomaly = models.BooleanField(default=False)
    anomaly_reasons = models.JSONField(default=list)
    
    # Additional data
    metadata = models.JSONField(default=dict)
    old_values = models.JSONField(default=dict)
    new_values = models.JSONField(default=dict)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Tenant context
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='security_logs')
    
    class Meta:
        db_table = 'security_audit_logs'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action_type', 'created_at']),
            models.Index(fields=['severity', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['risk_score', 'created_at']),
        ]

    def __str__(self):
        return f"{self.action_type} - {self.user.email if self.user else 'Anonymous'}"


class SecurityIncident(models.Model):
    """Security incident management"""
    INCIDENT_TYPES = [
        ('brute_force', 'Brute Force Attack'),
        ('data_breach', 'Data Breach'),
        ('unauthorized_access', 'Unauthorized Access'),
        ('malware_detection', 'Malware Detection'),
        ('phishing_attempt', 'Phishing Attempt'),
        ('ddos_attack', 'DDoS Attack'),
        ('sql_injection', 'SQL Injection'),
        ('xss_attempt', 'XSS Attempt'),
        ('privilege_escalation', 'Privilege Escalation'),
        ('data_exfiltration', 'Data Exfiltration'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('investigating', 'Investigating'),
        ('contained', 'Contained'),
        ('resolved', 'Resolved'),
        ('false_positive', 'False Positive'),
    ]
    
    SEVERITY_LEVELS = SecurityAuditLog.SEVERITY_LEVELS
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    incident_type = models.CharField(max_length=30, choices=INCIDENT_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Affected resources
    affected_users = models.ManyToManyField(User, related_name='security_incidents', blank=True)
    affected_systems = models.JSONField(default=list)
    affected_data = models.JSONField(default=dict)
    
    # Investigation details
    investigation_notes = models.TextField(blank=True, null=True)
    evidence = models.JSONField(default=list)
    mitigation_steps = models.JSONField(default=list)
    
    # Timeline
    detected_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    contained_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Assignment
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_incidents')
    
    # Impact assessment
    impact_assessment = models.TextField(blank=True, null=True)
    business_impact = models.CharField(max_length=20, choices=[
        ('none', 'None'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], default='low')
    
    # Related logs
    related_logs = models.ManyToManyField(SecurityAuditLog, related_name='incidents', blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='security_incidents')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'security_incidents'
        ordering = ['-detected_at']

    def __str__(self):
        return f"{self.title} ({self.severity})"


class SecurityPolicy(models.Model):
    """Security policies and compliance rules"""
    POLICY_TYPES = [
        ('password', 'Password Policy'),
        ('access_control', 'Access Control'),
        ('data_protection', 'Data Protection'),
        ('api_security', 'API Security'),
        ('session_management', 'Session Management'),
        ('encryption', 'Encryption Policy'),
        ('audit_logging', 'Audit Logging'),
        ('incident_response', 'Incident Response'),
    ]
    
    COMPLIANCE_STANDARDS = [
        ('gdpr', 'GDPR'),
        ('hipaa', 'HIPAA'),
        ('pci_dss', 'PCI DSS'),
        ('soc2', 'SOC 2'),
        ('iso27001', 'ISO 27001'),
        ('nist', 'NIST'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    policy_type = models.CharField(max_length=30, choices=POLICY_TYPES)
    compliance_standards = models.JSONField(default=list)
    
    # Policy rules
    rules = models.JSONField(default=dict)
    parameters = models.JSONField(default=dict)
    validation_logic = models.TextField(blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_enforced = models.BooleanField(default=True)
    enforcement_level = models.CharField(max_length=20, choices=[
        ('advisory', 'Advisory'),
        ('warning', 'Warning'),
        ('blocking', 'Blocking'),
        ('critical', 'Critical'),
    ], default='warning')
    
    # Applicability
    user_roles = models.JSONField(default=list)
    user_groups = models.JSONField(default=list)
    ip_ranges = models.JSONField(default=list)
    
    # Monitoring
    violation_count = models.IntegerField(default=0)
    last_violation = models.DateTimeField(null=True, blank=True)
    
    # Review cycle
    review_frequency = models.IntegerField(default=90)  # days
    last_reviewed = models.DateTimeField(null=True, blank=True)
    next_review = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_policies')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_policies')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='security_policies')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'security_policies'

    def __str__(self):
        return f"{self.name} ({self.policy_type})"


class SecurityPolicyViolation(models.Model):
    """Tracking of security policy violations"""
    policy = models.ForeignKey(SecurityPolicy, on_delete=models.CASCADE, related_name='violations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='policy_violations')
    
    # Violation details
    violation_details = models.JSONField(default=dict)
    context_data = models.JSONField(default=dict)
    
    # Action taken
    action_taken = models.CharField(max_length=50, blank=True, null=True)
    blocked = models.BooleanField(default=False)
    
    # Resolution
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'security_policy_violations'
        unique_together = ['policy', 'user', 'created_at']

    def __str__(self):
        return f"{self.user.email} violated {self.policy.name}"


class ThreatIntelligence(models.Model):
    """Threat intelligence data"""
    THREAT_TYPES = [
        ('malicious_ip', 'Malicious IP'),
        ('malicious_domain', 'Malicious Domain'),
        ('vulnerability', 'Vulnerability'),
        ('malware', 'Malware'),
        ('phishing', 'Phishing'),
        ('botnet', 'Botnet'),
        ('tor_exit', 'Tor Exit Node'),
        ('proxy', 'Proxy Server'),
    ]
    
    SEVERITY_LEVELS = SecurityAuditLog.SEVERITY_LEVELS
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    threat_type = models.CharField(max_length=30, choices=THREAT_TYPES)
    indicator = models.CharField(max_length=500)  # IP, domain, hash, etc.
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    
    # Threat details
    description = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=100)  # Threat intelligence source
    confidence = models.FloatField(default=0.0)  # 0.0 to 1.0
    
    # Active status
    is_active = models.BooleanField(default=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Related data
    tags = models.JSONField(default=list)
    related_indicators = models.JSONField(default=list)
    
    # Blocking rules
    auto_block = models.BooleanField(default=False)
    block_duration = models.IntegerField(null=True, blank=True)  # hours
    
    # Metadata
    metadata = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'threat_intelligence'
        indexes = [
            models.Index(fields=['threat_type', 'is_active']),
            models.Index(fields=['severity', 'is_active']),
            models.Index(fields=['indicator']),
        ]

    def __str__(self):
        return f"{self.threat_type}: {self.indicator}"


class SecurityScan(models.Model):
    """Automated security scans"""
    SCAN_TYPES = [
        ('vulnerability', 'Vulnerability Scan'),
        ('malware', 'Malware Scan'),
        ('configuration', 'Configuration Audit'),
        ('compliance', 'Compliance Check'),
        ('penetration', 'Penetration Test'),
        ('code_analysis', 'Code Analysis'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scan_type = models.CharField(max_length=30, choices=SCAN_TYPES)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Target
    target_type = models.CharField(max_length=50)  # system, application, network
    target_identifier = models.CharField(max_length=500)  # URL, IP, application name
    
    # Configuration
    scan_parameters = models.JSONField(default=dict)
    schedule = models.JSONField(default=dict)  # Cron-like schedule
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.FloatField(default=0.0)
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)  # seconds
    
    # Results
    findings = models.JSONField(default=list)
    vulnerabilities_found = models.IntegerField(default=0)
    risk_score = models.FloatField(default=0.0)
    
    # Reports
    report_generated = models.BooleanField(default=False)
    report_path = models.CharField(max_length=500, blank=True, null=True)
    
    # Assignment
    initiated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='initiated_scans')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='security_scans')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'security_scans'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.scan_type})"


class AccessControl(models.Model):
    """Fine-grained access control"""
    RESOURCE_TYPES = [
        ('course', 'Course'),
        ('lesson', 'Lesson'),
        ('quiz', 'Quiz'),
        ('user', 'User'),
        ('tenant', 'Tenant'),
        ('report', 'Report'),
        ('api', 'API Endpoint'),
        ('file', 'File'),
    ]
    
    PERMISSION_TYPES = [
        ('read', 'Read'),
        ('write', 'Write'),
        ('delete', 'Delete'),
        ('admin', 'Admin'),
        ('execute', 'Execute'),
        ('share', 'Share'),
        ('export', 'Export'),
        ('import', 'Import'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_controls')
    resource_type = models.CharField(max_length=30, choices=RESOURCE_TYPES)
    resource_id = models.CharField(max_length=255)
    permission = models.CharField(max_length=20, choices=PERMISSION_TYPES)
    
    # Conditions
    conditions = models.JSONField(default=dict)  # Time-based, IP-based, etc.
    restrictions = models.JSONField(default=dict)
    
    # Status
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Audit
    granted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='granted_permissions')
    reason = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'access_controls'
        unique_together = ['user', 'resource_type', 'resource_id', 'permission']

    def __str__(self):
        return f"{self.user.email} - {self.permission} on {self.resource_type}:{self.resource_id}"


class DataEncryption(models.Model):
    """Data encryption management"""
    ENCRYPTION_TYPES = [
        ('aes256', 'AES-256'),
        ('rsa4096', 'RSA-4096'),
        ('chacha20', 'ChaCha20'),
        ('custom', 'Custom'),
    ]
    
    DATA_TYPES = [
        ('personal_data', 'Personal Data'),
        ('financial_data', 'Financial Data'),
        ('health_data', 'Health Data'),
        ('academic_records', 'Academic Records'),
        ('communication', 'Communication'),
        ('files', 'Files'),
        ('database', 'Database'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data_type = models.CharField(max_length=30, choices=DATA_TYPES)
    encryption_type = models.CharField(max_length=20, choices=ENCRYPTION_TYPES)
    
    # Encryption keys
    key_id = models.CharField(max_length=255)
    key_version = models.IntegerField(default=1)
    algorithm = models.CharField(max_length=100)
    
    # Data reference
    data_reference = models.CharField(max_length=500)  # Table.field or file path
    checksum = models.CharField(max_length=64)  # SHA-256
    
    # Status
    is_encrypted = models.BooleanField(default=True)
    encryption_date = models.DateTimeField(auto_now_add=True)
    last_rotation = models.DateTimeField(null=True, blank=True)
    next_rotation = models.DateTimeField(null=True, blank=True)
    
    # Access control
    authorized_users = models.ManyToManyField(User, related_name='encryption_access', blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='encryption_records')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'data_encryption'

    def __str__(self):
        return f"{self.data_type} - {self.encryption_type}"
