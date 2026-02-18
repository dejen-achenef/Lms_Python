from celery import Celery
from django.conf import settings
import os

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_platform.config.settings')

app = Celery('lms_platform')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'send-assignment-due-reminders': {
        'task': 'apps.notifications.tasks.send_assignment_due_reminder',
        'schedule': 60.0 * 60.0,  # Run every hour
    },
    'cleanup-expired-sessions': {
        'task': 'apps.users.tasks.cleanup_expired_sessions',
        'schedule': 60.0 * 60.0 * 24.0,  # Run daily
    },
    'generate-daily-reports': {
        'task': 'apps.analytics.tasks.generate_daily_reports',
        'schedule': 60.0 * 60.0 * 24.0,  # Run daily at midnight
    },
}

app.conf.timezone = 'UTC'
