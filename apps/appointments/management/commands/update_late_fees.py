# management/commands/update_late_fees.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.appointments.models import Appointment


class Command(BaseCommand):
    help = 'Update late payment fees for overdue appointments'

    def handle(self, *args, **options):
        now = timezone.now()

        # Get unpaid appointments past due date
        overdue_appointments = Appointment.objects.filter(
            is_paid=False,
            payment_due_date__lt=now,
            status__in=['CONFIRMED', 'COMPLETED']
        )

        updated = 0
        for appointment in overdue_appointments:
            old_fee = appointment.late_payment_fee
            new_fee = appointment.apply_late_payment_fee()

            if new_fee > old_fee:
                appointment.late_payment_fee = new_fee
                appointment.calculate_total_amount()
                appointment.save()
                updated += 1

                # إرسال تذكير بالدفع
                # send_payment_reminder(appointment)

        self.stdout.write(
            self.style.SUCCESS(f'Updated {updated} appointments')
        )