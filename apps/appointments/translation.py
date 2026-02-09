"""
Translation configuration for Appointments app
"""
from modeltranslation.translator import register, TranslationOptions
from .models import Appointment


@register(Appointment)
class AppointmentTranslationOptions(TranslationOptions):
    """Translation options for Appointment model"""
    fields = ('symptoms', 'notes', 'cancellation_reason')
