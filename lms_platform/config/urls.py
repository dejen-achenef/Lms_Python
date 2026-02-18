from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('lms_platform.apps.users.urls')),
    path('api/v1/tenants/', include('lms_platform.apps.tenants.urls')),
    path('api/v1/courses/', include('lms_platform.apps.courses.urls')),
    path('api/v1/enrollments/', include('lms_platform.apps.enrollments.urls')),
    path('api/v1/payments/', include('lms_platform.apps.payments.urls')),
    path('api/v1/notifications/', include('lms_platform.apps.notifications.urls')),
    path('api/v1/analytics/', include('lms_platform.apps.analytics.urls')),
    path('api/v1/quizzes/', include('lms_platform.apps.quizzes.urls')),
    path('api/v1/chat/', include('lms_platform.apps.chat.urls')),
    path('api/v1/gamification/', include('lms_platform.apps.gamification.urls')),
    path('api/v1/ai/', include('lms_platform.apps.ai.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
