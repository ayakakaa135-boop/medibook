from modeltranslation.translator import register, TranslationOptions
from .models import Clinic

@register(Clinic)
class ClinicTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'address', 'city')
