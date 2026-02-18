from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Avg, Count
from django.utils import timezone

from .models import Category, Course, Module, Lesson, LessonProgress, CourseReview, CourseBookmark
from .serializers import (
    CategorySerializer, CourseSerializer, CourseCreateSerializer,
    ModuleSerializer, LessonSerializer, LessonDetailSerializer,
    LessonProgressSerializer, LessonProgressUpdateSerializer,
    CourseReviewSerializer, CourseBookmarkSerializer
)
from common.permissions import IsTenantAdmin, IsTeacherOrAdmin, IsEnrolledOrReadOnly


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'tenant'):
            return Category.objects.filter(tenant=user.tenant)
        return Category.objects.none()

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsEnrolledOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'difficulty', 'is_free', 'category', 'instructor']
    search_fields = ['title', 'description', 'short_description']
    ordering_fields = ['title', 'created_at', 'published_at', 'price']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return CourseCreateSerializer
        return CourseSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Course.objects.all()
        elif hasattr(user, 'tenant'):
            queryset = Course.objects.filter(tenant=user.tenant)
            
            # Filter by published status for non-teachers
            if user.role not in ['admin', 'teacher']:
                queryset = queryset.filter(status='published')
            
            return queryset
        return Course.objects.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
        else:
            permission_classes = [IsAuthenticated, IsEnrolledOrReadOnly]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(
            instructor=self.request.user,
            tenant=self.request.user.tenant
        )

    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):
        course = self.get_object()
        
        # Check if course is full
        if course.is_full:
            return Response(
                {'error': 'Course is full'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already enrolled
        if course.enrollments.filter(student=request.user, is_active=True).exists():
            return Response(
                {'error': 'Already enrolled in this course'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create enrollment
        from apps.enrollments.models import Enrollment
        enrollment = Enrollment.objects.create(
            student=request.user,
            course=course,
            is_paid=course.is_free
        )
        
        return Response({
            'message': 'Successfully enrolled in course',
            'enrollment_id': enrollment.id
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        course = self.get_object()
        if course.status != 'published':
            course.status = 'published'
            course.published_at = timezone.now()
            course.save()
        return Response({'status': 'published'})

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        course = self.get_object()
        course.status = 'archived'
        course.save()
        return Response({'status': 'archived'})

    @action(detail=True, methods=['get'])
    def modules(self, request, pk=None):
        course = self.get_object()
        modules = course.modules.all()
        serializer = ModuleSerializer(modules, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        course = self.get_object()
        
        # Check if user is enrolled
        if not course.enrollments.filter(student=request.user, is_active=True).exists():
            return Response(
                {'error': 'Not enrolled in this course'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get overall progress
        enrollment = course.enrollments.get(student=request.user, is_active=True)
        
        # Get lesson progress details
        lesson_progress = LessonProgress.objects.filter(
            user=request.user,
            lesson__module__course=course
        ).select_related('lesson')
        
        progress_data = []
        for progress in lesson_progress:
            progress_data.append({
                'lesson_id': progress.lesson.id,
                'lesson_title': progress.lesson.title,
                'module_id': progress.lesson.module.id,
                'module_title': progress.lesson.module.title,
                'is_completed': progress.is_completed,
                'completion_percentage': progress.completion_percentage,
                'watch_time': progress.watch_time,
                'last_position': progress.last_position
            })
        
        return Response({
            'enrollment_id': enrollment.id,
            'completion_percentage': enrollment.completion_percentage,
            'completed_lessons': enrollment.completed_lessons,
            'total_lessons': enrollment.total_lessons,
            'lesson_progress': progress_data
        })

    @action(detail=True, methods=['get', 'post'])
    def reviews(self, request, pk=None):
        course = self.get_object()
        
        if request.method == 'GET':
            reviews = course.reviews.filter(is_public=True)
            serializer = CourseReviewSerializer(reviews, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            # Check if user is enrolled
            if not course.enrollments.filter(student=request.user, is_active=True).exists():
                return Response(
                    {'error': 'Must be enrolled to review'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = CourseReviewSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, course=course)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ModuleViewSet(viewsets.ModelViewSet):
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    filter_backends = [OrderingFilter]
    ordering_fields = ['order', 'created_at']
    ordering = ['order']

    def get_queryset(self):
        course_id = self.request.query_params.get('course_id')
        if course_id:
            return Module.objects.filter(course_id=course_id)
        return Module.objects.none()

    def perform_create(self, serializer):
        # Set the order if not provided
        if not serializer.validated_data.get('order'):
            last_order = Module.objects.filter(
                course=serializer.validated_data['course']
            ).order_by('-order').first()
            serializer.validated_data['order'] = (last_order.order + 1) if last_order else 1
        serializer.save()


class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsEnrolledOrReadOnly]
    filter_backends = [OrderingFilter]
    ordering_fields = ['order', 'created_at']
    ordering = ['order']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LessonDetailSerializer
        return LessonSerializer

    def get_queryset(self):
        module_id = self.request.query_params.get('module_id')
        if module_id:
            return Lesson.objects.filter(module_id=module_id)
        return Lesson.objects.none()

    def perform_create(self, serializer):
        # Set the order if not provided
        if not serializer.validated_data.get('order'):
            last_order = Lesson.objects.filter(
                module=serializer.validated_data['module']
            ).order_by('-order').first()
            serializer.validated_data['order'] = (last_order.order + 1) if last_order else 1
        serializer.save()

    @action(detail=True, methods=['get', 'post', 'patch'])
    def progress(self, request, pk=None):
        lesson = self.get_object()
        
        # Check if user is enrolled in the course
        course = lesson.module.course
        if not course.enrollments.filter(student=request.user, is_active=True).exists():
            return Response(
                {'error': 'Not enrolled in this course'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if request.method == 'GET':
            try:
                progress = lesson.progress.get(user=request.user)
                serializer = LessonProgressSerializer(progress)
                return Response(serializer.data)
            except LessonProgress.DoesNotExist:
                return Response({
                    'is_completed': False,
                    'completion_percentage': 0,
                    'watch_time': 0,
                    'last_position': 0
                })
        
        elif request.method in ['POST', 'PATCH']:
            progress, created = LessonProgress.objects.get_or_create(
                user=request.user,
                lesson=lesson,
                defaults={
                    'completion_percentage': 0,
                    'watch_time': 0,
                    'last_position': 0
                }
            )
            
            serializer = LessonProgressUpdateSerializer(
                progress, 
                data=request.data, 
                partial=True
            )
            if serializer.is_valid():
                updated_progress = serializer.save()
                
                # Check if lesson is completed
                if updated_progress.completion_percentage >= 100:
                    updated_progress.mark_completed()
                    
                    # Update course enrollment progress
                    enrollment = course.enrollments.get(student=request.user, is_active=True)
                    enrollment.update_progress()
                
                return Response(LessonProgressSerializer(updated_progress).data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        lesson = self.get_object()
        
        # Check if user is enrolled in the course
        course = lesson.module.course
        if not course.enrollments.filter(student=request.user, is_active=True).exists():
            return Response(
                {'error': 'Not enrolled in this course'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        progress, created = LessonProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson
        )
        
        progress.mark_completed()
        
        # Update course enrollment progress
        enrollment = course.enrollments.get(student=request.user, is_active=True)
        enrollment.update_progress()
        
        return Response({'message': 'Lesson marked as completed'})

    @action(detail=True, methods=['get', 'post'])
    def bookmarks(self, request, pk=None):
        lesson = self.get_object()
        
        if request.method == 'GET':
            bookmarks = lesson.bookmarks.filter(user=request.user)
            serializer = CourseBookmarkSerializer(bookmarks, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            bookmark, created = CourseBookmark.objects.get_or_create(
                user=request.user,
                lesson=lesson,
                defaults={
                    'position': request.data.get('position', 0),
                    'note': request.data.get('note', '')
                }
            )
            
            if not created:
                bookmark.position = request.data.get('position', bookmark.position)
                bookmark.note = request.data.get('note', bookmark.note)
                bookmark.save()
            
            serializer = CourseBookmarkSerializer(bookmark)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class CourseBookmarkViewSet(viewsets.ModelViewSet):
    serializer_class = CourseBookmarkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CourseBookmark.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
