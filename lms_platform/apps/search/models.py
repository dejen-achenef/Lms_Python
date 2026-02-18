from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import json

User = get_user_model()


class SearchIndex(models.Model):
    """Advanced search index for all content types"""
    CONTENT_TYPES = [
        ('course', 'Course'),
        ('lesson', 'Lesson'),
        ('quiz', 'Quiz'),
        ('user', 'User'),
        ('document', 'Document'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('forum_post', 'Forum Post'),
        ('announcement', 'Announcement'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Content reference
    content_type = models.CharField(max_length=30, choices=CONTENT_TYPES)
    content_id = models.CharField(max_length=255)
    content_version = models.IntegerField(default=1)
    
    # Searchable content
    title = models.TextField()
    description = models.TextField()
    content = models.TextField()
    tags = models.JSONField(default=list)
    keywords = models.JSONField(default=list)
    
    # Metadata
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='searchable_content', null=True, blank=True)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='search_index')
    
    # Categorization
    category = models.CharField(max_length=100, blank=True, null=True)
    subcategory = models.CharField(max_length=100, blank=True, null=True)
    subject = models.CharField(max_length=100, blank=True, null=True)
    difficulty_level = models.CharField(max_length=20, blank=True, null=True)
    
    # Engagement metrics
    view_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    review_count = models.IntegerField(default=0)
    
    # Quality indicators
    content_quality_score = models.FloatField(default=0.0)
    relevance_score = models.FloatField(default=0.0)
    popularity_score = models.FloatField(default=0.0)
    
    # Timing
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    # Access control
    is_public = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    access_level = models.CharField(max_length=20, default='public')  # public, authenticated, premium, restricted
    
    # Language and locale
    language = models.CharField(max_length=10, default='en')
    locale = models.CharField(max_length=10, blank=True, null=True)
    
    # Search optimization
    search_vector = models.TextField(blank=True, null=True)  # For full-text search
    search_boost = models.FloatField(default=1.0)
    
    # External references
    external_url = models.URLField(blank=True, null=True)
    thumbnail_url = models.URLField(blank=True, null=True)
    
    # Custom fields
    custom_attributes = models.JSONField(default=dict)
    
    indexed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'search_index'
        unique_together = ['content_type', 'content_id', 'content_version']
        indexes = [
            models.Index(fields=['content_type', 'is_active']),
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['category', 'subcategory']),
            models.Index(fields=['difficulty_level']),
            models.Index(fields=['language']),
            models.Index(fields=['created_at']),
            models.Index(fields=['popularity_score']),
        ]

    def __str__(self):
        return f"{self.content_type}:{self.content_id} - {self.title}"


class SearchQuery(models.Model):
    """Search query tracking and analytics"""
    QUERY_TYPES = [
        ('simple', 'Simple Search'),
        ('advanced', 'Advanced Search'),
        ('filtered', 'Filtered Search'),
        ('semantic', 'Semantic Search'),
        ('voice', 'Voice Search'),
        ('image', 'Image Search'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_queries', null=True, blank=True)
    
    # Query details
    query_type = models.CharField(max_length=20, choices=QUERY_TYPES, default='simple')
    query_text = models.TextField()
    query_hash = models.CharField(max_length=64)  # SHA-256 for deduplication
    
    # Filters and parameters
    filters = models.JSONField(default=dict)
    sort_by = models.CharField(max_length=50, blank=True, null=True)
    sort_order = models.CharField(max_length=10, default='desc')
    page = models.IntegerField(default=1)
    page_size = models.IntegerField(default=20)
    
    # Results
    total_results = models.IntegerField(default=0)
    result_ids = models.JSONField(default=list)  # Top result IDs
    clicked_results = models.JSONField(default=list)  # Clicked result IDs
    
    # Performance
    query_time = models.FloatField(default=0.0)  # milliseconds
    cache_hit = models.BooleanField(default=False)
    
    # Context
    search_context = models.CharField(max_length=100, blank=True, null=True)  # Where search was initiated
    device_type = models.CharField(max_length=20, blank=True, null=True)
    
    # Analytics
    session_id = models.CharField(max_length=255, blank=True, null=True)
    referrer = models.URLField(blank=True, null=True)
    
    # Language
    query_language = models.CharField(max_length=10, default='en')
    
    # AI enhancements
    intent_detected = models.CharField(max_length=100, blank=True, null=True)
    entities_extracted = models.JSONField(default=list)
    semantic_similarity = models.FloatField(null=True, blank=True)
    
    # Satisfaction
    user_satisfaction = models.IntegerField(null=True, blank=True)  # 1-5 rating
    feedback = models.TextField(blank=True, null=True)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='search_queries')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'search_queries'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['query_hash']),
            models.Index(fields=['query_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['total_results']),
        ]

    def __str__(self):
        return f"Query: {self.query_text[:50]}... ({self.user.email if self.user else 'Anonymous'})"


class SearchSuggestion(models.Model):
    """Search autocomplete and suggestions"""
    SUGGESTION_TYPES = [
        ('autocomplete', 'Autocomplete'),
        ('did_you_mean', 'Did You Mean'),
        ('related', 'Related Search'),
        ('trending', 'Trending'),
        ('popular', 'Popular'),
        ('personalized', 'Personalized'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    suggestion_text = models.CharField(max_length=255)
    suggestion_type = models.CharField(max_length=20, choices=SUGGESTION_TYPES)
    
    # Metrics
    frequency = models.IntegerField(default=0)  # How often this is searched
    click_through_rate = models.FloatField(default=0.0)
    success_rate = models.FloatField(default=0.0)  # Searches that led to results
    
    # Context
    context = models.JSONField(default=dict)
    target_audience = models.JSONField(default=list)
    
    # Personalization
    user_segments = models.JSONField(default=list)
    personalization_score = models.FloatField(default=0.0)
    
    # Quality
    quality_score = models.FloatField(default=0.0)
    admin_approved = models.BooleanField(default=False)
    
    # Timing
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    trending_since = models.DateTimeField(null=True, blank=True)
    
    # Language
    language = models.CharField(max_length=10, default='en')
    
    # Boost factors
    boost_factor = models.FloatField(default=1.0)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='search_suggestions')
    
    class Meta:
        db_table = 'search_suggestions'
        indexes = [
            models.Index(fields=['suggestion_type', 'frequency']),
            models.Index(fields=['language', 'frequency']),
            models.Index(fields=['trending_since']),
            models.Index(fields=['quality_score']),
        ]

    def __str__(self):
        return f"{self.suggestion_text} ({self.suggestion_type})"


class SearchAnalytics(models.Model):
    """Search analytics and insights"""
    ANALYSIS_TYPES = [
        ('daily', 'Daily Summary'),
        ('weekly', 'Weekly Summary'),
        ('monthly', 'Monthly Summary'),
        ('trending', 'Trending Analysis'),
        ('performance', 'Performance Analysis'),
        ('user_behavior', 'User Behavior Analysis'),
        ('content_gap', 'Content Gap Analysis'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis_type = models.CharField(max_length=30, choices=ANALYSIS_TYPES)
    
    # Time period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Search metrics
    total_searches = models.IntegerField(default=0)
    unique_searchers = models.IntegerField(default=0)
    average_query_length = models.FloatField(default=0.0)
    average_results_per_search = models.FloatField(default=0.0)
    
    # Performance metrics
    average_query_time = models.FloatField(default=0.0)  # milliseconds
    cache_hit_rate = models.FloatField(default=0.0)
    zero_results_rate = models.FloatField(default=0.0)
    
    # User satisfaction
    average_satisfaction = models.FloatField(default=0.0)
    click_through_rate = models.FloatField(default=0.0)
    bounce_rate = models.FloatField(default=0.0)
    
    # Top queries
    top_queries = models.JSONField(default=list)
    trending_queries = models.JSONField(default=list)
    failed_queries = models.JSONField(default=list)
    
    # Content insights
    most_viewed_content = models.JSONField(default=list)
    content_gaps = models.JSONField(default=list)
    search_intent_distribution = models.JSONField(default=dict)
    
    # Device and platform breakdown
    device_breakdown = models.JSONField(default=dict)
    platform_breakdown = models.JSONField(default=dict)
    
    # Geographic distribution
    geographic_distribution = models.JSONField(default=dict)
    language_distribution = models.JSONField(default=dict)
    
    # AI insights
    search_patterns = models.JSONField(default=dict)
    user_segments = models.JSONField(default=dict)
    recommendations = models.JSONField(default=list)
    
    # Raw data
    raw_data = models.JSONField(default=dict)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='search_analytics')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'search_analytics'
        unique_together = ['analysis_type', 'period_start', 'period_end', 'tenant']
        ordering = ['-period_start']

    def __str__(self):
        return f"{self.analysis_type}: {self.period_start.date()} to {self.period_end.date()}"


class ContentRecommendation(models.Model):
    """AI-powered content recommendations"""
    RECOMMENDATION_TYPES = [
        ('collaborative', 'Collaborative Filtering'),
        ('content_based', 'Content-Based'),
        ('hybrid', 'Hybrid'),
        ('knowledge_graph', 'Knowledge Graph'),
        ('semantic', 'Semantic Similarity'),
        ('popularity', 'Popularity-Based'),
        ('trending', 'Trending'),
        ('personalized', 'Personalized'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_recommendations')
    
    # Recommendation details
    recommendation_type = models.CharField(max_length=30, choices=RECOMMENDATION_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Recommended content
    recommended_items = models.JSONField(default=list)  # List of content_type:content_id
    
    # Scoring
    relevance_score = models.FloatField(default=0.0)
    confidence_score = models.FloatField(default=0.0)
    diversity_score = models.FloatField(default=0.0)
    novelty_score = models.FloatField(default=0.0)
    
    # Context
    context = models.JSONField(default=dict)
    trigger_event = models.CharField(max_length=100, blank=True, null=True)
    
    # Personalization factors
    user_preferences = models.JSONField(default=dict)
    learning_history = models.JSONField(default=dict)
    skill_level = models.CharField(max_length=20, blank=True, null=True)
    
    # Business rules
    business_rules = models.JSONField(default=dict)
    boost_factors = models.JSONField(default=dict)
    
    # A/B testing
    experiment_id = models.CharField(max_length=100, blank=True, null=True)
    variant = models.CharField(max_length=50, blank=True, null=True)
    
    # Interaction tracking
    viewed = models.BooleanField(default=False)
    clicked = models.BooleanField(default=False)
    converted = models.BooleanField(default=False)
    
    viewed_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    converted_at = models.DateTimeField(null=True, blank=True)
    
    # Feedback
    user_feedback = models.IntegerField(null=True, blank=True)  # 1-5 rating
    feedback_comments = models.TextField(blank=True, null=True)
    
    # Expiration
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    
    # AI model info
    model_version = models.CharField(max_length=50, blank=True, null=True)
    model_confidence = models.FloatField(default=0.0)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='content_recommendations')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'content_recommendations'
        indexes = [
            models.Index(fields=['user', 'valid_from']),
            models.Index(fields=['recommendation_type']),
            models.Index(fields=['relevance_score']),
            models.Index(fields=['valid_until']),
        ]

    def __str__(self):
        return f"Recommendation for {self.user.email}: {self.title}"


class KnowledgeGraph(models.Model):
    """Knowledge graph for semantic search and recommendations"""
    NODE_TYPES = [
        ('concept', 'Concept'),
        ('skill', 'Skill'),
        ('topic', 'Topic'),
        ('course', 'Course'),
        ('lesson', 'Lesson'),
        ('career', 'Career'),
        ('industry', 'Industry'),
        ('tool', 'Tool'),
    ]
    
    RELATIONSHIP_TYPES = [
        ('prerequisite', 'Prerequisite'),
        ('related_to', 'Related To'),
        ('teaches', 'Teaches'),
        ('requires', 'Requires'),
        ('similar_to', 'Similar To'),
        ('part_of', 'Part Of'),
        ('leads_to', 'Leads To'),
        ('used_in', 'Used In'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Nodes
    node_type = models.CharField(max_length=30, choices=NODE_TYPES)
    node_id = models.CharField(max_length=255)
    node_label = models.CharField(max_length=255)
    node_description = models.TextField(blank=True, null=True)
    
    # Properties
    properties = models.JSONField(default=dict)
    metadata = models.JSONField(default=dict)
    
    # Embeddings for semantic similarity
    embedding = models.JSONField(default=list)  # Vector representation
    embedding_model = models.CharField(max_length=100, blank=True, null=True)
    
    # Relationships
    relationships = models.JSONField(default=list)  # List of relationship objects
    
    # Analytics
    connection_count = models.IntegerField(default=0)
    strength = models.FloatField(default=0.0)
    centrality = models.FloatField(default=0.0)
    
    # Quality
    confidence = models.FloatField(default=0.0)
    verified = models.BooleanField(default=False)
    
    # Language
    language = models.CharField(max_length=10, default='en')
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='knowledge_graph')
    
    class Meta:
        db_table = 'knowledge_graph'
        unique_together = ['node_type', 'node_id', 'language']
        indexes = [
            models.Index(fields=['node_type', 'language']),
            models.Index(fields=['strength']),
            models.Index(fields=['centrality']),
            models.Index(fields=['confidence']),
        ]

    def __str__(self):
        return f"{self.node_type}: {self.node_label}"


class SearchConfiguration(models.Model):
    """Search engine configuration and tuning"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Search engine settings
    engine = models.CharField(max_length=50, default='elasticsearch')
    index_name = models.CharField(max_length=100)
    index_settings = models.JSONField(default=dict)
    
    # Ranking and scoring
    ranking_algorithm = models.CharField(max_length=50, default='bm25')
    scoring_factors = models.JSONField(default=dict)
    boost_config = models.JSONField(default=dict)
    
    # Synonyms and expansions
    synonyms = models.JSONField(default=list)
    expansions = models.JSONField(default=list)
    stop_words = models.JSONField(default=list)
    
    # Language processing
    analyzers = models.JSONField(default=dict)
    tokenizers = models.JSONField(default=dict)
    filters = models.JSONField(default=dict)
    
    # Performance tuning
    max_results = models.IntegerField(default=1000)
    query_timeout = models.IntegerField(default=30)  # seconds
    cache_size = models.BigIntegerField(default=1073741824)  # 1GB
    
    # AI/ML settings
    semantic_search_enabled = models.BooleanField(default=False)
    embedding_model = models.CharField(max_length=100, blank=True, null=True)
    similarity_threshold = models.FloatField(default=0.7)
    
    # Personalization
    personalization_enabled = models.BooleanField(default=True)
    user_behavior_weight = models.FloatField(default=0.3)
    content_quality_weight = models.FloatField(default=0.4)
    popularity_weight = models.FloatField(default=0.3)
    
    # Autocomplete
    autocomplete_enabled = models.BooleanField(default=True)
    autocomplete_max_suggestions = models.IntegerField(default=10)
    autocomplete_min_characters = models.IntegerField(default=2)
    
    # Analytics
    analytics_enabled = models.BooleanField(default=True)
    query_logging_enabled = models.BooleanField(default=True)
    click_tracking_enabled = models.BooleanField(default=True)
    
    # Business rules
    business_rules = models.JSONField(default=dict)
    content_filters = models.JSONField(default=dict)
    
    # Status
    is_active = models.BooleanField(default=True)
    version = models.CharField(max_length=20, default='1.0.0')
    
    # Metadata
    description = models.TextField(blank=True, null=True)
    configuration = models.JSONField(default=dict)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='search_configurations')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'search_configurations'

    def __str__(self):
        return f"Search Config: {self.index_name} ({self.engine})"
