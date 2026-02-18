from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import json

User = get_user_model()


class BlockchainNetwork(models.Model):
    """Blockchain network configuration"""
    NETWORK_TYPES = [
        ('ethereum', 'Ethereum'),
        ('polygon', 'Polygon'),
        ('binance', 'Binance Smart Chain'),
        ('avalanche', 'Avalanche'),
        ('solana', 'Solana'),
        ('hyperledger', 'Hyperledger Fabric'),
        ('private', 'Private Network'),
        ('testnet', 'Test Network'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Maintenance'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    network_type = models.CharField(max_length=30, choices=NETWORK_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Network configuration
    rpc_url = models.URLField()
    websocket_url = models.URLField(blank=True, null=True)
    chain_id = models.IntegerField()
    
    # Contract configuration
    contract_address = models.CharField(max_length=255, blank=True, null=True)
    contract_abi = models.JSONField(default=dict)
    
    # Account configuration
    admin_address = models.CharField(max_length=255)
    private_key_encrypted = models.TextField(blank=True, null=True)
    
    # Gas settings
    gas_limit = models.IntegerField(default=100000)
    gas_price_gwei = models.FloatField(null=True, blank=True)
    
    # Security
    ssl_enabled = models.BooleanField(default=True)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    
    # Monitoring
    block_time = models.IntegerField(default=15)  # seconds
    confirmation_blocks = models.IntegerField(default=12)
    
    # Status tracking
    last_block_synced = models.BigIntegerField(default=0)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='blockchain_networks')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'blockchain_networks'
        indexes = [
            models.Index(fields=['network_type', 'status']),
            models.Index(fields=['chain_id']),
        ]

    def __str__(self):
        return f"Network: {self.name} ({self.network_type})"


class CertificateTemplate(models.Model):
    """Blockchain certificate templates"""
    TEMPLATE_TYPES = [
        ('course_completion', 'Course Completion'),
        ('degree', 'Degree'),
        ('diploma', 'Diploma'),
        ('certification', 'Certification'),
        ('achievement', 'Achievement'),
        ('attendance', 'Attendance'),
        ('participation', 'Participation'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Design
    background_image = models.ImageField(upload_to='certificate_backgrounds/', null=True, blank=True)
    layout_config = models.JSONField(default=dict)
    css_styles = models.TextField(blank=True, null=True)
    
    # Content fields
    fields = models.JSONField(default=dict)  # Field definitions for the certificate
    
    # Blockchain settings
    issue_on_blockchain = models.BooleanField(default=True)
    network = models.ForeignKey(BlockchainNetwork, on_delete=models.CASCADE, related_name='certificate_templates', null=True, blank=True)
    
    # Validation settings
    unique_identifier_field = models.CharField(max_length=100, default='certificate_id')
    expires_after_days = models.IntegerField(null=True, blank=True)
    
    # Security
    digital_signature_required = models.BooleanField(default=True)
    qr_code_enabled = models.BooleanField(default=True)
    
    # Preview
    preview_image = models.ImageField(upload_to='certificate_previews/', null=True, blank=True)
    
    # Version control
    version = models.IntegerField(default=1)
    is_default = models.BooleanField(default=False)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificate_templates')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='certificate_templates')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'certificate_templates'
        indexes = [
            models.Index(fields=['template_type', 'status']),
            models.Index(fields=['is_default']),
        ]

    def __str__(self):
        return f"Template: {self.name}"


class BlockchainCertificate(models.Model):
    """Blockchain-issued certificates"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Issuance'),
        ('issued', 'Issued'),
        ('revoked', 'Revoked'),
        ('expired', 'Expired'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    certificate_id = models.CharField(max_length=100, unique=True)
    
    # Recipient
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blockchain_certificates')
    recipient_name = models.CharField(max_length=255)
    recipient_email = models.EmailField()
    
    # Certificate details
    template = models.ForeignKey(CertificateTemplate, on_delete=models.CASCADE, related_name='certificates')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Related entities
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='certificates', null=True, blank=True)
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE, related_name='certificates', null=True, blank=True)
    
    # Content data
    certificate_data = models.JSONField(default=dict)
    
    # Issuance
    issued_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issued_certificates')
    issued_at = models.DateTimeField(null=True, blank=True)
    
    # Expiration
    expires_at = models.DateTimeField(null=True, blank=True)
    is_permanent = models.BooleanField(default=True)
    
    # Blockchain information
    transaction_hash = models.CharField(max_length=255, blank=True, null=True)
    block_number = models.BigIntegerField(null=True, blank=True)
    block_hash = models.CharField(max_length=255, blank=True, null=True)
    gas_used = models.BigIntegerField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Verification
    verification_code = models.CharField(max_length=255, unique=True)
    qr_code = models.ImageField(upload_to='certificate_qr/', null=True, blank=True)
    
    # Files
    pdf_file = models.FileField(upload_to='certificates/pdf/', null=True, blank=True)
    image_file = models.ImageField(upload_to='certificates/images/', null=True, blank=True)
    
    # Revocation
    revoked_at = models.DateTimeField(null=True, blank=True)
    revocation_reason = models.TextField(blank=True, null=True)
    revoked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='revoked_certificates')
    
    # Metadata
    metadata = models.JSONField(default=dict)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='blockchain_certificates')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'blockchain_certificates'
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['certificate_id']),
            models.Index(fields=['transaction_hash']),
            models.Index(fields=['verification_code']),
            models.Index(fields=['issued_at']),
        ]

    def __str__(self):
        return f"Certificate: {self.title} - {self.recipient_name}"


class CertificateVerification(models.Model):
    """Certificate verification logs"""
    VERIFICATION_TYPES = [
        ('qr_scan', 'QR Code Scan'),
        ('code_entry', 'Code Entry'),
        ('api_call', 'API Call'),
        ('blockchain', 'Blockchain Verification'),
        ('manual', 'Manual Verification'),
    ]
    
    certificate = models.ForeignKey(BlockchainCertificate, on_delete=models.CASCADE, related_name='verifications')
    
    # Verification details
    verification_type = models.CharField(max_length=30, choices=VERIFICATION_TYPES)
    verification_code = models.CharField(max_length=255)
    
    # Request information
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    referrer = models.URLField(blank=True, null=True)
    
    # Geographic information
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    
    # Result
    is_valid = models.BooleanField()
    verification_message = models.TextField()
    
    # Additional data
    certificate_data = models.JSONField(default=dict)
    
    # Timestamp
    verified_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'certificate_verifications'
        indexes = [
            models.Index(fields=['certificate', 'verified_at']),
            models.Index(fields(['verification_code']),
            models.Index(fields(['is_valid']),
            models.Index(fields(['verified_at']),
        ]

    def __str__(self):
        return f"Verification: {self.verification_code} - {'Valid' if self.is_valid else 'Invalid'}"


class BlockchainTransaction(models.Model):
    """Blockchain transaction tracking"""
    TRANSACTION_TYPES = [
        ('issue_certificate', 'Issue Certificate'),
        ('revoke_certificate', 'Revoke Certificate'),
        ('update_certificate', 'Update Certificate'),
        ('batch_issue', 'Batch Issue'),
        ('contract_deployment', 'Contract Deployment'),
        ('contract_upgrade', 'Contract Upgrade'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
        ('replaced', 'Replaced'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES)
    
    # Transaction details
    transaction_hash = models.CharField(max_length=255, unique=True)
    from_address = models.CharField(max_length=255)
    to_address = models.CharField(max_length=255, blank=True, null=True)
    
    # Network information
    network = models.ForeignKey(BlockchainNetwork, on_delete=models.CASCADE, related_name='transactions')
    block_number = models.BigIntegerField(null=True, blank=True)
    block_hash = models.CharField(max_length=255, blank=True, null=True)
    
    # Gas information
    gas_price = models.BigIntegerField(null=True, blank=True)  # wei
    gas_limit = models.BigIntegerField(null=True, blank=True)
    gas_used = models.BigIntegerField(null=True, blank=True)
    
    # Value and fees
    transaction_value = models.BigIntegerField(default=0)  # wei
    transaction_fee = models.DecimalField(max_digits=20, decimal_places=18, default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    confirmations = models.IntegerField(default=0)
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    # Related certificates
    certificates = models.ManyToManyField(BlockchainCertificate, related_name='transactions', blank=True)
    
    # Data
    input_data = models.TextField(blank=True, null=True)
    logs = models.JSONField(default=list)
    
    # Error information
    error_message = models.TextField(blank=True, null=True)
    error_code = models.CharField(max_length=50, blank=True, null=True)
    
    # Retry information
    retry_count = models.IntegerField(default=0)
    parent_transaction = models.CharField(max_length=255, blank=True, null=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blockchain_transactions')
    
    class Meta:
        db_table = 'blockchain_transactions'
        indexes = [
            models.Index(fields(['network', 'status']),
            models.Index(fields(['transaction_hash']),
            models.Index(fields(['from_address']),
            models.Index(fields(['block_number']),
            models.Index(fields(['created_at']),
        ]

    def __str__(self):
        return f"Transaction: {self.transaction_hash[:10]}... ({self.status})"


class SmartContract(models.Model):
    """Smart contract management"""
    CONTRACT_TYPES = [
        ('certificate', 'Certificate Contract'),
        ('registry', 'Registry Contract'),
        ('access_control', 'Access Control Contract'),
        ('payment', 'Payment Contract'),
        ('nft', 'NFT Contract'),
        ('token', 'Token Contract'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('deployed', 'Deployed'),
        ('verified', 'Verified'),
        ('deprecated', 'Deprecated'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    contract_type = models.CharField(max_length=30, choices=CONTRACT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Contract code
    source_code = models.TextField()
    compiled_bytecode = models.TextField(blank=True, null=True)
    abi = models.JSONField(default=dict)
    
    # Deployment information
    network = models.ForeignKey(BlockchainNetwork, on_delete=models.CASCADE, related_name='contracts')
    contract_address = models.CharField(max_length=255, blank=True, null=True)
    deployment_transaction = models.CharField(max_length=255, blank=True, null=True)
    
    # Version
    version = models.CharField(max_length=20, default='1.0.0')
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verification_guid = models.CharField(max_length=255, blank=True, null=True)
    
    # Constructor arguments
    constructor_args = models.JSONField(default=list)
    
    # Admin settings
    admin_address = models.CharField(max_length=255)
    
    # Upgrade settings
    is_upgradable = models.BooleanField(default=False)
    proxy_address = models.CharField(max_length=255, blank=True, null=True)
    
    # Events
    event_filters = models.JSONField(default=dict)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='smart_contracts')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='smart_contracts')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'smart_contracts'
        indexes = [
            models.Index(fields(['contract_type', 'status']),
            models.Index(fields(['network']),
            models.Index(fields(['contract_address']),
        ]

    def __str__(self):
        return f"Contract: {self.name} ({self.contract_type})"


class DigitalSignature(models.Model):
    """Digital signatures for certificates"""
    SIGNATURE_TYPES = [
        ('issuer', 'Issuer Signature'),
        ('recipient', 'Recipient Signature'),
        ('verifier', 'Verifier Signature'),
        ('witness', 'Witness Signature'),
    ]
    
    certificate = models.ForeignKey(BlockchainCertificate, on_delete=models.CASCADE, related_name='signatures')
    
    # Signature details
    signature_type = models.CharField(max_length=20, choices=SIGNATURE_TYPES)
    signer_address = models.CharField(max_length=255)
    signature_data = models.TextField()  # Base64 encoded signature
    
    # Signer information
    signer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='digital_signatures')
    signer_name = models.CharField(max_length=255)
    signer_role = models.CharField(max_length=100, blank=True, null=True)
    
    # Signature metadata
    signing_algorithm = models.CharField(max_length=50, default='RSA-SHA256')
    certificate_used = models.TextField(blank=True, null=True)
    
    # Timestamp
    signed_at = models.DateTimeField(auto_now_add=True)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Additional data
    metadata = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'digital_signatures'
        indexes = [
            models.Index(fields(['certificate', 'signature_type']),
            models.Index(fields(['signer_address']),
            models.Index(fields(['signed_at']),
        ]

    def __str__(self):
        return f"Signature: {self.signer_name} - {self.signature_type}"


class CertificateBatch(models.Model):
    """Batch certificate processing"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Batch configuration
    template = models.ForeignKey(CertificateTemplate, on_delete=models.CASCADE, related_name='batches')
    network = models.ForeignKey(BlockchainNetwork, on_delete=models.CASCADE, related_name='batches')
    
    # Recipients
    recipients = models.JSONField(default=list)  # List of recipient data
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Progress
    total_recipients = models.IntegerField(default=0)
    processed_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    
    # Blockchain transaction
    batch_transaction = models.CharField(max_length=255, blank=True, null=True)
    gas_used = models.BigIntegerField(null=True, blank=True)
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    estimated_completion = models.DateTimeField(null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(blank=True, null=True)
    failed_items = models.JSONField(default=list)
    
    # Cost tracking
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    cost_per_certificate = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    # Created by
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificate_batches')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='certificate_batches')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'certificate_batches'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields(['status', 'created_at']),
            models.Index(fields(['template']),
            models.Index(fields(['created_by']),
        ]

    def __str__(self):
        return f"Batch: {self.name} ({self.status})"
