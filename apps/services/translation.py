from modeltranslation.translator import register, TranslationOptions
from .models import Service

@register(Service)
class ServiceTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'preparation_instructions')
