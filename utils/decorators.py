from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


def patient_required(view_func):
    """Decorator to ensure user is a patient"""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')

        if not request.user.is_patient:
            messages.error(request, _('You must be a patient to access this page'))
            return redirect('dashboard:index')

        return view_func(request, *args, **kwargs)

    return wrapper


def doctor_required(view_func):
    """Decorator to ensure user is a doctor"""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')

        if not request.user.is_doctor:
            messages.error(request, _('You must be a doctor to access this page'))
            return redirect('dashboard:index')

        return view_func(request, *args, **kwargs)

    return wrapper


def admin_required(view_func):
    """Decorator to ensure user is an admin"""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')

        if not request.user.is_admin_user:
            messages.error(request, _('You must be an admin to access this page'))
            return redirect('dashboard:index')

        return view_func(request, *args, **kwargs)

    return wrapper