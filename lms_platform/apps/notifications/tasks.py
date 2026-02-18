from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Notification, NotificationTemplate
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_email_notification(notification_id):
    try:
        notification = Notification.objects.get(id=notification_id)
        
        if notification.is_email_sent:
            logger.info(f"Email already sent for notification {notification_id}")
            return
        
        # Get email template
        template = NotificationTemplate.objects.filter(
            tenant=notification.user.tenant,
            notification_type=notification.notification_type,
            send_email=True
        ).first()
        
        if not template:
            logger.warning(f"No email template found for {notification.notification_type}")
            return
        
        # Prepare email context
        context = {
            'user': notification.user,
            'notification': notification,
            'course': notification.course,
            'lesson': notification.lesson,
            'action_url': notification.action_url,
        }
        
        # Send email
        send_mail(
            subject=template.email_subject,
            message=render_to_string('emails/notification.txt', context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.user.email],
            html_message=render_to_string('emails/notification.html', context),
            fail_silently=False,
        )
        
        # Mark as sent
        notification.mark_email_sent()
        logger.info(f"Email sent successfully for notification {notification_id}")
        
    except Exception as e:
        logger.error(f"Failed to send email for notification {notification_id}: {str(e)}")


@shared_task
def send_bulk_notifications(user_ids, title, message, notification_type, metadata=None):
    try:
        notifications = []
        for user_id in user_ids:
            notification = Notification.objects.create(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                metadata=metadata or {}
            )
            notifications.append(notification)
        
        # Send emails asynchronously
        for notification in notifications:
            send_email_notification.delay(str(notification.id))
        
        logger.info(f"Created {len(notifications)} notifications")
        return len(notifications)
        
    except Exception as e:
        logger.error(f"Failed to send bulk notifications: {str(e)}")
        return 0


@shared_task
def send_course_enrollment_notification(enrollment_id):
    try:
        from apps.enrollments.models import Enrollment
        
        enrollment = Enrollment.objects.get(id=enrollment_id)
        
        notification = Notification.objects.create(
            user=enrollment.student,
            title='Course Enrollment Confirmed',
            message=f'You have been successfully enrolled in {enrollment.course.title}',
            notification_type='course_enrollment',
            course=enrollment.course,
            action_url=f'/courses/{enrollment.course.id}'
        )
        
        send_email_notification.delay(str(notification.id))
        logger.info(f"Enrollment notification sent for {enrollment.student.email}")
        
    except Exception as e:
        logger.error(f"Failed to send enrollment notification: {str(e)}")


@shared_task
def send_assignment_due_reminder():
    try:
        from apps.enrollments.models import Assignment
        from django.utils import timezone
        from datetime import timedelta
        
        # Find assignments due in 24 hours
        tomorrow = timezone.now() + timedelta(days=1)
        assignments = Assignment.objects.filter(
            due_date__lte=tomorrow,
            due_date__gt=timezone.now()
        ).select_related('lesson__module__course')
        
        notifications_created = 0
        
        for assignment in assignments:
            # Get all enrolled students
            enrollments = assignment.lesson.module.course.enrollments.filter(is_active=True)
            
            for enrollment in enrollments:
                # Check if student hasn't submitted
                if not assignment.submissions.filter(student=enrollment.student).exists():
                    notification = Notification.objects.create(
                        user=enrollment.student,
                        title='Assignment Due Soon',
                        message=f'Assignment "{assignment.title}" is due on {assignment.due_date.strftime("%B %d, %Y at %I:%M %p")}',
                        notification_type='assignment_due',
                        course=assignment.lesson.module.course,
                        assignment=assignment,
                        action_url=f'/courses/{assignment.lesson.module.course.id}/assignments/{assignment.id}'
                    )
                    
                    send_email_notification.delay(str(notification.id))
                    notifications_created += 1
        
        logger.info(f"Created {notifications_created} assignment due reminders")
        return notifications_created
        
    except Exception as e:
        logger.error(f"Failed to send assignment due reminders: {str(e)}")
        return 0


@shared_task
def generate_progress_report(user_id, course_id=None):
    try:
        from apps.users.models import User
        from apps.courses.models import Course
        
        user = User.objects.get(id=user_id)
        
        if course_id:
            courses = [Course.objects.get(id=course_id)]
        else:
            # Get all enrolled courses
            courses = Course.objects.filter(enrollments__student=user, enrollments__is_active=True)
        
        report_data = {
            'user': user.full_name,
            'email': user.email,
            'generated_at': timezone.now().isoformat(),
            'courses': []
        }
        
        for course in courses:
            enrollment = course.enrollments.get(student=user, is_active=True)
            
            course_data = {
                'title': course.title,
                'completion_percentage': enrollment.completion_percentage,
                'completed_lessons': enrollment.completed_lessons,
                'total_lessons': enrollment.total_lessons,
                'time_spent': enrollment.total_time_spent,
                'enrollment_date': enrollment.enrollment_date.isoformat()
            }
            
            report_data['courses'].append(course_data)
        
        # Here you could generate a PDF or send the report via email
        logger.info(f"Generated progress report for {user.email}")
        return report_data
        
    except Exception as e:
        logger.error(f"Failed to generate progress report: {str(e)}")
        return None
