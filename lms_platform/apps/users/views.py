from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth import login, logout
from django.utils import timezone

from .models import User, UserProfile, UserSession
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    UserProfileSerializer, LoginSerializer, PasswordChangeSerializer,
    PasswordResetSerializer
)
from common.permissions import IsTenantAdmin, IsTeacherOrAdmin


class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Create or update session
            session, created = UserSession.objects.get_or_create(
                user=user,
                session_key=request.session.session_key or '',
                defaults={
                    'ip_address': request.META.get('REMOTE_ADDR'),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                }
            )
            
            if not created:
                session.ip_address = request.META.get('REMOTE_ADDR')
                session.user_agent = request.META.get('HTTP_USER_AGENT', '')
                session.last_activity = timezone.now()
                session.save()
            
            # Update user last login
            user.last_login = timezone.now()
            user.last_login_ip = request.META.get('REMOTE_ADDR')
            user.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Deactivate user session
            if request.user.is_authenticated:
                UserSession.objects.filter(
                    user=request.user,
                    session_key=request.session.session_key
                ).update(is_active=False)
            
            return Response({'message': 'Successfully logged out'})
        except Exception as e:
            return Response(
                {'error': 'Invalid token'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def refresh_token(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            return Response({
                'access': str(token.access_token),
            })
        except Exception as e:
            return Response(
                {'error': 'Invalid refresh token'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'is_active', 'tenant']
    search_fields = ['email', 'first_name', 'last_name', 'username']
    ordering_fields = ['email', 'date_joined', 'last_login']
    ordering = ['email']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        elif hasattr(user, 'tenant'):
            return User.objects.filter(tenant=user.tenant)
        return User.objects.filter(id=user.id)

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            permission_classes = [IsAuthenticated, IsTenantAdmin]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({'message': 'Password changed successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            # TODO: Implement password reset email sending
            return Response({'message': 'Password reset email sent'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'patch'])
    def profile(self, request, pk=None):
        user = self.get_object()
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        if request.method == 'GET':
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            serializer = UserProfileSerializer(
                profile, 
                data=request.data, 
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'status': 'activated'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'status': 'deactivated'})
