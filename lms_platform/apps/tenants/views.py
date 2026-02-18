from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q

from .models import Tenant, TenantSettings
from .serializers import TenantSerializer, TenantCreateSerializer, TenantSettingsSerializer
from common.permissions import IsTenantAdmin


class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'plan_type']
    search_fields = ['name', 'subdomain', 'domain']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'create':
            return TenantCreateSerializer
        return TenantSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Tenant.objects.all()
        elif hasattr(user, 'tenant'):
            return Tenant.objects.filter(id=user.tenant.id)
        return Tenant.objects.none()

    @action(detail=True, methods=['get', 'patch', 'put'])
    def settings(self, request, pk=None):
        tenant = self.get_object()
        
        if request.method == 'GET':
            settings, created = TenantSettings.objects.get_or_create(tenant=tenant)
            serializer = TenantSettingsSerializer(settings)
            return Response(serializer.data)
        
        elif request.method in ['PATCH', 'PUT']:
            settings, created = TenantSettings.objects.get_or_create(tenant=tenant)
            serializer = TenantSettingsSerializer(settings, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        tenant = self.get_object()
        tenant.is_active = True
        tenant.save()
        return Response({'status': 'activated'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        tenant = self.get_object()
        tenant.is_active = False
        tenant.save()
        return Response({'status': 'deactivated'})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=403)
        
        stats = {
            'total_tenants': Tenant.objects.count(),
            'active_tenants': Tenant.objects.filter(is_active=True).count(),
            'basic_plan': Tenant.objects.filter(plan_type='basic').count(),
            'pro_plan': Tenant.objects.filter(plan_type='pro').count(),
            'enterprise_plan': Tenant.objects.filter(plan_type='enterprise').count(),
        }
        return Response(stats)
