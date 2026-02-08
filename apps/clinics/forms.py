from django import forms
from .models import Clinic
from django.utils.translation import gettext_lazy as _

class ClinicSearchForm(forms.Form):
    """Clinic search and filter form"""

    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': _('Search clinics...'),
            'class': 'w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-purple-500',
            'hx-get': '/clinics/',
            'hx-trigger': 'keyup changed delay:500ms',
            'hx-target': '#clinic-list',
        })
    )

    city = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select(attrs={
            'class': 'px-4 py-2 rounded-lg border focus:ring-2 focus:ring-purple-500',
            'hx-get': '/clinics/',
            'hx-trigger': 'change',
            'hx-target': '#clinic-list',
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cities = Clinic.objects.filter(is_active=True).values_list('city', flat=True).distinct()
        self.fields['city'].choices = [('', _('All Cities'))] + [(c, c) for c in cities]