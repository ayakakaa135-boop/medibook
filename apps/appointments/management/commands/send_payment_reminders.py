# management/commands/send_payment_reminders.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.appointments.models import Appointment



class Command(BaseCommand):
    help = 'Send payment reminders'

    def handle(self, *args, **options):
        now = timezone.now()

        # تذكير قبل أسبوع من الاستحقاق
        upcoming_due = Appointment.objects.filter(
            is_paid=False,
            payment_due_date__lte=now + timedelta(days=7),
            payment_due_date__gt=now
        )

        for appointment in upcoming_due:
            send_email(
                to=appointment.patient.email,
                subject='Payment Reminder',
                template='emails/payment_reminder.html',
                context={'appointment': appointment}
            )