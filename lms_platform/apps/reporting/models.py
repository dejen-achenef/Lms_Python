from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import json

User = get_user_model()


class Report(models.Model):
    """Custom reports and dashboards"""
    REPORT_TYPES = [
        ('summary', 'Summary Report'),
        ('detailed', 'Detailed Report'),
        ('trend', 'Trend Analysis'),
        ('comparison', 'Comparison Report'),
        ('forecast', 'Forecast Report'),
        ('real_time', 'Real-time Dashboard'),
        ('executive', 'Executive Summary'),
        ('compliance', 'Compliance Report'),
    ]
    
    VISUALIZATION_TYPES = [
        ('table', 'Table'),
        ('chart', 'Chart'),
        ('graph', 'Graph'),
        ('gauge', 'Gauge'),
        ('map', 'Map'),
        ('heatmap', 'Heatmap'),
        ('pivot', 'Pivot Table'),
        ('kpi', 'KPI Cards'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    visualization_type = models.CharField(max_length=20, choices=VISUALIZATION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Data sources
    data_sources = models.JSONField(default=list)
    filters = models.JSONField(default=dict)
    parameters = models.JSONField(default=dict)
    
    # Query configuration
    sql_query = models.TextField(blank=True, null=True)
    query_builder_config = models.JSONField(default=dict)
    
    # Visualization settings
    chart_config = models.JSONField(default=dict)
    layout_config = models.JSONField(default=dict)
    styling = models.JSONField(default=dict)
    
    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    schedule_config = models.JSONField(default=dict)
    next_run = models.DateTimeField(null=True, blank=True)
    
    # Distribution
    recipients = models.JSONField(default=list)
    distribution_method = models.CharField(max_length=20, default='email', choices=[
        ('email', 'Email'),
        ('dashboard', 'Dashboard'),
        ('api', 'API'),
        ('webhook', 'Webhook'),
    ])
    
    # Access control
    is_public = models.BooleanField(default=False)
    allowed_users = models.ManyToManyField(User, related_name='accessible_reports', blank=True)
    allowed_roles = models.JSONField(default=list)
    
    # Performance
    estimated_runtime = models.IntegerField(null=True, blank=True)  # seconds
    cache_duration = models.IntegerField(default=3600)  # seconds
    
    # Version control
    version = models.IntegerField(default=1)
    parent_report = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_reports')
    
    # Metadata
    tags = models.JSONField(default=list)
    category = models.CharField(max_length=100, blank=True, null=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_reports')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_reports', null=True, blank=True)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='reports')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reports'
        indexes = [
            models.Index(fields=['report_type', 'status']),
            models.Index(fields=['is_scheduled', 'next_run']),
            models.Index(fields=['created_by', 'created_at']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.name} ({self.report_type})"


class ReportExecution(models.Model):
    """Report execution history"""
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='executions')
    
    # Execution details
    execution_id = models.UUIDField(default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    
    # Parameters
    parameters_used = models.JSONField(default=dict)
    filters_applied = models.JSONField(default=dict)
    
    # Timing
    queued_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)  # seconds
    
    # Results
    row_count = models.IntegerField(null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)  # bytes
    file_path = models.CharField(max_length=500, blank=True, null=True)
    
    # Performance metrics
    query_time = models.FloatField(null=True, blank=True)  # seconds
    render_time = models.FloatField(null=True, blank=True)  # seconds
    
    # Error handling
    error_message = models.TextField(blank=True, null=True)
    error_traceback = models.TextField(blank=True, null=True)
    
    # Distribution
    distributed_at = models.DateTimeField(null=True, blank=True)
    distribution_status = models.JSONField(default=dict)
    
    # User context
    triggered_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='triggered_reports', null=True, blank=True)
    
    class Meta:
        db_table = 'report_executions'
        ordering = ['-queued_at']
        indexes = [
            models.Index(fields=['report', 'status']),
            models.Index(fields=['status', 'queued_at']),
            models.Index(fields=['triggered_by', 'queued_at']),
        ]

    def __str__(self):
        return f"Execution {self.execution_id} - {self.report.name}"


class Dashboard(models.Model):
    """Custom dashboards"""
    LAYOUT_TYPES = [
        ('grid', 'Grid Layout'),
        ('flex', 'Flex Layout'),
        ('freeform', 'Freeform Layout'),
        ('tabbed', 'Tabbed Layout'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    layout_type = models.CharField(max_length=20, choices=LAYOUT_TYPES, default='grid')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Layout configuration
    layout_config = models.JSONField(default=dict)
    widgets = models.JSONField(default=list)
    
    # Data refresh
    auto_refresh = models.BooleanField(default=False)
    refresh_interval = models.IntegerField(default=300)  # seconds
    
    # Filters and controls
    global_filters = models.JSONField(default=list)
    date_range_selector = models.BooleanField(default=True)
    
    # Access control
    is_public = models.BooleanField(default=False)
    allowed_users = models.ManyToManyField(User, related_name='accessible_dashboards', blank=True)
    allowed_roles = models.JSONField(default=list)
    
    # Sharing
    shareable_link = models.UUIDField(null=True, blank=True)
    allow_embedding = models.BooleanField(default=False)
    
    # Theme
    theme_config = models.JSONField(default=dict)
    
    # Performance
    cache_enabled = models.BooleanField(default=True)
    cache_duration = models.IntegerField(default=300)  # seconds
    
    # Analytics
    view_count = models.IntegerField(default=0)
    unique_viewers = models.IntegerField(default=0)
    last_viewed = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_dashboards')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_dashboards', null=True, blank=True)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='dashboards')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dashboards'
        indexes = [
            models.Index(fields=['status', 'is_public']),
            models.Index(fields=['created_by', 'created_at']),
            models.Index(fields=['view_count']),
        ]

    def __str__(self):
        return f"Dashboard: {self.name}"


class KPI(models.Model):
    """Key Performance Indicators"""
    KPI_TYPES = [
        ('counter', 'Counter'),
        ('gauge', 'Gauge'),
        ('trend', 'Trend'),
        ('progress', 'Progress Bar'),
        ('metric', 'Simple Metric'),
    ]
    
    AGGREGATION_TYPES = [
        ('sum', 'Sum'),
        ('average', 'Average'),
        ('count', 'Count'),
        ('min', 'Minimum'),
        ('max', 'Maximum'),
        ('custom', 'Custom Formula'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    kpi_type = models.CharField(max_length=20, choices=KPI_TYPES)
    aggregation_type = models.CharField(max_length=20, choices=AGGREGATION_TYPES)
    
    # Data source
    data_source = models.JSONField(default=dict)
    metric_field = models.CharField(max_length=100)
    filters = models.JSONField(default=dict)
    
    # Display settings
    unit = models.CharField(max_length=50, blank=True, null=True)
    decimal_places = models.IntegerField(default=0)
    prefix = models.CharField(max_length=10, blank=True, null=True)
    suffix = models.CharField(max_length=10, blank=True, null=True)
    
    # Targets and thresholds
    target_value = models.FloatField(null=True, blank=True)
    warning_threshold = models.FloatField(null=True, blank=True)
    critical_threshold = models.FloatField(null=True, blank=True)
    
    # Color coding
    color_scheme = models.JSONField(default=dict)
    
    # Trend analysis
    show_trend = models.BooleanField(default=False)
    trend_period = models.IntegerField(default=30)  # days
    
    # Dashboard placement
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='kpis', null=True, blank=True)
    position = models.JSONField(default=dict)
    
    # Caching
    cache_duration = models.IntegerField(default=300)  # seconds
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_kpis')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='kpis')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'kpis'
        indexes = [
            models.Index(fields=['dashboard']),
            models.Index(fields=['kpi_type']),
        ]

    def __str__(self):
        return f"KPI: {self.name}"


class DataWarehouse(models.Model):
    """Data warehouse configuration"""
    WAREHOUSE_TYPES = [
        ('postgresql', 'PostgreSQL'),
        ('mysql', 'MySQL'),
        ('snowflake', 'Snowflake'),
        ('bigquery', 'Google BigQuery'),
        ('redshift', 'Amazon Redshift'),
        ('clickhouse', 'ClickHouse'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    warehouse_type = models.CharField(max_length=30, choices=WAREHOUSE_TYPES)
    
    # Connection details
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    database = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=255)  # Encrypted
    
    # SSL and security
    ssl_enabled = models.BooleanField(default=True)
    ssl_cert_path = models.CharField(max_length=500, blank=True, null=True)
    
    # Configuration
    connection_pool_size = models.IntegerField(default=5)
    query_timeout = models.IntegerField(default=300)  # seconds
    
    # Status
    is_active = models.BooleanField(default=True)
    last_tested = models.DateTimeField(null=True, blank=True)
    connection_status = models.CharField(max_length=20, default='unknown')
    
    # Tables and schemas
    schemas = models.JSONField(default=list)
    tables = models.JSONField(default=dict)
    
    # Sync configuration
    sync_enabled = models.BooleanField(default=False)
    sync_schedule = models.JSONField(default=dict)
    last_sync = models.DateTimeField(null=True, blank=True)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='data_warehouses')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'data_warehouses'

    def __str__(self):
        return f"Data Warehouse: {self.name}"


class ETLJob(models.Model):
    """ETL (Extract, Transform, Load) jobs"""
    JOB_TYPES = [
        ('incremental', 'Incremental Load'),
        ('full', 'Full Load'),
        ('real_time', 'Real-time Sync'),
        ('batch', 'Batch Process'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('paused', 'Paused'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_max_length=255)
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Source configuration
    source_config = models.JSONField(default=dict)
    
    # Transformation logic
    transformation_rules = models.JSONField(default=list)
    custom_transformations = models.TextField(blank=True, null=True)
    
    # Target configuration
    target_config = models.JSONField(default=dict)
    
    # Scheduling
    schedule_config = models.JSONField(default=dict)
    next_run = models.DateTimeField(null=True, blank=True)
    
    # Execution history
    last_run = models.DateTimeField(null=True, blank=True)
    last_success = models.DateTimeField(null=True, blank=True)
    last_failure = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    total_runs = models.IntegerField(default=0)
    successful_runs = models.IntegerField(default=0)
    failed_runs = models.IntegerField(default=0)
    average_runtime = models.FloatField(default=0.0)  # seconds
    
    # Data metrics
    records_processed = models.BigIntegerField(default=0)
    records_transformed = models.BigIntegerField(default=0)
    records_loaded = models.BigIntegerField(default=0)
    
    # Error handling
    error_threshold = models.IntegerField(default=0)  # Max errors before failure
    retry_count = models.IntegerField(default=3)
    
    # Notifications
    notify_on_success = models.BooleanField(default=False)
    notify_on_failure = models.BooleanField(default=True)
    notification_recipients = models.JSONField(default=list)
    
    # Dependencies
    dependencies = models.JSONField(default=list)  # Other ETL jobs that must complete first
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_etl_jobs')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='etl_jobs')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'etl_jobs'
        indexes = [
            models.Index(fields=['status', 'next_run']),
            models.Index(fields=['job_type']),
            models.Index(fields=['last_run']),
        ]

    def __str__(self):
        return f"ETL Job: {self.name}"


class ETLExecution(models.Model):
    """ETL job execution history"""
    job = models.ForeignKey(ETLJob, on_delete=models.CASCADE, related_name='executions')
    
    # Execution details
    execution_id = models.UUIDField(default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=20, choices=ETLJob.STATUS_CHOICES, default='pending')
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)  # seconds
    
    # Data metrics
    records_extracted = models.BigIntegerField(default=0)
    records_transformed = models.BigIntegerField(default=0)
    records_loaded = models.BigIntegerField(default=0)
    records_rejected = models.BigIntegerField(default=0)
    
    # Performance metrics
    extract_time = models.FloatField(null=True, blank=True)  # seconds
    transform_time = models.FloatField(null=True, blank=True)  # seconds
    load_time = models.FloatField(null=True, blank=True)  # seconds
    
    # Error handling
    error_count = models.IntegerField(default=0)
    error_details = models.JSONField(default=list)
    warnings = models.JSONField(default=list)
    
    # Logs
    execution_log = models.TextField(blank=True, null=True)
    
    # Trigger context
    triggered_by = models.CharField(max_length=20, default='schedule')  # schedule, manual, api
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'etl_executions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['job', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"ETL Execution {self.execution_id} - {self.job.name}"


class BusinessIntelligence(models.Model):
    """BI insights and predictions"""
    INSIGHT_TYPES = [
        ('trend', 'Trend Analysis'),
        ('anomaly', 'Anomaly Detection'),
        ('forecast', 'Forecast'),
        ('correlation', 'Correlation Analysis'),
        ('segmentation', 'Customer Segmentation'),
        ('optimization', 'Optimization Suggestion'),
        ('risk', 'Risk Assessment'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    insight_type = models.CharField(max_length=30, choices=INSIGHT_TYPES)
    description = models.TextField()
    
    # Data and analysis
    data_sources = models.JSONField(default=list)
    analysis_method = models.CharField(max_length=100)
    confidence_score = models.FloatField(default=0.0)
    
    # Findings
    key_findings = models.JSONField(default=list)
    metrics = models.JSONField(default=dict)
    
    # Recommendations
    recommendations = models.JSONField(default=list)
    action_items = models.JSONField(default=list)
    
    # Visualizations
    charts = models.JSONField(default=list)
    
    # Impact assessment
    business_impact = models.TextField(blank=True, null=True)
    potential_roi = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Priority and urgency
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='medium')
    
    # Timeframe
    analysis_period_start = models.DateTimeField()
    analysis_period_end = models.DateTimeField()
    valid_until = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, default='new', choices=[
        ('new', 'New'),
        ('reviewing', 'Reviewing'),
        ('approved', 'Approved'),
        ('implemented', 'Implemented'),
        ('archived', 'Archived'),
    ])
    
    # Assignment
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_insights')
    
    # Follow-up
    follow_up_date = models.DateTimeField(null=True, blank=True)
    implementation_notes = models.TextField(blank=True, null=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_insights')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='bi_insights')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'business_intelligence'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['insight_type', 'priority']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['analysis_period_end']),
        ]

    def __str__(self):
        return f"BI Insight: {self.title}"


class AlertSystem(models.Model):
    """Automated alert system for KPIs and metrics"""
    ALERT_TYPES = [
        ('threshold', 'Threshold Breach'),
        ('trend', 'Trend Change'),
        ('anomaly', 'Anomaly Detection'),
        ('data_quality', 'Data Quality Issue'),
        ('system', 'System Alert'),
    ]
    
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
    name = models.CharField(max_length=255)
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    
    # Conditions
    conditions = models.JSONField(default=dict)
    threshold_values = models.JSONField(default=dict)
    
    # Monitoring target
    target_kpi = models.ForeignKey(KPI, on_delete=models.CASCADE, related_name='alerts', null=True, blank=True)
    target_metric = models.CharField(max_length=100, blank=True, null=True)
    
    # Notification settings
    notification_channels = models.JSONField(default=list)
    notification_recipients = models.JSONField(default=list)
    
    # Schedule
    evaluation_schedule = models.JSONField(default=dict)
    cooldown_period = models.IntegerField(default=300)  # seconds
    
    # Status
    is_active = models.BooleanField(default=True)
    current_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # History
    last_triggered = models.DateTimeField(null=True, blank=True)
    trigger_count = models.IntegerField(default=0)
    
    # Auto-resolution
    auto_resolve = models.BooleanField(default=False)
    auto_resolve_conditions = models.JSONField(default=dict)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_alerts')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='alerts')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'alert_systems'
        indexes = [
            models.Index(fields=['is_active', 'current_status']),
            models.Index(fields=['severity']),
            models.Index(fields=['last_triggered']),
        ]

    def __str__(self):
        return f"Alert: {self.name}"


class AlertExecution(models.Model):
    """Alert execution history"""
    alert = models.ForeignKey(AlertSystem, on_delete=models.CASCADE, related_name='executions')
    
    # Execution details
    execution_id = models.UUIDField(default=uuid.uuid4, editable=False)
    triggered_at = models.DateTimeField(auto_now_add=True)
    
    # Evaluation results
    condition_met = models.BooleanField(default=False)
    evaluated_value = models.FloatField(null=True, blank=True)
    threshold_value = models.FloatField(null=True, blank=True)
    
    # Message
    alert_message = models.TextField()
    
    # Notifications sent
    notifications_sent = models.JSONField(default=list)
    notification_status = models.JSONField(default=dict)
    
    # Resolution
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_alerts')
    resolution_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'alert_executions'
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['alert', 'triggered_at']),
            models.Index(fields=['condition_met']),
        ]

    def __str__(self):
        return f"Alert Execution {self.execution_id} - {self.alert.name}"
