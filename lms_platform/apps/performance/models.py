from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import json

User = get_user_model()


class CacheConfiguration(models.Model):
    """Advanced cache configuration"""
    CACHE_TYPES = [
        ('redis', 'Redis'),
        ('memcached', 'Memcached'),
        ('database', 'Database'),
        ('file', 'File System'),
        ('memory', 'In-Memory'),
        ('cdn', 'CDN'),
    ]
    
    STRATEGIES = [
        ('write_through', 'Write Through'),
        ('write_behind', 'Write Behind'),
        ('write_around', 'Write Around'),
        ('refresh_ahead', 'Refresh Ahead'),
        ('cache_aside', 'Cache Aside'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    cache_type = models.CharField(max_length=20, choices=CACHE_TYPES)
    strategy = models.CharField(max_length=20, choices=STRATEGIES, default='cache_aside')
    
    # Connection settings
    host = models.CharField(max_length=255, blank=True, null=True)
    port = models.IntegerField(null=True, blank=True)
    database = models.IntegerField(null=True, blank=True)
    
    # Performance settings
    max_memory = models.BigIntegerField(null=True, blank=True)  # bytes
    ttl = models.IntegerField(default=3600)  # seconds
    max_connections = models.IntegerField(default=100)
    
    # Eviction policy
    eviction_policy = models.CharField(max_length=50, default='lru', choices=[
        ('lru', 'Least Recently Used'),
        ('lfu', 'Least Frequently Used'),
        ('fifo', 'First In First Out'),
        ('random', 'Random'),
        ('ttl', 'Time To Live'),
    ])
    
    # Compression
    compression_enabled = models.BooleanField(default=False)
    compression_algorithm = models.CharField(max_length=20, default='gzip')
    
    # Serialization
    serialization_format = models.CharField(max_length=20, default='json', choices=[
        ('json', 'JSON'),
        ('pickle', 'Pickle'),
        ('msgpack', 'MessagePack'),
        ('protobuf', 'Protocol Buffers'),
    ])
    
    # Clustering
    cluster_enabled = models.BooleanField(default=False)
    cluster_nodes = models.JSONField(default=list)
    
    # Monitoring
    monitoring_enabled = models.BooleanField(default=True)
    metrics_retention = models.IntegerField(default=7)  # days
    
    # Security
    authentication_enabled = models.BooleanField(default=False)
    ssl_enabled = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    health_status = models.CharField(max_length=20, default='unknown')
    last_health_check = models.DateTimeField(null=True, blank=True)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='cache_configurations')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cache_configurations'
        indexes = [
            models.Index(fields=['cache_type', 'is_active']),
            models.Index(fields=['health_status']),
        ]

    def __str__(self):
        return f"Cache Config: {self.name}"


class CacheRule(models.Model):
    """Advanced caching rules"""
    RULE_TYPES = [
        ('query', 'Query Result'),
        ('object', 'Object Instance'),
        ('template', 'Template Fragment'),
        ('api', 'API Response'),
        ('static', 'Static Content'),
        ('computed', 'Computed Value'),
    ]
    
    TRIGGER_EVENTS = [
        ('create', 'On Create'),
        ('update', 'On Update'),
        ('delete', 'On Delete'),
        ('custom', 'Custom Event'),
        ('schedule', 'Scheduled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES)
    
    # Target
    target_pattern = models.CharField(max_length=255)  # Regex or pattern
    target_model = models.CharField(max_length=100, blank=True, null=True)
    
    # Cache settings
    ttl = models.IntegerField(default=3600)  # seconds
    cache_key_template = models.CharField(max_length=500)
    
    # Invalidation
    invalidate_on = models.JSONField(default=list)  # List of trigger events
    invalidate_patterns = models.JSONField(default=list)
    
    # Conditions
    conditions = models.JSONField(default=dict)
    
    # Priority
    priority = models.IntegerField(default=5)  # 1-10
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Statistics
    hit_count = models.IntegerField(default=0)
    miss_count = models.IntegerField(default=0)
    invalidation_count = models.IntegerField(default=0)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cache_rules')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='cache_rules')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cache_rules'
        indexes = [
            models.Index(fields=['rule_type', 'is_active']),
            models.Index(fields=['priority']),
        ]

    def __str__(self):
        return f"Cache Rule: {self.name}"


class CacheEntry(models.Model):
    """Individual cache entries"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Key information
    cache_key = models.CharField(max_length=500)
    cache_type = models.CharField(max_length=50)
    
    # Data
    value = models.TextField()  # Serialized data
    value_size = models.BigIntegerField(default=0)  # bytes
    
    # Metadata
    content_type = models.CharField(max_length=100, blank=True, null=True)
    encoding = models.CharField(max_length=20, default='utf-8')
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    # Access tracking
    access_count = models.IntegerField(default=0)
    hit_rate = models.FloatField(default=0.0)
    
    # Status
    is_valid = models.BooleanField(default=True)
    
    # Tags
    tags = models.JSONField(default=list)
    
    # Version
    version = models.IntegerField(default=1)
    
    class Meta:
        db_table = 'cache_entries'
        indexes = [
            models.Index(fields=['cache_key']),
            models.Index(fields=['cache_type']),
            models.Index(fields=['expires_at']),
            models.Index(fields ['last_accessed']),
        ]

    def __str__(self):
        return f"Cache Entry: {self.cache_key}"


class PerformanceMetric(models.Model):
    """Performance metrics collection"""
    METRIC_TYPES = [
        ('response_time', 'Response Time'),
        ('throughput', 'Throughput'),
        ('error_rate', 'Error Rate'),
        ('cpu_usage', 'CPU Usage'),
        ('memory_usage', 'Memory Usage'),
        ('database_queries', 'Database Queries'),
        ('cache_hits', 'Cache Hits'),
        ('user_sessions', 'User Sessions'),
    ]
    
    UNITS = [
        ('milliseconds', 'Milliseconds'),
        ('seconds', 'Seconds'),
        ('requests_per_second', 'Requests/Second'),
        ('percentage', 'Percentage'),
        ('bytes', 'Bytes'),
        ('count', 'Count'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPES)
    unit = models.CharField(max_length=30, choices=UNITS)
    
    # Value
    value = models.FloatField()
    
    # Context
    service = models.CharField(max_length=100, blank=True, null=True)
    endpoint = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.UUID(null=True, blank=True)
    session_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Additional dimensions
    dimensions = models.JSONField(default=dict)
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Quality
    quality_score = models.FloatField(null=True, blank=True)  # 0.0 to 1.0
    
    # Alerting
    alert_threshold = models.FloatField(null=True, blank=True)
    alert_triggered = models.BooleanField(default=False)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='performance_metrics')
    
    class Meta:
        db_table = 'performance_metrics'
        indexes = [
            models.Index(fields=['metric_type', 'timestamp']),
            models.Index(fields=['service', 'timestamp']),
            models.Index(fields['endpoint']),
        ]

    def __str__(self):
        return f"{self.metric_type}: {self.value} {self.unit}"


class PerformanceAlert(models.Model):
    """Performance alerting system"""
    SEVERITY_LEVELS = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('resolved', 'Resolved'),
        ('suppressed', 'Suppressed'),
        ('acknowledged', 'Acknowledged'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_max_length=255)
    description = models.TextField()
    
    # Conditions
    metric_type = models.CharField(max_length=30, choices=PerformanceMetric.METRIC_TYPES)
    condition = models.CharField(max_length=100)  # >, <, >=, <=, ==
    threshold = models.FloatField()
    duration = models.IntegerField(default=300)  # seconds
    
    # Additional filters
    filters = models.JSONField(default=dict)
    
    # Severity
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    
    # Notification
    notification_channels = models.JSONField(default=list)
    notification_recipients = models.JSONField(default=list)
    
    # Status
    is_active = models.BooleanField(default=True)
    current_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # History
    last_triggered = models.DateTimeField(null=True, blank=True)
    trigger_count = models.IntegerField(default=0)
    
    # Cooldown
    cooldown_period = models.IntegerField(default=900)  # seconds
    next_notification = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performance_alerts')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='performance_alerts')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'performance_alerts'
        indexes = [
            models.Index(fields=['is_active', 'current_status']),
            models.Index(fields=['severity']),
            models.Index(fields=['last_triggered']),
        ]

    def __str__(self):
        return f"Alert: {self.name}"


class PerformanceReport(models.Model):
    """Automated performance reports"""
    REPORT_TYPES = [
        ('daily', 'Daily Summary'),
        ('weekly', 'Weekly Summary'),
        ('monthly', 'Monthly Summary'),
        ('real_time', 'Real-time Dashboard'),
        ('trend', 'Trend Analysis'),
        ('anomaly', 'Anomaly Detection'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Time period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Configuration
    metrics = models.JSONField(default=list)
    filters = models.JSONField(default=dict)
    group_by = models.JSONField(default=list)
    
    # Output
    output_format = models.CharField(max_length=20, default='json', choices=[
        ('json', 'JSON'),
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
        ('html', 'HTML'),
    ])
    
    # File information
    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    
    # Distribution
    recipients = models.JSONField(default=list)
    auto_distribute = models.BooleanField(default=False)
    
    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    schedule_config = models.JSONField(default=dict)
    next_run = models.DateTimeField(null=True, blank=True)
    
    # Processing
    generated_at = models.DateTimeField(null=True, blank=True)
    processing_time = models.IntegerField(null=True, blank=True)  # seconds
    
    # Error handling
    error_message = models.TextField(blank=True, null=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performance_reports')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='performance_reports')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'performance_reports'
        indexes = [
            models.Index(fields=['report_type', 'status']),
            models.Index(fields=['period_start']),
            models.Index(fields ['is_scheduled', 'next_run']),
        ]

    def __str__(self):
        return f"Report: {self.name}"


class DatabaseOptimization(models.Model):
    """Database optimization settings"""
    OPTIMIZATION_TYPES = [
        ('index', 'Index Optimization'),
        ('query', 'Query Optimization'),
        ('partition', 'Table Partitioning'),
        ('vacuum', 'Database Vacuum'),
        ('analyze', 'Statistics Update'),
        ('connection_pool', 'Connection Pooling'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    optimization_type = models.CharField(max_length=30, choices=OPTIMIZATION_TYPES)
    
    # Target
    target_table = models.CharField(max_length=100, blank=True, null=True)
    target_query = models.TextField(blank=True, null=True)
    
    # Configuration
    configuration = models.JSONField(default=dict)
    
    # Scheduling
    schedule_config = models.JSONField(default=dict)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    
    # Performance impact
    estimated_improvement = models.FloatField(null=True, blank=True)  # percentage
    actual_improvement = models.FloatField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Results
    execution_time = models.IntegerField(null=True, blank=True)  # seconds
    rows_affected = models.IntegerField(null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='database_optimizations')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='database_optimizations')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'database_optimizations'
        indexes = [
            models.Index(fields=['optimization_type', 'is_active']),
            models.Index(fields=['last_run']),
        ]

    def __str__(self):
        return f"Optimization: {self.name}"


class CDNConfiguration(models.Model):
    """CDN configuration and management"""
    PROVIDERS = [
        ('cloudflare', 'Cloudflare'),
        ('aws_cloudfront', 'AWS CloudFront'),
        ('fastly', 'Fastly'),
        ('akamai', 'Akamai'),
        ('azure_cdn', 'Azure CDN'),
        ('google_cdn', 'Google CDN'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    provider = models.CharField(max_length=30, choices=PROVIDERS)
    
    # Configuration
    distribution_id = models.CharField(max_length=255, blank=True, null=True)
    domain_name = models.CharField(max_length=255)
    origin_url = models.URLField()
    
    # Caching settings
    default_ttl = models.IntegerField(default=86400)  # seconds
    min_ttl = models.IntegerField(default=0)
    max_ttl = models.IntegerField(default=31536000)  # 1 year
    
    # Path patterns
    cache_patterns = models.JSONField(default=dict)
    bypass_patterns = models.JSONField(default=dict)
    
    # Compression
    compression_enabled = models.BooleanField(default=True)
    gzip_enabled = models.BooleanField(default=True)
    brotli_enabled = models.BooleanField(default=False)
    
    # Security
    https_only = models.BooleanField(default=True)
    custom_ssl_certificate = models.BooleanField(default=False)
    
    # Geographic settings
    geographic_restrictions = models.JSONField(default=dict)
    
    # Status
    is_active = models.BooleanField(default=True)
    deployment_status = models.CharField(max_length=20, default='pending')
    
    # Analytics
    analytics_enabled = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cdn_configurations')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='cdn_configurations')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cdn_configurations'
        indexes = [
            models.Index(fields=['provider', 'is_active']),
            models.Index(fields=['deployment_status']),
        ]

    def __str__(self):
        return f"CDN: {self.name} ({self.provider})"


class LoadBalancer(models.Model):
    """Load balancer configuration"""
    ALGORITHMS = [
        ('round_robin', 'Round Robin'),
        ('least_connections', 'Least Connections'),
        ('weighted_round_robin', 'Weighted Round Robin'),
        ('ip_hash', 'IP Hash'),
        ('random', 'Random'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    algorithm = models.CharField(max_length=30, choices=ALGORITHMS, default='round_robin')
    
    # Backend servers
    backend_servers = models.JSONField(default=list)
    
    # Health checks
    health_check_enabled = models.BooleanField(default=True)
    health_check_path = models.CharField(max_length=255, default='/health')
    health_check_interval = models.IntegerField(default=30)  # seconds
    health_check_timeout = models.IntegerField(default=5)  # seconds
    
    # Session persistence
    session_persistence = models.BooleanField(default=False)
    persistence_method = models.CharField(max_length=20, blank=True, null=True)
    
    # SSL/TLS
    ssl_enabled = models.BooleanField(default=False)
    ssl_certificate = models.TextField(blank=True, null=True)
    ssl_private_key = models.TextField(blank=True, null=True)
    
    # Rate limiting
    rate_limiting_enabled = models.BooleanField(default=False)
    rate_limit = models.IntegerField(null=True, blank=True)  # requests per second
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Statistics
    total_requests = models.BigIntegerField(default=0)
    active_connections = models.IntegerField(default=0)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='load_balancers')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='load_balancers')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'load_balancers'
        indexes = [
            models.Index(fields=['algorithm', 'is_active']),
        ]

    def __str__(self):
        return f"Load Balancer: {self.name}"
