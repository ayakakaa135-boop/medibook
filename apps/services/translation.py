"""
Translation configuration for Services app
"""
from modeltranslation.translator import register, TranslationOptions
from .models import Service


@register(Service)
class ServiceTranslationOptions(TranslationOptions):
    """Translation options for Service model"""
    fields = ('name', 'description', 'preparation_instructions')
