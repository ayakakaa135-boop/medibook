"""
Fix slugs for existing clinics and services
"""
import os
import django
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.clinics.models import Clinic
from apps.services.models import Service
from apps.doctors.models import Specialization

print('🔧 Fixing slugs for existing records...\n')

# Fix specialization slugs FIRST
print('📍 Fixing specialization slugs...')
for spec in Specialization.objects.all():
    spec.slug = ''  # Clear slug to force regeneration  
    spec.save()
    print(f'  ✓ {spec.name_ar or spec.name_en or spec.name} -> slug: {spec.slug}')

print(f'\n✓ Fixed {Specialization.objects.count()} specializations')

# Fix clinic slugs
print('\n📍 Fixing clinic slugs...')
for clinic in Clinic.objects.all():
    clinic.slug = ''  # Clear slug to force regeneration
    clinic.save()
    print(f'  ✓ {clinic.name_ar or clinic.name_en or clinic.name} -> slug: {clinic.slug}')

print(f'\n✓ Fixed {Clinic.objects.count()} clinics')

# Fix service slugs
print('\n📍 Fixing service slugs...')
for service in Service.objects.all():
    service.slug = ''  # Clear slug to force regeneration
    service.save()
    print(f'  ✓ {service.name_ar or service.name_en or service.name} -> slug: {service.slug}')

print(f'\n✓ Fixed {Service.objects.count()} services')

print('\n✅ All slugs fixed successfully!')
