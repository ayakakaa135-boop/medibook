"""
Translation configuration for Doctors app
"""
from modeltranslation.translator import register, TranslationOptions
from .models import Specialization, Doctor


@register(Specialization)
class SpecializationTranslationOptions(TranslationOptions):
    """Translation options for Specialization model"""
    fields = ('name', 'description')


@register(Doctor)
class DoctorTranslationOptions(TranslationOptions):
    """Translation options for Doctor model"""
    fields = ('bio', 'education')
