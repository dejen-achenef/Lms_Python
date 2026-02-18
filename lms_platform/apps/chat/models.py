from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import json

User = get_user_model()


class ChatRoom(models.Model):
    """Real-time chat rooms for courses, groups, and direct messages"""
    ROOM_TYPES = [
        ('course', 'Course Discussion'),
        ('lesson', 'Lesson Q&A'),
        ('group', 'Study Group'),
        ('direct', 'Direct Message'),
        ('announcement', 'Announcement'),
        ('support', 'Support Chat'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    
    # Related objects
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='chat_rooms', null=True, blank=True)
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE, related_name='chat_rooms', null=True, blank=True)
    
    # Settings
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    allow_file_sharing = models.BooleanField(default=True)
    allow_voice_messages = models.BooleanField(default=True)
    allow_screen_sharing = models.BooleanField(default=False)
    
    # Moderation
    require_approval = models.BooleanField(default=False)
    auto_moderation = models.BooleanField(default=True)
    
    # Metadata
    tags = models.JSONField(default=list)
    custom_settings = models.JSONField(default=dict)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_rooms'
        ordering = ['-updated_at']

    def __str__(self):
        return self.name

    @property
    def participant_count(self):
        return self.participants.filter(is_active=True).count()

    @property
    def message_count(self):
        return self.messages.count()

    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()


class ChatParticipant(models.Model):
    """Participants in chat rooms"""
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('member', 'Member'),
        ('guest', 'Guest'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_participations')
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='participants')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    
    # Status
    is_active = models.BooleanField(default=True)
    is_muted = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    
    # Permissions
    can_send_messages = models.BooleanField(default=True)
    can_send_files = models.BooleanField(default=True)
    can_delete_messages = models.BooleanField(default=False)
    can_pin_messages = models.BooleanField(default=False)
    
    # Activity tracking
    last_read_at = models.DateTimeField(null=True, blank=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    typing = models.BooleanField(default=False)
    typing_since = models.DateTimeField(null=True, blank=True)
    
    # Notifications
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'chat_participants'
        unique_together = ['user', 'room']
        indexes = [
            models.Index(fields=['room', 'is_active']),
            models.Index(fields=['user', 'last_activity_at']),
        ]

    def __str__(self):
        return f"{self.user.email} in {self.room.name}"

    def mark_messages_read(self):
        """Mark all messages in the room as read"""
        self.last_read_at = timezone.now()
        self.save()


class Message(models.Model):
    """Chat messages with rich content"""
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('link', 'Link Preview'),
        ('poll', 'Poll'),
        ('system', 'System Message'),
        ('announcement', 'Announcement'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    
    # Message content
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    content = models.TextField()
    
    # Rich content
    attachments = models.JSONField(default=list)
    mentions = models.ManyToManyField(User, related_name='mentioned_in', blank=True)
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Reactions
    reactions = models.JSONField(default=dict)  # {'👍': [user_ids], '❤️': [user_ids]}
    
    # Moderation
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    moderated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_messages')
    moderation_reason = models.TextField(blank=True, null=True)
    
    # Metadata
    metadata = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['room', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
            models.Index(fields=['is_pinned', 'created_at']),
        ]

    def __str__(self):
        return f"{self.sender.email}: {self.content[:50]}..."

    def add_reaction(self, user, emoji):
        """Add or remove a reaction to the message"""
        if emoji not in self.reactions:
            self.reactions[emoji] = []
        
        user_id = str(user.id)
        if user_id in self.reactions[emoji]:
            self.reactions[emoji].remove(user_id)
            if not self.reactions[emoji]:
                del self.reactions[emoji]
        else:
            self.reactions[emoji].append(user_id)
        
        self.save()


class VideoCall(models.Model):
    """Video/voice call sessions"""
    CALL_TYPES = [
        ('video', 'Video Call'),
        ('voice', 'Voice Call'),
        ('screen_share', 'Screen Share'),
        ('webinar', 'Webinar'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('starting', 'Starting'),
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Call details
    call_type = models.CharField(max_length=20, choices=CALL_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Scheduling
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    
    # Participants
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_calls')
    participants = models.ManyToManyField(User, related_name='call_participations', through='CallParticipant')
    max_participants = models.IntegerField(default=50)
    
    # Settings
    is_recorded = models.BooleanField(default=False)
    recording_url = models.URLField(blank=True, null=True)
    require_password = models.BooleanField(default=False)
    password = models.CharField(max_length=50, blank=True, null=True)
    
    # Related objects
    room = models.OneToOneField(ChatRoom, on_delete=models.CASCADE, related_name='video_call', null=True, blank=True)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='video_calls', null=True, blank=True)
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE, related_name='video_calls', null=True, blank=True)
    
    # Analytics
    duration = models.IntegerField(null=True, blank=True)  # in minutes
    peak_participants = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'video_calls'
        ordering = ['-scheduled_start']

    def __str__(self):
        return f"{self.title} ({self.call_type})"


class CallParticipant(models.Model):
    """Participants in video calls"""
    ROLE_CHOICES = [
        ('host', 'Host'),
        ('co_host', 'Co-Host'),
        ('presenter', 'Presenter'),
        ('participant', 'Participant'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    call = models.ForeignKey(VideoCall, on_delete=models.CASCADE, related_name='call_participations')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='participant')
    
    # Status
    joined_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(default=0)  # in minutes
    
    # Permissions
    can_share_screen = models.BooleanField(default=False)
    can_mute_others = models.BooleanField(default=False)
    can_record = models.BooleanField(default=False)
    
    # Connection quality
    connection_quality = models.CharField(max_length=20, default='good')
    video_enabled = models.BooleanField(default=True)
    audio_enabled = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'call_participants'
        unique_together = ['user', 'call']

    def __str__(self):
        return f"{self.user.email} in {self.call.title}"


class StudyGroup(models.Model):
    """Study groups for collaborative learning"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    # Group settings
    is_private = models.BooleanField(default=False)
    max_members = models.IntegerField(default=50)
    requires_approval = models.BooleanField(default=True)
    
    # Related objects
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='study_groups', null=True, blank=True)
    chat_room = models.OneToOneField(ChatRoom, on_delete=models.CASCADE, related_name='study_group')
    
    # Leadership
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_study_groups')
    moderators = models.ManyToManyField(User, related_name='moderated_groups', blank=True)
    
    # Metadata
    tags = models.JSONField(default=list)
    rules = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'study_groups'

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.members.filter(is_active=True).count()


class StudyGroupMember(models.Model):
    """Members of study groups"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_group_memberships')
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='members')
    
    # Status
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    role = models.CharField(max_length=20, default='member')
    
    # Activity
    last_activity = models.DateTimeField(auto_now=True)
    contribution_score = models.IntegerField(default=0)
    
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'study_group_members'
        unique_together = ['user', 'group']

    def __str__(self):
        return f"{self.user.email} in {self.group.name}"


class Whiteboard(models.Model):
    """Collaborative whiteboards for real-time collaboration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    
    # Whiteboard content
    canvas_data = models.JSONField(default=dict)
    elements = models.JSONField(default=list)  # Drawing elements
    
    # Settings
    is_public = models.BooleanField(default=False)
    allow_collaboration = models.BooleanField(default=True)
    auto_save = models.BooleanField(default=True)
    
    # Related objects
    room = models.OneToOneField(ChatRoom, on_delete=models.CASCADE, related_name='whiteboard', null=True, blank=True)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='whiteboards', null=True, blank=True)
    
    # Ownership
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_whiteboards')
    collaborators = models.ManyToManyField(User, related_name='whiteboard_collaborations', blank=True)
    
    # Version control
    version = models.IntegerField(default=1)
    last_saved_at = models.DateTimeField(auto_now=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'whiteboards'

    def __str__(self):
        return self.title


class CollaborationSession(models.Model):
    """Real-time collaboration sessions"""
    SESSION_TYPES = [
        ('whiteboard', 'Whiteboard Session'),
        ('code_review', 'Code Review'),
        ('document_edit', 'Document Editing'),
        ('brainstorm', 'Brainstorming'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES)
    
    # Session data
    session_data = models.JSONField(default=dict)
    shared_content = models.TextField(blank=True, null=True)
    
    # Participants
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_sessions')
    participants = models.ManyToManyField(User, related_name='collaboration_sessions', blank=True)
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Related objects
    room = models.OneToOneField(ChatRoom, on_delete=models.CASCADE, related_name='collaboration_session', null=True, blank=True)
    whiteboard = models.OneToOneField(Whiteboard, on_delete=models.CASCADE, related_name='collaboration_session', null=True, blank=True)
    
    class Meta:
        db_table = 'collaboration_sessions'

    def __str__(self):
        return f"{self.title} ({self.session_type})"
