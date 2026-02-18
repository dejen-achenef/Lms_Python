from rest_framework import serializers
from .models import Category, Course, Module, Lesson, LessonProgress, CourseReview, CourseBookmark


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CourseSerializer(serializers.ModelSerializer):
    enrolled_students_count = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    total_modules = serializers.ReadOnlyField()
    total_lessons = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    instructor_name = serializers.CharField(source='instructor.full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'short_description', 'thumbnail',
            'difficulty', 'status', 'language', 'is_free', 'price',
            'estimated_hours', 'max_students', 'instructor', 'instructor_name',
            'tenant', 'category', 'category_name', 'enrolled_students_count',
            'average_rating', 'total_modules', 'total_lessons', 'is_full',
            'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = [
            'id', 'enrolled_students_count', 'average_rating', 'total_modules',
            'total_lessons', 'is_full', 'created_at', 'updated_at', 'published_at'
        ]


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'title', 'description', 'short_description', 'thumbnail',
            'difficulty', 'language', 'is_free', 'price',
            'estimated_hours', 'max_students', 'category'
        ]
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value


class ModuleSerializer(serializers.ModelSerializer):
    total_lessons = serializers.ReadOnlyField()
    completed_lessons = serializers.SerializerMethodField()
    
    class Meta:
        model = Module
        fields = [
            'id', 'title', 'description', 'order', 'course',
            'is_published', 'total_lessons', 'completed_lessons',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_completed_lessons(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.completed_lessons(request.user)
        return 0


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'description', 'content', 'lesson_type',
            'order', 'video_url', 'video_duration', 'resources',
            'is_mandatory', 'is_published', 'allow_comments',
            'module', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LessonDetailSerializer(LessonSerializer):
    progress = serializers.SerializerMethodField()
    bookmarks = serializers.SerializerMethodField()
    
    class Meta(LessonSerializer.Meta):
        fields = LessonSerializer.Meta.fields + ['progress', 'bookmarks']
    
    def get_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = obj.progress.get(user=request.user)
                return {
                    'is_completed': progress.is_completed,
                    'completion_percentage': progress.completion_percentage,
                    'watch_time': progress.watch_time,
                    'last_position': progress.last_position
                }
            except LessonProgress.DoesNotExist:
                return {
                    'is_completed': False,
                    'completion_percentage': 0,
                    'watch_time': 0,
                    'last_position': 0
                }
        return None
    
    def get_bookmarks(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            bookmarks = obj.bookmarks.filter(user=request.user)
            return CourseBookmarkSerializer(bookmarks, many=True).data
        return []


class LessonProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    
    class Meta:
        model = LessonProgress
        fields = [
            'id', 'lesson', 'lesson_title', 'is_completed',
            'completion_percentage', 'watch_time', 'last_position',
            'started_at', 'completed_at', 'updated_at'
        ]
        read_only_fields = ['id', 'started_at', 'updated_at']


class LessonProgressUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = [
            'completion_percentage', 'watch_time', 'last_position'
        ]
    
    def validate_completion_percentage(self, value):
        if not 0 <= value <= 100:
            raise serializers.ValidationError("Completion percentage must be between 0 and 100.")
        return value


class CourseReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = CourseReview
        fields = [
            'id', 'user', 'user_name', 'course', 'rating', 'comment',
            'is_public', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CourseBookmarkSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    
    class Meta:
        model = CourseBookmark
        fields = [
            'id', 'lesson', 'lesson_title', 'position', 'note', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
