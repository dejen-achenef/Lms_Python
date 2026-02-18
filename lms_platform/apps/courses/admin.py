from django.contrib import admin
from .models import Category, Course, Module, Lesson, LessonProgress, CourseReview, CourseBookmark


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant', 'parent', 'created_at']
    list_filter = ['tenant', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    ordering = ['order']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'tenant', 'status', 'difficulty', 'is_free', 'price', 'created_at']
    list_filter = ['status', 'difficulty', 'is_free', 'tenant', 'created_at']
    search_fields = ['title', 'description', 'instructor__email']
    ordering = ['-created_at']
    inlines = [ModuleInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'short_description', 'thumbnail')
        }),
        ('Course Details', {
            'fields': ('difficulty', 'status', 'language', 'category')
        }),
        ('Pricing', {
            'fields': ('is_free', 'price')
        }),
        ('Duration & Capacity', {
            'fields': ('estimated_hours', 'max_students')
        }),
        ('Relations', {
            'fields': ('instructor', 'tenant')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at', 'published_at']


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    ordering = ['order']


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'is_published', 'created_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'description', 'course__title']
    ordering = ['course', 'order']
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'lesson_type', 'order', 'is_published', 'is_mandatory', 'created_at']
    list_filter = ['lesson_type', 'is_published', 'is_mandatory', 'created_at']
    search_fields = ['title', 'description', 'module__title']
    ordering = ['module', 'order']


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'is_completed', 'completion_percentage', 'watch_time', 'updated_at']
    list_filter = ['is_completed', 'created_at', 'updated_at']
    search_fields = ['user__email', 'lesson__title']
    ordering = ['-updated_at']


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'rating', 'is_public', 'created_at']
    list_filter = ['rating', 'is_public', 'created_at']
    search_fields = ['user__email', 'course__title', 'comment']
    ordering = ['-created_at']


@admin.register(CourseBookmark)
class CourseBookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'position', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'lesson__title', 'note']
    ordering = ['-created_at']
