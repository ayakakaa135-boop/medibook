# tests/test_payments.py
from datetime import timezone, timedelta

from django.test import TestCase
from decimal import Decimal
from apps.appointments.models import Appointment


class PaymentTests(TestCase):
    def test_cancellation_fee_calculation(self):
        """Test cancellation fee for appointments < 24 hours"""
        appointment = Appointment.objects.create(
            # ... بيانات الموعد
            base_price=Decimal('200.00')
        )

        # إلغاء قبل أقل من 24 ساعة
        fee = appointment.calculate_cancellation_fee()
        self.assertEqual(fee, Decimal('100.00'))  # 50%

    def test_late_payment_fee(self):
        """Test late payment fee calculation"""
        appointment = Appointment.objects.create(
            base_price=Decimal('200.00'),
            payment_due_date=timezone.now() - timedelta(days=14)  # أسبوعين تأخير
        )

        fee = appointment.apply_late_payment_fee()
        self.assertEqual(fee, Decimal('20.00'))  # 5% * 2 weeks = 10%