from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from .models import User, Profile


class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form"""

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-purple-500'
            })


class ProfileUpdateForm(forms.ModelForm):
    """Profile update form"""

    class Meta:
        model = Profile
        fields = [
            'avatar', 'phone', 'address', 'city', 'country',
            'date_of_birth', 'bio', 'language', 'timezone',
            'email_notifications', 'sms_notifications'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'bio': forms.Textarea(attrs={'rows': 4}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['email_notifications', 'sms_notifications']:
                self.fields[field].widget.attrs.update({
                    'class': 'w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-purple-500'
                })


class UserUpdateForm(forms.ModelForm):
    """User basic info update form"""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-purple-500'
            })

