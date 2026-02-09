"""
Translation configuration for Clinics app
"""
from modeltranslation.translator import register, TranslationOptions
from .models import Clinic


@register(Clinic)
class ClinicTranslationOptions(TranslationOptions):
    """Translation options for Clinic model"""
    fields = ('name', 'description', 'address')
