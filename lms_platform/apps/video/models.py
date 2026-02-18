from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import json

User = get_user_model()


class VideoAsset(models.Model):
    """Video asset management"""
    VIDEO_TYPES = [
        ('lecture', 'Lecture'),
        ('tutorial', 'Tutorial'),
        ('presentation', 'Presentation'),
        ('demo', 'Demo'),
        ('interview', 'Interview'),
        ('webinar', 'Webinar'),
        ('promo', 'Promotional'),
        ('intro', 'Introduction'),
        ('outro', 'Outro'),
    ]
    
    STATUS_CHOICES = [
        ('uploading', 'Uploading'),
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('failed', 'Failed'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    video_type = models.CharField(max_length=20, choices=VIDEO_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploading')
    
    # Original file
    original_file = models.FileField(upload_to='videos/original/')
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField(default=0)  # bytes
    file_hash = models.CharField(max_length=64)  # SHA-256
    
    # Video properties
    duration = models.FloatField(null=True, blank=True)  # seconds
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    bitrate = models.IntegerField(null=True, blank=True)  # kbps
    frame_rate = models.FloatField(null=True, blank=True)
    
    # Encoding
    codec = models.CharField(max_length=50, blank=True, null=True)
    container = models.CharField(max_length=20, blank=True, null=True)
    
    # Audio properties
    audio_codec = models.CharField(max_length=50, blank=True, null=True)
    audio_bitrate = models.IntegerField(null=True, blank=True)
    audio_channels = models.IntegerField(null=True, blank=True)
    audio_sample_rate = models.IntegerField(null=True, blank=True)
    
    # Thumbnails
    thumbnail = models.ImageField(upload_to='videos/thumbnails/', null=True, blank=True)
    preview_gif = models.ImageField(upload_to='videos/previews/', null=True, blank=True)
    
    # Subtitles and captions
    subtitles = models.JSONField(default=list)
    auto_generated_captions = models.BooleanField(default=False)
    
    # Processing settings
    processing_config = models.JSONField(default=dict)
    
    # CDN URLs
    cdn_url = models.URLField(blank=True, null=True)
    streaming_url = models.URLField(blank=True, null=True)
    
    # Access control
    is_public = models.BooleanField(default=False)
    allowed_users = models.ManyToManyField(User, related_name='accessible_videos', blank=True)
    
    # Analytics
    view_count = models.IntegerField(default=0)
    unique_viewers = models.IntegerField(default=0)
    average_watch_time = models.FloatField(default=0.0)
    
    # Tags and metadata
    tags = models.JSONField(default=list)
    category = models.CharField(max_length=100, blank=True, null=True)
    
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_videos')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='video_assets')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'video_assets'
        indexes = [
            models.Index(fields=['video_type', 'status']),
            models.Index(fields=['uploaded_by', 'created_at']),
            models.Index(fields=['tags']),
        ]

    def __str__(self):
        return f"Video: {self.title}"


class VideoEncoding(models.Model):
    """Video encoding profiles and jobs"""
    ENCODING_TYPES = [
        ('h264', 'H.264'),
        ('h265', 'H.265/HEVC'),
        ('vp9', 'VP9'),
        ('av1', 'AV1'),
    ]
    
    QUALITY_LEVELS = [
        ('auto', 'Auto'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('ultra', 'Ultra'),
        ('4k', '4K'),
        ('8k', '8K'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    video = models.ForeignKey(VideoAsset, on_delete=models.CASCADE, related_name='encodings')
    
    # Encoding configuration
    encoding_type = models.CharField(max_length=20, choices=ENCODING_TYPES)
    quality_level = models.CharField(max_length=20, choices=QUALITY_LEVELS)
    
    # Output settings
    output_width = models.IntegerField(null=True, blank=True)
    output_height = models.IntegerField(null=True, blank=True)
    output_bitrate = models.IntegerField(null=True, blank=True)
    output_file_size = models.BigIntegerField(null=True, blank=True)
    
    # Adaptive streaming
    is_adaptive = models.BooleanField(default=False)
    bandwidth = models.IntegerField(null=True, blank=True)  # kbps
    
    # File information
    output_file = models.FileField(upload_to='videos/encoded/', null=True, blank=True)
    output_url = models.URLField(blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Progress
    progress = models.FloatField(default=0.0)  # 0.0 to 1.0
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    processing_time = models.IntegerField(null=True, blank=True)  # seconds
    
    # Error handling
    error_message = models.TextField(blank=True, null=True)
    retry_count = models.IntegerField(default=0)
    
    # Cost tracking
    processing_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'video_encodings'
        indexes = [
            models.Index(fields=['video', 'status']),
            models.Index(fields=['encoding_type', 'quality_level']),
        ]

    def __str__(self):
        return f"Encoding: {self.video.title} - {self.quality_level}"


class VideoStreaming(models.Model):
    """Video streaming configuration"""
    STREAMING_PROTOCOLS = [
        ('hls', 'HLS'),
        ('dash', 'MPEG-DASH'),
        ('rtmp', 'RTMP'),
        ('webrtc', 'WebRTC'),
        ('hds', 'HDS'),
    ]
    
    video = models.OneToOneField(VideoAsset, on_delete=models.CASCADE, related_name='streaming')
    
    # Streaming URLs
    hls_url = models.URLField(blank=True, null=True)
    dash_url = models.URLField(blank=True, null=True)
    rtmp_url = models.URLField(blank=True, null=True)
    
    # Streaming configuration
    protocols = models.JSONField(default=list)
    adaptive_bitrate = models.BooleanField(default=True)
    
    # DRM protection
    drm_enabled = models.BooleanField(default=False)
    drm_type = models.CharField(max_length=50, blank=True, null=True)
    
    # Live streaming
    is_live = models.BooleanField(default=False)
    stream_key = models.CharField(max_length=255, blank=True, null=True)
    
    # Recording
    auto_record = models.BooleanField(default=False)
    recording_url = models.URLField(blank=True, null=True)
    
    # Analytics
    stream_start_time = models.DateTimeField(null=True, blank=True)
    stream_end_time = models.DateTimeField(null=True, blank=True)
    concurrent_viewers = models.IntegerField(default=0)
    peak_viewers = models.IntegerField(default=0)
    
    # Quality settings
    max_bitrate = models.IntegerField(null=True, blank=True)
    min_bitrate = models.IntegerField(null=True, blank=True)
    
    # Geographic restrictions
    geo_restrictions = models.JSONField(default=dict)
    
    # Access control
    token_required = models.BooleanField(default=False)
    token_expiry = models.IntegerField(default=3600)  # seconds
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'video_streaming'

    def __str__(self):
        return f"Streaming: {self.video.title}"


class VideoAnalytics(models.Model):
    """Video analytics and engagement tracking"""
    ANALYTICS_TYPES = [
        ('view', 'View Tracking'),
        ('engagement', 'Engagement Metrics'),
        ('drop_off', 'Drop-off Analysis'),
        ('quality', 'Quality Metrics'),
        ('performance', 'Performance Metrics'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey(VideoAsset, on_delete=models.CASCADE, related_name='analytics')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_analytics', null=True, blank=True)
    
    # Analytics type
    analytics_type = models.CharField(max_length=30, choices=ANALYTICS_TYPES)
    
    # Session information
    session_id = models.CharField(max_length=255, blank=True, null=True)
    
    # View tracking
    view_start = models.DateTimeField()
    view_end = models.DateTimeField(null=True, blank=True)
    total_watch_time = models.FloatField(default=0.0)  # seconds
    
    # Progress tracking
    max_position = models.FloatField(default=0.0)  # seconds
    completion_percentage = models.FloatField(default=0.0)
    
    # Engagement events
    events = models.JSONField(default=list)  # List of engagement events
    
    # Quality metrics
    average_bitrate = models.FloatField(null=True, blank=True)
    buffer_events = models.IntegerField(default=0)
    error_events = models.IntegerField(default=0)
    
    # Device and browser
    device_type = models.CharField(max_length=50, blank=True, null=True)
    browser = models.CharField(max_length=100, blank=True, null=True)
    operating_system = models.CharField(max_length=100, blank=True, null=True)
    
    # Geographic
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    
    # Network
    connection_type = models.CharField(max_length=50, blank=True, null=True)
    download_speed = models.FloatField(null=True, blank=True)  # Mbps
    
    # Additional data
    metadata = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'video_analytics'
        indexes = [
            models.Index(fields=['video', 'analytics_type']),
            models.Index(fields=['user', 'view_start']),
            models.Index(fields=['session_id']),
            models.Index(fields=['view_start']),
        ]

    def __str__(self):
        return f"Analytics: {self.video.title} - {self.analytics_type}"


class VideoPlaylist(models.Model):
    """Video playlists and series"""
    PLAYLIST_TYPES = [
        ('course', 'Course Playlist'),
        ('series', 'Video Series'),
        ('collection', 'Collection'),
        ('favorites', 'Favorites'),
        ('watch_later', 'Watch Later'),
        ('featured', 'Featured'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    playlist_type = models.CharField(max_length=30, choices=PLAYLIST_TYPES)
    
    # Videos
    videos = models.ManyToManyField(VideoAsset, related_name='playlists', through='PlaylistVideo')
    
    # Ordering and settings
    auto_play = models.BooleanField(default=True)
    shuffle = models.BooleanField(default=False)
    repeat = models.BooleanField(default=False)
    
    # Access control
    is_public = models.BooleanField(default=True)
    allowed_users = models.ManyToManyField(User, related_name='accessible_playlists', blank=True)
    
    # Thumbnail
    thumbnail = models.ImageField(upload_to='playlist_thumbnails/', null=True, blank=True)
    
    # Statistics
    total_duration = models.FloatField(default=0.0)  # seconds
    view_count = models.IntegerField(default=0)
    
    # Tags
    tags = models.JSONField(default=list)
    category = models.CharField(max_length=100, blank=True, null=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_playlists')
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='video_playlists')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'video_playlists'
        indexes = [
            models.Index(fields=['playlist_type', 'is_public']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return f"Playlist: {self.title}"


class PlaylistVideo(models.Model):
    """Through model for playlist videos with ordering"""
    playlist = models.ForeignKey(VideoPlaylist, on_delete=models.CASCADE)
    video = models.ForeignKey(VideoAsset, on_delete=models.CASCADE)
    
    # Ordering
    order = models.PositiveIntegerField(default=0)
    
    # Additional settings
    auto_start = models.BooleanField(default=True)
    custom_title = models.CharField(max_length=255, blank=True, null=True)
    custom_description = models.TextField(blank=True, null=True)
    
    # Timestamp (for starting position)
    start_time = models.FloatField(default=0.0)  # seconds
    
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'playlist_videos'
        unique_together = ['playlist', 'video']
        ordering = ['order']

    def __str__(self):
        return f"{self.playlist.title} - {self.video.title}"


class VideoTranscript(models.Model):
    """Video transcripts and captions"""
    TRANSCRIPT_TYPES = [
        ('auto', 'Auto-generated'),
        ('manual', 'Manual'),
        ('edited', 'Edited Auto'),
        ('professional', 'Professional'),
    ]
    
    LANGUAGES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('it', 'Italian'),
        ('pt', 'Portuguese'),
        ('ru', 'Russian'),
        ('ja', 'Japanese'),
        ('ko', 'Korean'),
        ('zh', 'Chinese'),
    ]
    
    video = models.ForeignKey(VideoAsset, on_delete=models.CASCADE, related_name='transcripts')
    
    # Transcript content
    language = models.CharField(max_length=10, choices=LANGUAGES)
    transcript_type = models.CharField(max_length=20, choices=TRANSCRIPT_TYPES)
    
    # Text content
    content = models.TextField()
    formatted_content = models.TextField(blank=True, null=True)  # With timestamps
    
    # Timestamps
    timestamps = models.JSONField(default=list)  # List of {time, text} objects
    
    # Confidence and quality
    confidence_score = models.FloatField(default=0.0)  # 0.0 to 1.0
    accuracy_score = models.FloatField(default=0.0)  # 0.0 to 1.0
    
    # Status
    is_complete = models.BooleanField(default=False)
    is_reviewed = models.BooleanField(default=False)
    
    # Review information
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_transcripts')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Export formats
    srt_content = models.TextField(blank=True, null=True)
    vtt_content = models.TextField(blank=True, null=True)
    
    # Cost tracking
    generation_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'video_transcripts'
        unique_together = ['video', 'language']
        indexes = [
            models.Index(fields=['language', 'is_complete']),
        ]

    def __str__(self):
        return f"Transcript: {self.video.title} ({self.language})"


class VideoChapter(models.Model):
    """Video chapters and markers"""
    video = models.ForeignKey(VideoAsset, on_delete=models.CASCADE, related_name='chapters')
    
    # Chapter information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Timing
    start_time = models.FloatField()  # seconds
    end_time = models.FloatField(null=True, blank=True)  # seconds
    
    # Thumbnail
    thumbnail = models.ImageField(upload_to='chapter_thumbnails/', null=True, blank=True)
    
    # Tags
    tags = models.JSONField(default=list)
    
    # Ordering
    order = models.PositiveIntegerField(default=0)
    
    # Navigation
    is_skippable = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'video_chapters'
        ordering = ['order']

    def __str__(self):
        return f"Chapter: {self.title} ({self.start_time}s)"


class VideoComment(models.Model):
    """Video comments and annotations"""
    COMMENT_TYPES = [
        ('comment', 'Comment'),
        ('question', 'Question'),
        ('annotation', 'Annotation'),
        ('correction', 'Correction'),
        ('timestamp', 'Timestamp Note'),
    ]
    
    video = models.ForeignKey(VideoAsset, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_comments')
    
    # Comment content
    comment_type = models.CharField(max_length=20, choices=COMMENT_TYPES)
    content = models.TextField()
    
    # Timestamp (for timestamped comments)
    timestamp = models.FloatField(null=True, blank=True)  # seconds
    
    # Replies
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Moderation
    is_approved = models.BooleanField(default=True)
    moderated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_video_comments')
    moderated_at = models.DateTimeField(null=True, blank=True)
    
    # Engagement
    like_count = models.IntegerField(default=0)
    reply_count = models.IntegerField(default=0)
    
    # Status
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'video_comments'
        ordering = ['timestamp', 'created_at']
        indexes = [
            models.Index(fields=['video', 'timestamp']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['is_approved', 'created_at']),
        ]

    def __str__(self):
        return f"Comment by {self.user.email} on {self.video.title}"
