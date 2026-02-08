from datetime import datetime, timedelta
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Appointment(models.Model):
    """Patient Appointment Model with Payment System - SIMPLIFIED TIMEZONE"""

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        CONFIRMED = 'CONFIRMED', _('Confirmed')
        CANCELED = 'CANCELED', _('Canceled')
        COMPLETED = 'COMPLETED', _('Completed')
        NO_SHOW = 'NO_SHOW', _('No Show')

    # Relations
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name=_('patient')
    )
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name=_('doctor')
    )
    clinic = models.ForeignKey(
        'clinics.Clinic',
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name=_('clinic')
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments',
        verbose_name=_('service')
    )

    # Scheduling
    date = models.DateField(_('date'))
    start_time = models.TimeField(_('start time'))
    end_time = models.TimeField(_('end time'), blank=True, null=True)

    # Details
    symptoms = models.TextField(_('symptoms'), blank=True)
    notes = models.TextField(_('notes'), blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    # Payment Fields
    base_price = models.DecimalField(
        _('base price'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    cancellation_fee = models.DecimalField(
        _('cancellation fee'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    late_payment_fee = models.DecimalField(
        _('late payment fee'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    total_amount = models.DecimalField(
        _('total amount'),
        max_digits=10,
        decimal_places=2,
        default=0
    )

    # Payment Status
    is_paid = models.BooleanField(_('is paid'), default=False)
    paid_at = models.DateTimeField(_('paid at'), null=True, blank=True)
    payment_due_date = models.DateTimeField(_('payment due date'), null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    confirmed_at = models.DateTimeField(_('confirmed at'), null=True, blank=True)
    canceled_at = models.DateTimeField(_('canceled at'), null=True, blank=True)
    cancellation_reason = models.TextField(_('cancellation reason'), blank=True)

    class Meta:
        verbose_name = _('appointment')
        verbose_name_plural = _('appointments')
        ordering = ['-date', '-start_time']
        indexes = [
            models.Index(fields=['patient', 'date']),
            models.Index(fields=['doctor', 'date']),
            models.Index(fields=['status']),
            models.Index(fields=['is_paid']),
        ]

    def __str__(self):
        return f"{self.patient.get_full_name()} - Dr. {self.doctor.user.get_full_name()} on {self.date}"

    def save(self, *args, **kwargs):
        """Auto-calculate end_time, prices, and payment due date"""
        # Calculate end_time
        if not self.end_time:
            duration = 30
            if self.service and hasattr(self.service, 'duration_minutes'):
                duration = self.service.duration_minutes or 30

            start_dt = datetime.combine(self.date, self.start_time)
            end_dt = start_dt + timedelta(minutes=duration)
            self.end_time = end_dt.time()

        # Set base price
        if not self.base_price and self.service:
            self.base_price = getattr(self.service, 'price', Decimal('0'))

        # Set payment due date - ALWAYS TIMEZONE AWARE
        if not self.payment_due_date:
            # Combine date and time
            dt = datetime.combine(self.date, self.start_time)
            # Make timezone aware
            dt = timezone.make_aware(dt) if timezone.is_naive(dt) else dt
            # Add 25 days
            self.payment_due_date = dt + timedelta(days=25)

        # Calculate total
        self.total_amount = self.base_price + self.cancellation_fee + self.late_payment_fee

        super().save(*args, **kwargs)

    def get_appointment_datetime(self):
        """Get appointment datetime as timezone-aware"""
        dt = datetime.combine(self.date, self.start_time)
        return timezone.make_aware(dt) if timezone.is_naive(dt) else dt

    def get_hours_until_appointment(self):
        """Calculate hours until appointment"""
        try:
            now = timezone.now()
            appointment_dt = self.get_appointment_datetime()
            delta = appointment_dt - now
            return delta.total_seconds() / 3600
        except:
            return None

    def calculate_cancellation_fee(self):
        """Calculate cancellation fee (50% if < 24 hours)"""

        # 1. التحقق من أن السعر الأساسي ليس فارغاً
        if self.base_price is None:
            return Decimal('0.00')

        hours_until = self.get_hours_until_appointment()

        if hours_until is not None and hours_until < 24:
            # 2. التحقق من القيمة القادمة من الإعدادات بشكل آمن
            raw_percentage = getattr(settings, 'CANCELLATION_FEE_PERCENTAGE', 50)

            # التأكد من أن النسبة ليست None وليست نصاً فارغاً
            if raw_percentage is None:
                percentage = Decimal('50')
            else:
                percentage = Decimal(str(raw_percentage))

            # 3. إجراء العملية الحسابية
            return (self.base_price * percentage) / Decimal('100')

        return Decimal('0.00')
    def calculate_late_payment_fee(self):
        """Calculate late payment fee"""

        # ✅ التحقق من وجود base_price أولاً
        if not self.base_price:
            return Decimal('0.00')

        if self.is_paid or not self.payment_due_date:
            return Decimal('0.00')

        now = timezone.now()

        # Ensure payment_due_date is timezone-aware
        due_date = self.payment_due_date
        if timezone.is_naive(due_date):
            due_date = timezone.make_aware(due_date)

        if now <= due_date:
            return Decimal('0.00')

        # Calculate overdue days
        days_overdue = (now - due_date).days
        weeks_overdue = max(1, (days_overdue // 7) + 1)

        # 5% per week, max 50%
        percentage = min(
            getattr(settings, 'LATE_PAYMENT_FEE_PERCENTAGE', 5) * weeks_overdue,
            getattr(settings, 'MAX_LATE_FEE_PERCENTAGE', 50)
        )

        return (self.base_price * Decimal(percentage)) / Decimal('100')

    def get_absolute_url(self):
        return reverse('appointments:detail', kwargs={'pk': self.pk})

    # Properties
    @property
    def is_past(self):
        """Check if appointment is in the past"""
        try:
            return self.get_appointment_datetime() < timezone.now()
        except:
            return self.date < timezone.now().date()

    @property
    def is_upcoming(self):
        return not self.is_past and self.status in ['PENDING', 'CONFIRMED']

    @property
    def can_cancel(self):
        return self.status in ['PENDING', 'CONFIRMED'] and not self.is_past

    @property
    def can_cancel_free(self):
        hours = self.get_hours_until_appointment()
        return hours is not None and hours >= 24

    @property
    def is_payment_overdue(self):
        """Check if payment is overdue"""
        if self.is_paid or not self.payment_due_date:
            return False

        try:
            due_date = self.payment_due_date
            if timezone.is_naive(due_date):
                due_date = timezone.make_aware(due_date)
            return timezone.now() > due_date
        except:
            return False

    @property
    def days_until_payment_due(self):
        """Days until payment due"""
        if self.is_paid or not self.payment_due_date:
            return 0

        try:
            due_date = self.payment_due_date
            if timezone.is_naive(due_date):
                due_date = timezone.make_aware(due_date)

            delta = due_date - timezone.now()
            return max(0, delta.days)
        except:
            return 0

    @property
    def hours_until_appointment(self):
        """Helper property"""
        return self.get_hours_until_appointment()

    @property
    def duration_minutes(self):
        if self.end_time and self.start_time:
            start = datetime.combine(self.date, self.start_time)
            end = datetime.combine(self.date, self.end_time)
            return int((end - start).total_seconds() / 60)
        return 30


class Payment(models.Model):
    """Payment Model - SIMPLIFIED"""

    class PaymentMethod(models.TextChoices):
        VISA = 'VISA', _('Visa')
        MASTERCARD = 'MASTERCARD', _('Mastercard')
        CASH = 'CASH', _('Cash')

    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        PROCESSING = 'PROCESSING', _('Processing')
        COMPLETED = 'COMPLETED', _('Completed')
        FAILED = 'FAILED', _('Failed')
        REFUNDED = 'REFUNDED', _('Refunded')

    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='payments')
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.VISA)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)

    card_last_four = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=20, blank=True)
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    gateway_response = models.JSONField(null=True, blank=True)

    base_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cancellation_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    late_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    is_refunded = models.BooleanField(default=False)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refunded_at = models.DateTimeField(null=True, blank=True)
    refund_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.transaction_id or self.id} - {self.amount} SAR"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            import uuid
            self.transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

    def mark_as_completed(self):
        self.status = self.PaymentStatus.COMPLETED
        self.completed_at = timezone.now()
        self.appointment.is_paid = True
        self.appointment.paid_at = timezone.now()
        self.appointment.save()
        self.save()

    def mark_as_failed(self, reason=''):
        self.status = self.PaymentStatus.FAILED
        if reason:
            self.gateway_response = {'error': reason}
        self.save()


class PaymentCard(models.Model):
    """Saved Payment Cards"""

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_cards')

    card_token = models.CharField(max_length=255)
    card_last_four = models.CharField(max_length=4)
    card_brand = models.CharField(max_length=20)
    expiry_month = models.CharField(max_length=2)
    expiry_year = models.CharField(max_length=4)
    cardholder_name = models.CharField(max_length=255)

    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.card_brand.upper()} **** {self.card_last_four}"

    def save(self, *args, **kwargs):
        if self.is_default:
            PaymentCard.objects.filter(patient=self.patient, is_default=True).exclude(pk=self.pk).update(
                is_default=False)
        super().save(*args, **kwargs)