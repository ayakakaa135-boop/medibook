from modeltranslation.translator import register, TranslationOptions
from .models import Specialization, Doctor

@register(Specialization)
class SpecializationTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

@register(Doctor)
class DoctorTranslationOptions(TranslationOptions):
    fields = ('education', 'bio')
