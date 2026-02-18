from django.http import Http404
from django.core.cache import cache
from apps.tenants.models import Tenant


def get_tenant_from_request(request):
    tenant_id = request.META.get('HTTP_X_TENANT_ID')
    subdomain = request.META.get('HTTP_X_SUBDOMAIN')
    
    if tenant_id:
        cache_key = f'tenant_{tenant_id}'
        tenant = cache.get(cache_key)
        if not tenant:
            try:
                tenant = Tenant.objects.get(id=tenant_id, is_active=True)
                cache.set(cache_key, tenant, timeout=300)
            except Tenant.DoesNotExist:
                return None
        return tenant
    
    elif subdomain:
        cache_key = f'tenant_subdomain_{subdomain}'
        tenant = cache.get(cache_key)
        if not tenant:
            try:
                tenant = Tenant.objects.get(subdomain=subdomain, is_active=True)
                cache.set(cache_key, tenant, timeout=300)
            except Tenant.DoesNotExist:
                return None
        return tenant
    
    return None


def get_current_tenant():
    from threading import local
    _thread_locals = local()
    return getattr(_thread_locals, 'tenant', None)


def set_current_tenant(tenant):
    from threading import local
    _thread_locals = local()
    _thread_locals.tenant = tenant
