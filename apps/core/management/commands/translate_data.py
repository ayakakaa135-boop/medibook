import os
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.clinics.models import Clinic
from apps.doctors.models import Doctor, Specialization
from apps.services.models import Service
from openai import OpenAI

class Command(BaseCommand):
    help = 'Translate existing database data to Arabic using LLM'

    def handle(self, *args, **kwargs):
        client = OpenAI()
        
        self.stdout.write('Translating Specializations...')
        for obj in Specialization.objects.all():
            if not obj.name_ar:
                obj.name_ar = self.translate(client, obj.name)
            if not obj.description_ar and obj.description:
                obj.description_ar = self.translate(client, obj.description)
            obj.save()

        self.stdout.write('Translating Clinics...')
        for obj in Clinic.objects.all():
            if not obj.name_ar:
                obj.name_ar = self.translate(client, obj.name)
            if not obj.description_ar:
                obj.description_ar = self.translate(client, obj.description)
            if not obj.address_ar:
                obj.address_ar = self.translate(client, obj.address)
            if not obj.city_ar:
                obj.city_ar = self.translate(client, obj.city)
            obj.save()

        self.stdout.write('Translating Doctors...')
        for obj in Doctor.objects.all():
            if not obj.education_ar and obj.education:
                obj.education_ar = self.translate(client, obj.education)
            if not obj.bio_ar and obj.bio:
                obj.bio_ar = self.translate(client, obj.bio)
            obj.save()

        self.stdout.write('Translating Services...')
        for obj in Service.objects.all():
            if not obj.name_ar:
                obj.name_ar = self.translate(client, obj.name)
            if not obj.description_ar:
                obj.description_ar = self.translate(client, obj.description)
            if not obj.preparation_instructions_ar and obj.preparation_instructions:
                obj.preparation_instructions_ar = self.translate(client, obj.preparation_instructions)
            obj.save()

        self.stdout.write(self.style.SUCCESS('Successfully translated data'))

    def translate(self, client, text):
        if not text:
            return ""
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are a professional medical translator. Translate the following text to Arabic. Return only the translation."},
                    {"role": "user", "content": text}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error translating '{text}': {e}"))
            return text
