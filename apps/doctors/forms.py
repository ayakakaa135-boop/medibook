from django import forms
from django.core.exceptions import ValidationError
from .models import Doctor, WorkingHour, DayOff
from django.utils.translation import gettext_lazy as _

class WorkingHourForm(forms.ModelForm):
    """Working hours form"""

    class Meta:
        model = WorkingHour
        fields = ['day_of_week', 'start_time', 'end_time', 'is_active']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time:
            if start_time >= end_time:
                raise ValidationError(_('End time must be after start time'))

        return cleaned_data


class DayOffForm(forms.ModelForm):
    """Day off form"""

    class Meta:
        model = DayOff
        fields = ['date', 'reason', 'is_recurring']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'min': 'today'}),
            'reason': forms.TextInput(attrs={'placeholder': _('e.g., Vacation, Conference')}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'is_recurring':
                self.fields[field].widget.attrs.update({
                    'class': 'w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-purple-500'
                })


class DoctorSearchForm(forms.Form):
    """Doctor search and filter form"""

    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': _('Search doctors...'),
            'class': 'w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-purple-500'
        })
    )

    specialization = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-purple-500'
        })
    )

    clinic = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-purple-500'
        })
    )

    min_rating = forms.DecimalField(
        required=False,
        min_value=0,
        max_value=5,
        widget=forms.NumberInput(attrs={
            'placeholder': _('Min Rating'),
            'class': 'w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-purple-500'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Specialization
        from apps.clinics.models import Clinic

        # Populate specialization choices
        specializations = Specialization.objects.all()
        self.fields['specialization'].choices = [('', _('All Specializations'))] + [
            (s.slug, s.name) for s in specializations
        ]

        # Populate clinic choices
        clinics = Clinic.objects.filter(is_active=True)
        self.fields['clinic'].choices = [('', _('All Clinics'))] + [
            (c.slug, c.name) for c in clinics
        ]


class PaymentForm(forms.Form):
    # هذا الحقل هو الحل للمشكلة، نجعله مخفياً لأنه افتراضي 'card'
    payment_method = forms.CharField(
        widget=forms.HiddenInput(),
        initial='card'
    )

    card_number = forms.CharField(
        label=_("Card Number"),
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-purple-500',
            'placeholder': '0000 0000 0000 0000',
            'maxlength': '19'
        })
    )

    cardholder_name = forms.CharField(
        label=_("Cardholder Name"),
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-purple-500',
            'placeholder': _('Full Name on Card')
        })
    )

    expiry_month = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-purple-500',
            'placeholder': 'MM',
            'maxlength': '2'
        })
    )

    expiry_year = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-purple-500',
            'placeholder': 'YY',
            'maxlength': '2'
        })
    )

    cvv = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-purple-500',
            'placeholder': '***',
            'maxlength': '4'
        })
    )

    save_card = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded'
        })
    )