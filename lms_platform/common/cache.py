from django.core.cache import cache
from django.conf import settings
from functools import wraps
import hashlib
import json


def cache_key(*args, **kwargs):
    """Generate a cache key from function arguments"""
    key_data = {
        'args': args,
        'kwargs': sorted(kwargs.items())
    }
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_string.encode()).hexdigest()


def cache_result(timeout=300, key_prefix=''):
    """
    Decorator to cache function results
    Usage:
    @cache_result(timeout=60*15, key_prefix='user_profile')
    def get_user_profile(user_id):
        # Expensive operation
        return UserProfile.objects.get(user_id=user_id)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key_full = f"{key_prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            result = cache.get(cache_key_full)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key_full, result, timeout)
            return result
        
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern):
    """
    Invalidate cache keys matching a pattern
    Note: This requires redis backend for pattern matching
    """
    if hasattr(cache, 'delete_pattern'):
        cache.delete_pattern(pattern)
    else:
        # Fallback for other cache backends
        # This is less efficient as it requires iterating through keys
        pass


class CourseCacheManager:
    """Cache manager for course-related data"""
    
    @staticmethod
    def get_course_cache_key(course_id):
        return f"course:{course_id}"
    
    @staticmethod
    def get_course_progress_cache_key(user_id, course_id):
        return f"course_progress:{user_id}:{course_id}"
    
    @staticmethod
    def get_user_enrollments_cache_key(user_id):
        return f"user_enrollments:{user_id}"
    
    @staticmethod
    def cache_course(course, timeout=300):
        """Cache course data"""
        cache_key = CourseCacheManager.get_course_cache_key(course.id)
        course_data = {
            'id': str(course.id),
            'title': course.title,
            'description': course.description,
            'short_description': course.short_description,
            'thumbnail': course.thumbnail.url if course.thumbnail else None,
            'difficulty': course.difficulty,
            'status': course.status,
            'price': str(course.price),
            'is_free': course.is_free,
            'estimated_hours': course.estimated_hours,
            'instructor_id': str(course.instructor.id),
            'instructor_name': course.instructor.full_name,
            'enrolled_students_count': course.enrolled_students_count,
            'average_rating': course.average_rating,
            'total_modules': course.total_modules,
            'total_lessons': course.total_lessons,
            'is_full': course.is_full,
        }
        cache.set(cache_key, course_data, timeout)
    
    @staticmethod
    def get_cached_course(course_id):
        """Get cached course data"""
        cache_key = CourseCacheManager.get_course_cache_key(course_id)
        return cache.get(cache_key)
    
    @staticmethod
    def invalidate_course_cache(course_id):
        """Invalidate course cache"""
        cache_key = CourseCacheManager.get_course_cache_key(course_id)
        cache.delete(cache_key)
    
    @staticmethod
    def cache_user_progress(user_id, course_id, progress_data, timeout=300):
        """Cache user course progress"""
        cache_key = CourseCacheManager.get_course_progress_cache_key(user_id, course_id)
        cache.set(cache_key, progress_data, timeout)
    
    @staticmethod
    def get_cached_user_progress(user_id, course_id):
        """Get cached user course progress"""
        cache_key = CourseCacheManager.get_course_progress_cache_key(user_id, course_id)
        return cache.get(cache_key)
    
    @staticmethod
    def invalidate_user_progress_cache(user_id, course_id):
        """Invalidate user progress cache"""
        cache_key = CourseCacheManager.get_course_progress_cache_key(user_id, course_id)
        cache.delete(cache_key)


class UserCacheManager:
    """Cache manager for user-related data"""
    
    @staticmethod
    def get_user_profile_cache_key(user_id):
        return f"user_profile:{user_id}"
    
    @staticmethod
    def get_user_permissions_cache_key(user_id):
        return f"user_permissions:{user_id}"
    
    @staticmethod
    def cache_user_profile(user, timeout=300):
        """Cache user profile data"""
        cache_key = UserCacheManager.get_user_profile_cache_key(user.id)
        profile_data = {
            'id': str(user.id),
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.full_name,
            'role': user.role,
            'avatar': user.avatar.url if user.avatar else None,
            'is_active': user.is_active,
            'tenant_id': str(user.tenant.id) if user.tenant else None,
            'is_tenant_admin': user.is_tenant_admin,
            'is_teacher_or_admin': user.is_teacher_or_admin,
        }
        cache.set(cache_key, profile_data, timeout)
    
    @staticmethod
    def get_cached_user_profile(user_id):
        """Get cached user profile"""
        cache_key = UserCacheManager.get_user_profile_cache_key(user_id)
        return cache.get(cache_key)
    
    @staticmethod
    def invalidate_user_cache(user_id):
        """Invalidate all user-related cache"""
        patterns = [
            f"user_profile:{user_id}",
            f"user_permissions:{user_id}",
            f"user_enrollments:{user_id}",
        ]
        for pattern in patterns:
            cache.delete(pattern)


class AnalyticsCacheManager:
    """Cache manager for analytics data"""
    
    @staticmethod
    def get_analytics_cache_key(tenant_id, metric, date_range):
        return f"analytics:{tenant_id}:{metric}:{date_range}"
    
    @staticmethod
    def cache_analytics_data(tenant_id, metric, date_range, data, timeout=3600):
        """Cache analytics data"""
        cache_key = AnalyticsCacheManager.get_analytics_cache_key(tenant_id, metric, date_range)
        cache.set(cache_key, data, timeout)
    
    @staticmethod
    def get_cached_analytics_data(tenant_id, metric, date_range):
        """Get cached analytics data"""
        cache_key = AnalyticsCacheManager.get_analytics_cache_key(tenant_id, metric, date_range)
        return cache.get(cache_key)
