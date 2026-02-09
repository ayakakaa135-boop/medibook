"""
Script to populate database with bilingual dummy data
Run this with: python populate_data.py
"""
import os
import django
import sys

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.clinics.models import Clinic
from apps.doctors.models import Specialization, Doctor
from apps.services.models import Service
from apps.appointments.models import Appointment
from datetime import datetime, timedelta
from decimal import Decimal

User = get_user_model()

def main():
    print('🚀 Starting bilingual data population...\n')
    
    # Clear existing data (to avoid conflicts)
    print('🧹 Clearing existing data...')
    from django.db import connection
    
    Appointment.objects.all().delete()
    Service.objects.all().delete()
    Doctor.objects.all().delete()
    
    # Delete ALL specializations using raw SQL to bypass slug issues
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM doctors_specialization;")
    print('✓ Cleared all existing data')
    
    # Create Users
    print('\n👥 Creating users...')
    admin, _ = User.objects.get_or_create(
        email='admin@medibook.com',
        defaults={
            'first_name': 'محمد',
            'last_name': 'الأحمد',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True
        }
    )
    admin.set_password('admin123')
    admin.save()
    print('✓ Admin user created')
    
    doctor_user1, _ = User.objects.get_or_create(
        email='dr.ahmad@medibook.com',
        defaults={
            'first_name': 'أحمد',
            'last_name': 'السعيد',
            'is_active': True
        }
    )
    doctor_user1.set_password('doctor123')
    doctor_user1.save()
    print('✓ Doctor 1 created')
    
    doctor_user2, _ = User.objects.get_or_create(
        email='dr.fatima@medibook.com',
        defaults={
            'first_name': 'فاطمة',
            'last_name': 'الحسن',
            'is_active': True
        }
    )
    doctor_user2.set_password('doctor123')
    doctor_user2.save()
    print('✓ Doctor 2 created')
    
    patient1, _ = User.objects.get_or_create(
        email='sara@example.com',
        defaults={
            'first_name': 'سارة',
            'last_name': 'محمود',
            'is_active': True
        }
    )
    patient1.set_password('patient123')
    patient1.save()
    
    patient2, _ = User.objects.get_or_create(
        email='ali@example.com',
        defaults={
            'first_name': 'علي',
            'last_name': 'يوسف',
            'is_active': True
        }
    )
    patient2.set_password('patient123')
    patient2.save()
    print('✓ Patients created')
    
    # Create Clinics
    print('\n🏥 Creating clinics...')
    clinic1, _ = Clinic.objects.get_or_create(
        email='info@alamal.clinic',
        defaults={
            'name': 'عيادة الأمل الطبية',
            'name_ar': 'عيادة الأمل الطبية',
            'name_en': 'Al-Amal Medical Clinic',
            'description': 'عيادة طبية متخصصة تقدم خدمات شاملة في مجال الرعاية الصحية',
            'description_ar': 'عيادة طبية متخصصة تقدم خدمات شاملة في مجال الرعاية الصحية الأولية والتخصصات المختلفة',
            'description_en': 'A specialized medical clinic providing comprehensive services in primary healthcare and various specialties',
            'address': 'شارع الملك فهد، الرياض',
            'address_ar': 'شارع الملك فهد، الرياض، المملكة العربية السعودية',
            'address_en': 'King Fahd Street, Riyadh, Saudi Arabia',
            'city': 'الرياض',
            'phone': '+966112345678',
        }
    )
    print('✓ Clinic: عيادة الأمل الطبية')
    
    clinic2, _ = Clinic.objects.get_or_create(
        email='contact@alnour.center',
        defaults={
            'name': 'مركز النور الطبي',
            'name_ar': 'مركز النور الطبي',
            'name_en': 'Al-Nour Medical Center',
            'description': 'مركز طبي حديث مجهز بأحدث التقنيات الطبية',
            'description_ar': 'مركز طبي حديث مجهز بأحدث التقنيات الطبية ويضم نخبة من الأطباء المتخصصين',
            'description_en': 'A modern medical center equipped with the latest medical technologies and staffed by elite specialized doctors',
            'address': 'طريق الملك عبدالعزيز، جدة',
            'address_ar': 'طريق الملك عبدالعزيز، جدة، المملكة العربية السعودية',
            'address_en': 'King Abdulaziz Road, Jeddah, Saudi Arabia',
            'city': 'جدة',
            'phone': '+966126789012',
        }
    )
    print('✓ Clinic: مركز النور الطبي')
    
    # Create Specializations
    print('\n👨‍⚕️ Creating specializations...')
    spec1 = Specialization(
        name='طب الأطفال',
        description='تخصص طبي يهتم بصحة الأطفال',
        icon='fa-baby'
    )
    spec1.name_ar = 'طب الأطفال'
    spec1.name_en = 'Pediatrics'
    spec1.description_ar = 'تخصص طبي يهتم بصحة الأطفال من الولادة حتى سن المراهقة'
    spec1.description_en = 'Medical specialty focused on the health of children from birth to adolescence'
    spec1.save()
    print('✓ Specialization: طب الأطفال / Pediatrics')
    
    spec2 = Specialization(
        name='أمراض القلب',
        description='تخصص طبي يعنى بدراسة وعلاج أمراض القلب',
        icon='fa-heartbeat'
    )
    spec2.name_ar = 'أمراض القلب'
    spec2.name_en = 'Cardiology'
    spec2.description_ar = 'تخصص طبي يعنى بدراسة وعلاج أمراض القلب والأوعية الدموية'
    spec2.description_en = 'Medical specialty dealing with disorders of the heart and blood vessels'
    spec2.save()
    print('✓ Specialization: أمراض القلب / Cardiology')
    
    spec3 = Specialization(
        name='الأمراض الجلدية',
        description='تخصص طبي يركز على تشخيص وعلاج أمراض الجلد',
        icon='fa-hand-holding-medical'
    )
    spec3.name_ar = 'الأمراض الجلدية'
    spec3.name_en = 'Dermatology'
    spec3.description_ar = 'تخصص طبي يركز على تشخيص وعلاج أمراض الجلد والشعر والأظافر'
    spec3.description_en = 'Medical specialty focused on diagnosing and treating skin, hair, and nail conditions'
    spec3.save()
    print('✓ Specialization: الأمراض الجلدية / Dermatology')
    
    # Create Doctors
    print('\n👨‍⚕️ Creating doctors...')
    doctor1, _ = Doctor.objects.get_or_create(
        user=doctor_user1,
        defaults={
            'clinic': clinic1,
            'specialization': spec1,
            'license_number': 'MED-2020-12345',
            'experience_years': 8,
            'bio': 'طبيب أطفال متخصص مع خبرة 8 سنوات',
            'bio_ar': 'طبيب أطفال متخصص مع خبرة 8 سنوات في علاج الأطفال والرضع. حاصل على شهادة البورد السعودي في طب الأطفال.',
            'bio_en': 'Specialized pediatrician with 8 years of experience in treating children and infants. Saudi Board certified in Pediatrics.',
            'education': 'بكالوريوس الطب والجراحة - جامعة الملك سعود',
            'education_ar': 'بكالوريوس الطب والجراحة - جامعة الملك سعود\nالبورد السعودي في طب الأطفال',
            'education_en': 'MBBS - King Saud University\nSaudi Board in Pediatrics',
            'consultation_fee': Decimal('300.00'),
            'is_verified': True
        }
    )
    print('✓ Doctor: أحمد السعيد - طب الأطفال')
    
    doctor2, _ = Doctor.objects.get_or_create(
        user=doctor_user2,
        defaults={
            'clinic': clinic2,
            'specialization': spec2,
            'license_number': 'MED-2018-67890',
            'experience_years': 12,
            'bio': 'استشارية أمراض القلب مع خبرة واسعة',
            'bio_ar': 'استشارية أمراض القلب مع خبرة واسعة في تشخيص وعلاج أمراض القلب والشرايين. متخصصة في القسطرة القلبية.',
            'bio_en': 'Cardiology consultant with extensive experience in diagnosing and treating heart and artery diseases. Specialized in cardiac catheterization.',
            'education': 'بكالوريوس الطب والجراحة - جامعة الملك عبدالعزيز',
            'education_ar': 'بكالوريوس الطب والجراحة - جامعة الملك عبدالعزيز\nزمالة أمراض القلب - المملكة المتحدة',
            'education_en': 'MBBS - King Abdulaziz University\nCardiology Fellowship - United Kingdom',
            'consultation_fee': Decimal('500.00'),
            'is_verified': True
        }
    )
    print('✓ Doctor: فاطمة الحسن - أمراض القلب')
    
    # Create Services
    print('\n🏥 Creating services...')
    service1 = Service.objects.create(
        clinic=clinic1,
        name='فحص شامل للأطفال',
        name_ar='فحص شامل للأطفال',
        name_en='Comprehensive Child Checkup',
        description='فحص طبي شامل للأطفال',
        description_ar='فحص طبي شامل للأطفال يشمل الفحص السريري والتطعيمات ومتابعة النمو',
        description_en='Comprehensive medical examination for children including clinical examination, vaccinations, and growth monitoring',
        preparation_instructions='لا يوجد تحضيرات خاصة',
        preparation_instructions_ar='لا يوجد تحضيرات خاصة. يرجى إحضار دفتر التطعيمات إن وجد.',
        preparation_instructions_en='No special preparations needed. Please bring vaccination records if available.',
        duration_minutes=45,
        price=Decimal('250.00')
    )
    print('✓ Service: فحص شامل للأطفال / Child Checkup')
    
    service2 = Service.objects.create(
        clinic=clinic2,
        name='تخطيط القلب الكهربائي',
        name_ar='تخطيط القلب الكهربائي (ECG)',
        name_en='Electrocardiogram (ECG)',
        description='فحص كهربائية القلب',
        description_ar='فحص كهربائية القلب لتقييم النشاط الكهربائي للقلب واكتشاف أي مشاكل في نظم القلب',
        description_en='Heart electrical activity test to assess cardiac electrical activity and detect any rhythm problems',
        preparation_instructions='تجنب المجهود البدني الشديد قبل الفحص',
        preparation_instructions_ar='تجنب المجهود البدني الشديد قبل الفحص بساعة. ارتداء ملابس مريحة.',
        preparation_instructions_en='Avoid strenuous physical activity one hour before the test. Wear comfortable clothing.',
        duration_minutes=30,
        price=Decimal('200.00')
    )
    print('✓ Service: تخطيط القلب / ECG')
    
    service3 = Service.objects.create(
        clinic=clinic1,
        name='فحص الدم الشامل',
        name_ar='فحص الدم الشامل',
        name_en='Complete Blood Count (CBC)',
        description='فحص مختبري شامل للدم',
        description_ar='فحص مختبري شامل للدم لتقييم الصحة العامة واكتشاف مجموعة متنوعة من الاضطرابات',
        description_en='Comprehensive laboratory blood test to assess overall health and detect a variety of disorders',
        preparation_instructions='الصيام لمدة 8-12 ساعة',
        preparation_instructions_ar='الصيام لمدة 8-12 ساعة قبل الفحص. يمكن شرب الماء فقط.',
        preparation_instructions_en='Fasting for 8-12 hours before the test. Water only is allowed.',
        duration_minutes=15,
        price=Decimal('150.00')
    )
    print('✓ Service: فحص الدم / CBC')
    
    # Create Appointments
    print('\n📅 Creating appointments...')
    from datetime import time as dt_time
    today = datetime.now().date()
    
    # Past completed appointment
    appt1 = Appointment.objects.create(
        patient=patient1,
        doctor=doctor1,
        clinic=clinic1,
        service=service1,
        date=today - timedelta(days=5),
        start_time=dt_time(10, 0),  # 10:00
        symptoms='ارتفاع في درجة الحرارة',
        symptoms_ar='ارتفاع في درجة الحرارة وسعال',
        symptoms_en='High temperature and cough',
        notes='المريض يعاني من أعراض نزلة برد',
        notes_ar='المريض يعاني من أعراض نزلة برد منذ 3 أيام',
        notes_en='Patient has been experiencing cold symptoms for 3 days',
        status='COMPLETED'
    )
    print('✓ Appointment 1: Completed')
    
    # Upcoming confirmed appointment
    appt2 = Appointment.objects.create(
        patient=patient2,
        doctor=doctor2,
        clinic=clinic2,
        service=service2,
        date=today + timedelta(days=3),
        start_time=dt_time(14, 0),  # 14:00
        symptoms='ألم في الصدر',
        symptoms_ar='ألم في الصدر وضيق في التنفس',
        symptoms_en='Chest pain and shortness of breath',
        notes='فحص دوري للقلب',
        notes_ar='المريض يطلب فحص دوري للقلب',
        notes_en='Patient requests routine heart examination',
        status='CONFIRMED'
    )
    print('✓ Appointment 2: Confirmed')
    
    # Cancelled appointment
    appt3 = Appointment.objects.create(
        patient=patient1,
        doctor=doctor1,
        clinic=clinic1,
        service=service3,
        date=today - timedelta(days=2),
        start_time=dt_time(9, 0),  # 09:00
        symptoms='فحص دوري',
        symptoms_ar='فحص دوري',
        symptoms_en='Routine checkup',
        notes='فحص سنوي',
        notes_ar='فحص سنوي',
        notes_en='Annual checkup',
        status='CANCELED',
        cancellation_reason='ظروف طارئة',
        cancellation_reason_ar='المريض غير قادر على الحضور بسبب ظروف طارئة',
        cancellation_reason_en='Patient unable to attend due to emergency circumstances'
    )
    print('✓ Appointment 3: Cancelled')
    
    print('\n✅ Data population completed successfully!')
    print('\n📊 Summary:')
    print(f'  - {User.objects.count()} users')
    print(f'  - {Clinic.objects.count()} clinics')
    print(f'  - {Specialization.objects.count()} specializations')
    print(f'  - {Doctor.objects.count()} doctors')
    print(f'  - {Service.objects.count()} services')
    print(f'  - {Appointment.objects.count()} appointments')
    print('\n🔑 Login credentials:')
    print('  Admin: admin@medibook.com / admin123')
    print('  Doctors: dr.ahmad@medibook.com / doctor123')
    print('           dr.fatima@medibook.com / doctor123')
    print('  Patients: sara@example.com / patient123')
    print('            ali@example.com / patient123')

if __name__ == '__main__':
    main()
