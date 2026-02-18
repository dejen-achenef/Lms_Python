from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from .utils import get_tenant_from_request


class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tenant = get_tenant_from_request(request)
        if tenant:
            request.tenant = tenant
            cache.set(f'tenant_{tenant.id}', tenant, timeout=300)
        else:
            return HttpResponse('Tenant not found', status=404)
