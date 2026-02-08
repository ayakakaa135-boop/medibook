# apps/notifications/email_service.py
"""
Email Notification Service
Handles all email notifications for appointments, login, logout, etc.
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from datetime import datetime
# في أول الملف، أضف:
from django.utils.translation import gettext as _

class EmailService:
    """Service for sending email notifications"""

    @staticmethod
    def send_email(subject, to_email, template_name, context, from_email=None):
        """
        Send HTML email using template

        Args:
            subject: Email subject
            to_email: Recipient email
            template_name: Template path (e.g., 'emails/appointment_confirmation.html')
            context: Dictionary with template variables
            from_email: Sender email (optional)
        """
        if from_email is None:
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@clinic.com')

        # Render HTML content
        html_content = render_to_string(template_name, context)

        # Create plain text version
        text_content = strip_tags(html_content)

        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[to_email]
        )

        # Attach HTML version
        email.attach_alternative(html_content, "text/html")

        # Send
        try:
            email.send(fail_silently=False)
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    @classmethod
    def send_appointment_confirmation(cls, appointment):
        """Send appointment confirmation email"""
        subject = 'تأكيد حجز موعد - Appointment Confirmation'

        context = {
            'appointment': appointment,
            'patient_name': appointment.patient.get_full_name(),
            'doctor_name': appointment.doctor.user.get_full_name(),
            'clinic_name': appointment.clinic.name,
            'date': appointment.date,
            'time': appointment.start_time,
            'service': appointment.service.name if appointment.service else 'استشارة عامة',
            'price': appointment.base_price,
            'site_name': getattr(settings, 'SITE_NAME', 'عيادتنا'),
        }

        return cls.send_email(
            subject=subject,
            to_email=appointment.patient.email,
            template_name='emails/appointment_confirmation.html',
            context=context
        )

    @classmethod
    def send_appointment_reminder(cls, appointment):
        """Send appointment reminder (24 hours before)"""
        subject = 'تذكير بموعدك القادم - Appointment Reminder'

        context = {
            'appointment': appointment,
            'patient_name': appointment.patient.get_full_name(),
            'doctor_name': appointment.doctor.user.get_full_name(),
            'clinic_name': appointment.clinic.name,
            'date': appointment.date,
            'time': appointment.start_time,
        }

        return cls.send_email(
            subject=subject,
            to_email=appointment.patient.email,
            template_name='emails/appointment_reminder.html',
            context=context
        )

    @classmethod
    def send_appointment_cancellation(cls, appointment):
        """Send appointment cancellation email"""
        subject = 'إلغاء الموعد - Appointment Cancelled'

        context = {
            'appointment': appointment,
            'patient_name': appointment.patient.get_full_name(),
            'doctor_name': appointment.doctor.user.get_full_name(),
            'date': appointment.date,
            'time': appointment.start_time,
            'cancellation_fee': appointment.cancellation_fee,
        }

        return cls.send_email(
            subject=subject,
            to_email=appointment.patient.email,
            template_name='emails/appointment_cancelled.html',
            context=context
        )

    @classmethod
    def send_payment_confirmation(cls, payment):
        """Send payment confirmation email"""
        subject = 'تأكيد الدفع - Payment Confirmation'

        context = {
            'payment': payment,
            'patient_name': payment.patient.get_full_name(),
            'amount': payment.amount,
            'transaction_id': payment.transaction_id,
            'appointment': payment.appointment,
        }

        return cls.send_email(
            subject=subject,
            to_email=payment.patient.email,
            template_name='emails/payment_confirmation.html',
            context=context
        )

    @classmethod
    def send_payment_reminder(cls, appointment):
        """Send payment reminder email"""
        subject = 'تذكير بالدفع - Payment Reminder'

        context = {
            'appointment': appointment,
            'patient_name': appointment.patient.get_full_name(),
            'amount': appointment.total_amount,
            'days_remaining': appointment.days_until_payment_due,
        }

        return cls.send_email(
            subject=subject,
            to_email=appointment.patient.email,
            template_name='emails/payment_reminder.html',
            context=context
        )

    @classmethod
    def send_login_notification(cls, user, request):
        """Send login notification email"""
        subject = 'تسجيل دخول جديد - New Login Detected'

        # Get IP and user agent
        ip_address = cls._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')

        context = {
            'user': user,
            'user_name': user.get_full_name(),
            'login_time': datetime.now(),
            'ip_address': ip_address,
            'user_agent': user_agent,
        }

        return cls.send_email(
            subject=subject,
            to_email=user.email,
            template_name='emails/login_notification.html',
            context=context
        )

    @classmethod
    def send_logout_notification(cls, user, request):
        """Send logout notification email"""
        subject = 'تسجيل خروج - Logout Notification'

        ip_address = cls._get_client_ip(request)

        context = {
            'user': user,
            'user_name': user.get_full_name(),
            'logout_time': datetime.now(),
            'ip_address': ip_address,
        }

        return cls.send_email(
            subject=subject,
            to_email=user.email,
            template_name='emails/logout_notification.html',
            context=context
        )

    @classmethod
    def send_welcome_email(cls, user):
        """Send welcome email to new user"""
        subject = 'مرحباً بك - Welcome!'

        context = {
            'user': user,
            'user_name': user.get_full_name(),
            'site_name': getattr(settings, 'SITE_NAME', 'عيادتنا'),
        }

        return cls.send_email(
            subject=subject,
            to_email=user.email,
            template_name='emails/welcome.html',
            context=context
        )

    @staticmethod
    def _get_client_ip(request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip