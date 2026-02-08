from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


class PatientRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure user is a patient"""

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_patient

    def handle_no_permission(self):
        messages.error(self.request, _('You must be a patient to access this page'))
        return redirect('dashboard:index')


class DoctorRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure user is a doctor"""

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_doctor

    def handle_no_permission(self):
        messages.error(self.request, _('You must be a doctor to access this page'))
        return redirect('dashboard:index')


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure user is an admin"""

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin_user

    def handle_no_permission(self):
        messages.error(self.request, _('You must be an admin to access this page'))
        return redirect('dashboard:index')