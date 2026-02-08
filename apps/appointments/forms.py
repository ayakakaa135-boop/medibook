from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import datetime, timedelta, date
import re

from .models import Appointment, Payment, PaymentCard
from apps.doctors.models import Doctor, WorkingHour, DayOff


class AppointmentCreateForm(forms.ModelForm):
    """Appointment creation form with payment option"""

    pay_now = forms.BooleanField(
        required=False,
        initial=False,
        label=_('Pay now'),
        help_text=_('Check to pay immediately, or pay within 25 days')
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'service', 'date', 'start_time', 'symptoms', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500'
            }),
            'start_time': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500'
            }),
            'symptoms': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': _('Describe your symptoms...'),
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': _('Any special requests...'),
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)

        self.fields['doctor'].widget.attrs.update({
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500'
        })

        self.fields['service'].widget.attrs.update({
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500'
        })

        self.fields['date'].widget.attrs['min'] = timezone.now().date().isoformat()

        if self.doctor:
            self.fields['service'].queryset = self.doctor.clinic.services.filter(is_active=True)

        self.fields['symptoms'].required = False
        self.fields['notes'].required = False

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date < timezone.now().date():
            raise ValidationError(_('Cannot book appointments in the past'))

        max_date = timezone.now().date() + timedelta(days=90)
        if date and date > max_date:
            raise ValidationError(_('Cannot book appointments more than 3 months in advance'))

        return date

    def clean_start_time(self):
        start_time = self.cleaned_data.get('start_time')
        if not start_time:
            raise ValidationError(_('Please select a time'))
        return start_time

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')

        if not all([doctor, date, start_time]):
            return cleaned_data

        day_of_week = date.weekday()
        working_hours = WorkingHour.objects.filter(
            doctor=doctor,
            day_of_week=day_of_week,
            is_active=True
        )

        if not working_hours.exists():
            raise ValidationError({
                'date': _('Doctor is not available on this day')
            })

        is_valid_time = False
        for wh in working_hours:
            if wh.start_time <= start_time < wh.end_time:
                is_valid_time = True
                break

        if not is_valid_time:
            raise ValidationError({
                'start_time': _('Selected time is outside doctor\'s working hours')
            })

        if DayOff.objects.filter(doctor=doctor, date=date).exists():
            raise ValidationError({
                'date': _('Doctor is not available on this date')
            })

        conflicts = Appointment.objects.filter(
            doctor=doctor,
            date=date,
            start_time=start_time,
            status__in=['PENDING', 'CONFIRMED']
        )

        if self.instance.pk:
            conflicts = conflicts.exclude(pk=self.instance.pk)

        if conflicts.exists():
            raise ValidationError({
                'start_time': _('This time slot is already booked')
            })

        return cleaned_data


class AppointmentCancelForm(forms.Form):
    """Appointment cancellation form with fee warning"""

    reason = forms.CharField(
        required=False,
        label=_('Reason'),
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': _('Reason for cancellation (optional)'),
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500'
        })
    )

    acknowledge_fee = forms.BooleanField(
        required=False,
        label=_('I understand that I may be charged a cancellation fee'),
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-purple-600 bg-gray-100 border-gray-300 rounded focus:ring-purple-500'
        })
    )

    def __init__(self, *args, **kwargs):
        self.appointment = kwargs.pop('appointment', None)
        super().__init__(*args, **kwargs)

        # Make fee acknowledgment required if cancellation fee applies
        if self.appointment and not self.appointment.can_cancel_free:
            self.fields['acknowledge_fee'].required = True


class PaymentForm(forms.ModelForm):
    """Payment form for Visa/Mastercard - WITHOUT payment_method field"""

    card_number = forms.CharField(
        label=_('Card Number'),
        max_length=19,
        widget=forms.TextInput(attrs={
            'placeholder': '1234 5678 9012 3456',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500',
            'maxlength': '19'
        })
    )

    cardholder_name = forms.CharField(
        label=_('Cardholder Name'),
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'John Doe',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500'
        })
    )

    expiry_month = forms.CharField(
        label=_('Expiry Month'),
        max_length=2,
        widget=forms.TextInput(attrs={
            'placeholder': 'MM',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500',
            'maxlength': '2'
        })
    )

    expiry_year = forms.CharField(
        label=_('Expiry Year'),
        max_length=4,
        widget=forms.TextInput(attrs={
            'placeholder': 'YYYY',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500',
            'maxlength': '4'
        })
    )

    cvv = forms.CharField(
        label=_('CVV'),
        max_length=4,
        widget=forms.PasswordInput(attrs={
            'placeholder': '123',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500',
            'maxlength': '4'
        })
    )

    save_card = forms.BooleanField(
        required=False,
        label=_('Save card for future payments'),
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-purple-600 bg-gray-100 border-gray-300 rounded focus:ring-purple-500'
        })
    )

    class Meta:
        model = Payment
        fields = []  # No model fields needed, all are custom

    def clean_card_number(self):
        """Validate card number"""
        card_number = self.cleaned_data.get('card_number', '').replace(' ', '')

        # Remove spaces and dashes
        card_number = re.sub(r'[\s-]', '', card_number)

        # Check if only digits
        if not card_number.isdigit():
            raise ValidationError(_('Card number must contain only digits'))

        # Check length (13-19 digits)
        if not (13 <= len(card_number) <= 19):
            raise ValidationError(_('Invalid card number length'))

        # Luhn algorithm validation
        if not self._luhn_check(card_number):
            raise ValidationError(_('Invalid card number'))

        return card_number

    def clean_expiry_month(self):
        """Validate expiry month"""
        month = self.cleaned_data.get('expiry_month', '')

        if not month.isdigit():
            raise ValidationError(_('Month must be numeric'))

        month_int = int(month)
        if not (1 <= month_int <= 12):
            raise ValidationError(_('Month must be between 01 and 12'))

        return month.zfill(2)  # Pad with zero

    def clean_expiry_year(self):
        """Validate expiry year"""
        year = self.cleaned_data.get('expiry_year', '')

        if not year.isdigit():
            raise ValidationError(_('Year must be numeric'))

        if len(year) != 4:
            raise ValidationError(_('Year must be 4 digits'))

        year_int = int(year)
        current_year = timezone.now().year

        if year_int < current_year:
            raise ValidationError(_('Card has expired'))

        if year_int > current_year + 20:
            raise ValidationError(_('Invalid expiry year'))

        return year

    def clean_cvv(self):
        """Validate CVV"""
        cvv = self.cleaned_data.get('cvv', '')

        if not cvv.isdigit():
            raise ValidationError(_('CVV must contain only digits'))

        if not (3 <= len(cvv) <= 4):
            raise ValidationError(_('CVV must be 3 or 4 digits'))

        return cvv

    def clean(self):
        """Validate card expiry date"""
        cleaned_data = super().clean()
        month = cleaned_data.get('expiry_month')
        year = cleaned_data.get('expiry_year')

        if month and year:
            try:
                # التحقق من تاريخ اليوم
                today = date.today()

                # تحويل المدخلات إلى أرقام
                expiry_year = int(year)
                expiry_month = int(month)

                # منطق التحقق الصحيح:
                # البطاقة منتهية فقط إذا كانت السنة أقل من الحالية
                # أو إذا كانت نفس السنة ولكن الشهر أقل من الشهر الحالي
                if expiry_year < today.year or (expiry_year == today.year and expiry_month < today.month):
                    raise ValidationError(_('Card has expired'))

            except ValueError:
                raise ValidationError(_('Invalid expiry date'))

        return cleaned_data

    def _luhn_check(self, card_number):
        """Luhn algorithm for card validation"""

        def digits_of(n):
            return [int(d) for d in str(n)]

        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)

        for d in even_digits:
            checksum += sum(digits_of(d * 2))

        return checksum % 10 == 0


class SavedCardPaymentForm(forms.Form):
    """Form for paying with saved card"""

    saved_card = forms.ModelChoiceField(
        queryset=PaymentCard.objects.none(),
        label=_('Select Card'),
        widget=forms.RadioSelect(attrs={
            'class': 'w-4 h-4 text-purple-600 bg-gray-100 border-gray-300 focus:ring-purple-500'
        })
    )

    cvv = forms.CharField(
        label=_('CVV'),
        max_length=4,
        widget=forms.PasswordInput(attrs={
            'placeholder': '123',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500',
            'maxlength': '4'
        })
    )

    def __init__(self, *args, **kwargs):
        patient = kwargs.pop('patient', None)
        super().__init__(*args, **kwargs)

        if patient:
            self.fields['saved_card'].queryset = PaymentCard.objects.filter(
                patient=patient,
                is_active=True
            )

    def clean_cvv(self):
        cvv = self.cleaned_data.get('cvv', '')

        if not cvv.isdigit():
            raise ValidationError(_('CVV must contain only digits'))

        if not (3 <= len(cvv) <= 4):
            raise ValidationError(_('CVV must be 3 or 4 digits'))

        return cvv


class AppointmentFilterForm(forms.Form):
    """Appointment filtering form"""

    STATUS_CHOICES = [('', _('All Statuses'))] + list(Appointment.Status.choices)
    PAYMENT_CHOICES = [
        ('', _('All')),
        ('paid', _('Paid')),
        ('unpaid', _('Unpaid')),
        ('overdue', _('Overdue')),
    ]

    status = forms.ChoiceField(
        required=False,
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500'
        })
    )

    payment_status = forms.ChoiceField(
        required=False,
        choices=PAYMENT_CHOICES,
        label=_('Payment Status'),
        widget=forms.Select(attrs={
            'class': 'px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500'
        })
    )

    date_from = forms.DateField(
        required=False,
        label=_('From Date'),
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500'
        })
    )

    date_to = forms.DateField(
        required=False,
        label=_('To Date'),
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500'
        })
    )