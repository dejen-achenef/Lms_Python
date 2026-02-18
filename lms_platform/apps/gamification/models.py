from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import json

User = get_user_model()


class Badge(models.Model):
    """Achievement badges for gamification"""
    BADGE_TYPES = [
        ('course_completion', 'Course Completion'),
        ('streak', 'Learning Streak'),
        ('participation', 'Participation'),
        ('achievement', 'Special Achievement'),
        ('milestone', 'Milestone'),
        ('skill', 'Skill Mastery'),
        ('social', 'Social Learning'),
        ('leadership', 'Leadership'),
    ]
    
    RARITY_LEVELS = [
        ('common', 'Common'),
        ('uncommon', 'Uncommon'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES)
    rarity = models.CharField(max_length=20, choices=RARITY_LEVELS, default='common')
    
    # Visual design
    icon = models.ImageField(upload_to='badges/')
    color = models.CharField(max_length=7, default='#FFD700')  # Gold color
    animation = models.CharField(max_length=50, blank=True, null=True)
    
    # Award criteria
    criteria = models.JSONField(default=dict)  # Specific conditions to earn badge
    points_value = models.IntegerField(default=10)
    
    # Availability
    is_active = models.BooleanField(default=True)
    is_secret = models.BooleanField(default=False)  # Hidden until earned
    limited_quantity = models.BooleanField(default=False)
    max_awards = models.IntegerField(null=True, blank=True)
    
    # Metadata
    tags = models.JSONField(default=list)
    category = models.CharField(max_length=50, blank=True, null=True)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='badges')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_badges')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'badges'
        ordering = ['rarity', 'name']

    def __str__(self):
        return f"{self.name} ({self.rarity})"

    @property
    def award_count(self):
        return self.user_badges.count()

    @property
    def is_available(self):
        if not self.is_active:
            return False
        if self.limited_quantity and self.max_awards and self.award_count >= self.max_awards:
            return False
        return True


class UserBadge(models.Model):
    """Badges awarded to users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='user_badges')
    
    # Award details
    awarded_at = models.DateTimeField(auto_now_add=True)
    awarded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='awarded_badges')
    progress_data = models.JSONField(default=dict)  # Progress toward earning the badge
    
    # Display settings
    is_displayed = models.BooleanField(default=True)
    is_pinned = models.BooleanField(default=False)
    
    # Sharing
    shared_publicly = models.BooleanField(default=False)
    shared_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'user_badges'
        unique_together = ['user', 'badge']
        ordering = ['-awarded_at']

    def __str__(self):
        return f"{self.user.email} - {self.badge.name}"


class Leaderboard(models.Model):
    """Leaderboards for competitions and rankings"""
    LEADERBOARD_TYPES = [
        ('points', 'Points Leaderboard'),
        ('courses', 'Courses Completed'),
        ('streak', 'Learning Streak'),
        ('participation', 'Participation'),
        ('skills', 'Skill Points'),
        ('time', 'Time Spent Learning'),
        ('custom', 'Custom Metric'),
    ]
    
    TIME_PERIODS = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
        ('all_time', 'All Time'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    leaderboard_type = models.CharField(max_length=20, choices=LEADERBOARD_TYPES)
    time_period = models.CharField(max_length=20, choices=TIME_PERIODS, default='monthly')
    
    # Settings
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    max_entries = models.IntegerField(default=100)
    
    # Calculation rules
    scoring_rules = models.JSONField(default=dict)
    reset_schedule = models.CharField(max_length=50, blank=True, null=True)
    
    # Related objects
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='leaderboards', null=True, blank=True)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='leaderboards')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'leaderboards'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} ({self.time_period})"

    def get_top_users(self, limit=10):
        """Get top users for this leaderboard"""
        return self.entries.filter(rank__lte=limit).order_by('rank')


class LeaderboardEntry(models.Model):
    """Individual entries in leaderboards"""
    leaderboard = models.ForeignKey(Leaderboard, on_delete=models.CASCADE, related_name='entries')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaderboard_entries')
    
    # Ranking data
    rank = models.IntegerField()
    score = models.FloatField(default=0.0)
    previous_rank = models.IntegerField(null=True, blank=True)
    
    # Additional metrics
    metric_data = models.JSONField(default=dict)
    
    # Timestamps
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'leaderboard_entries'
        unique_together = ['leaderboard', 'user', 'period_start', 'period_end']
        ordering = ['rank']

    def __str__(self):
        return f"#{self.rank} {self.user.email} - {self.score}"


class PointsSystem(models.Model):
    """Points and rewards system"""
    POINT_TYPES = [
        ('course_completion', 'Course Completion'),
        ('lesson_completion', 'Lesson Completion'),
        ('quiz_score', 'Quiz Score'),
        ('assignment', 'Assignment Submission'),
        ('participation', 'Forum Participation'),
        ('helping_others', 'Helping Others'),
        ('streak', 'Daily Streak'),
        ('bonus', 'Bonus Points'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='points')
    points_type = models.CharField(max_length=30, choices=POINT_TYPES)
    points = models.IntegerField()
    
    # Related objects
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, null=True, blank=True)
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE, null=True, blank=True)
    
    # Metadata
    description = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'points_system'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email}: +{self.points} ({self.points_type})"


class Achievement(models.Model):
    """Complex achievements with multiple criteria"""
    ACHIEVEMENT_TYPES = [
        ('progressive', 'Progressive'),
        ('cumulative', 'Cumulative'),
        ('time_based', 'Time Based'),
        ('conditional', 'Conditional'),
        ('social', 'Social'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    
    # Criteria
    criteria = models.JSONField(default=dict)  # Complex criteria structure
    required_actions = models.JSONField(default=list)
    
    # Rewards
    points_reward = models.IntegerField(default=0)
    badge_reward = models.ForeignKey(Badge, on_delete=models.SET_NULL, null=True, blank=True)
    title_reward = models.CharField(max_length=100, blank=True, null=True)
    
    # Progress tracking
    max_progress = models.IntegerField(default=100)
    is_repeatable = models.BooleanField(default=False)
    cooldown_period = models.IntegerField(null=True, blank=True)  # in hours
    
    # Availability
    is_active = models.BooleanField(default=True)
    prerequisite_achievements = models.ManyToManyField('self', symmetrical=False, blank=True)
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='achievements')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'achievements'

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    """User progress and completion of achievements"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='user_achievements')
    
    # Progress
    progress = models.IntegerField(default=0)
    progress_data = models.JSONField(default=dict)
    
    # Completion
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    completion_count = models.IntegerField(default=0)  # For repeatable achievements
    
    # Rewards
    points_awarded = models.IntegerField(default=0)
    badge_awarded = models.ForeignKey(UserBadge, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_achievements'
        unique_together = ['user', 'achievement']

    def __str__(self):
        return f"{self.user.email} - {self.achievement.name} ({self.progress}%)"

    def update_progress(self, increment=1, data=None):
        """Update achievement progress"""
        if self.is_completed and not self.achievement.is_repeatable:
            return
        
        self.progress = min(self.progress + increment, self.achievement.max_progress)
        if data:
            self.progress_data.update(data)
        
        if self.progress >= self.achievement.max_progress and not self.is_completed:
            self.complete_achievement()
        
        self.save()

    def complete_achievement(self):
        """Mark achievement as completed and award rewards"""
        self.is_completed = True
        self.completed_at = timezone.now()
        self.completion_count += 1
        
        # Award points
        if self.achievement.points_reward > 0:
            PointsSystem.objects.create(
                user=self.user,
                points_type='bonus',
                points=self.achievement.points_reward,
                description=f"Achievement: {self.achievement.name}"
            )
            self.points_awarded = self.achievement.points_reward
        
        # Award badge
        if self.achievement.badge_reward:
            badge, created = UserBadge.objects.get_or_create(
                user=self.user,
                badge=self.achievement.badge_reward
            )
            self.badge_awarded = badge


class LearningStreak(models.Model):
    """Learning streak tracking"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learning_streak')
    
    # Current streak
    current_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    
    # Best streaks
    longest_streak = models.IntegerField(default=0)
    longest_streak_start = models.DateField(null=True, blank=True)
    longest_streak_end = models.DateField(null=True, blank=True)
    
    # Streak history
    streak_history = models.JSONField(default=list)
    
    # Milestones
    milestones_reached = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learning_streaks'

    def __str__(self):
        return f"{self.user.email}: {self.current_streak} day streak"

    def update_streak(self, activity_date=None):
        """Update learning streak based on activity"""
        if not activity_date:
            activity_date = timezone.now().date()
        
        if self.last_activity_date:
            days_diff = (activity_date - self.last_activity_date).days
            
            if days_diff == 1:
                # Continue streak
                self.current_streak += 1
            elif days_diff > 1:
                # Streak broken
                if self.current_streak > self.longest_streak:
                    self.longest_streak = self.current_streak
                
                self.current_streak = 1
            # days_diff == 0 means same day, no change
        else:
            # First activity
            self.current_streak = 1
        
        self.last_activity_date = activity_date
        
        # Check for milestones
        if self.current_streak in [7, 30, 100, 365] and str(self.current_streak) not in self.milestones_reached:
            self.milestones_reached.append(str(self.current_streak))
            self.award_streak_milestone(self.current_streak)
        
        self.save()

    def award_streak_milestone(self, days):
        """Award rewards for streak milestones"""
        from apps.notifications.tasks import send_bulk_notifications
        
        # Award points
        points = days * 10  # 10 points per day
        PointsSystem.objects.create(
            user=self.user,
            points_type='streak',
            points=points,
            description=f"{days} day learning streak!"
        )
        
        # Check for streak badge
        badge_name = f"{days} Day Streak"
        try:
            badge = Badge.objects.get(name=badge_name, tenant=self.user.tenant)
            UserBadge.objects.get_or_create(user=self.user, badge=badge)
        except Badge.DoesNotExist:
            pass


class Challenge(models.Model):
    """Learning challenges and competitions"""
    CHALLENGE_TYPES = [
        ('individual', 'Individual Challenge'),
        ('team', 'Team Challenge'),
        ('course', 'Course Challenge'),
        ('time_based', 'Time-Based Challenge'),
        ('skill_based', 'Skill-Based Challenge'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Timing
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Participation
    max_participants = models.IntegerField(null=True, blank=True)
    team_size = models.IntegerField(null=True, blank=True)
    require_approval = models.BooleanField(default=False)
    
    # Rewards
    points_reward = models.IntegerField(default=0)
    badge_reward = models.ForeignKey(Badge, on_delete=models.SET_NULL, null=True, blank=True)
    prize_description = models.TextField(blank=True, null=True)
    
    # Rules and criteria
    rules = models.JSONField(default=list)
    judging_criteria = models.JSONField(default=list)
    
    # Related objects
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='challenges', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_challenges')
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='challenges')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'challenges'
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        now = timezone.now()
        return self.status == 'active' and self.start_date <= now <= self.end_date


class ChallengeParticipant(models.Model):
    """Participants in challenges"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='challenge_participations')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='participants')
    
    # Status
    is_approved = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    # Progress
    progress_data = models.JSONField(default=dict)
    score = models.FloatField(default=0.0)
    rank = models.IntegerField(null=True, blank=True)
    
    # Team info (for team challenges)
    team_name = models.CharField(max_length=100, blank=True, null=True)
    team_members = models.ManyToManyField(User, related_name='team_memberships', blank=True)
    
    # Submission
    submission_data = models.JSONField(default=dict)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'challenge_participants'
        unique_together = ['user', 'challenge']

    def __str__(self):
        return f"{self.user.email} in {self.challenge.title}"
