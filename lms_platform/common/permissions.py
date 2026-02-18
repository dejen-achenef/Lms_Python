from rest_framework.permissions import BasePermission


class IsTenantAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or 
            request.user.role == 'admin'
        )


class IsTeacherOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or 
            request.user.role in ['admin', 'teacher']
        )


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return obj.user == request.user or request.user.is_superuser


class IsEnrolledOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Check if user is enrolled in the course
        if hasattr(obj, 'course'):
            course = obj.course
        else:
            course = obj
            
        return (
            request.user.is_superuser or
            request.user.role in ['admin', 'teacher'] or
            course.enrollments.filter(student=request.user, is_active=True).exists()
        )
