"""
Management command to generate dummy bilingual data (Arabic/English)
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.clinics.models import Clinic
from apps.doctors.models import Specialization, Doctor
from apps.services.models import Service
from apps.appointments.models import Appointment
from datetime import datetime, timedelta
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate dummy bilingual data for MediBook'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to generate dummy data...'))

        # Create users
        self.stdout.write('Creating users...')
        admin_user = self.create_or_get_user('admin@medibook.com', 'محمد', 'الأحمد', is_staff=True, is_superuser=True)
        doctor_user1 = self.create_or_get_user('doctor1@medibook.com', 'أحمد', 'السعيد')
        doctor_user2 = self.create_or_get_user('doctor2@medibook.com', 'فاطمة', 'الحسن')
        patient_user1 = self.create_or_get_user('patient1@medibook.com', 'سارة', 'محمود')
        patient_user2 = self.create_or_get_user('patient2@medibook.com', 'علي', 'يوسف')

        # Create clinics
        self.stdout.write('Creating clinics...')
        clinic1 = self.create_clinic(
            name_ar='عيادة الأمل الطبية',
            name_en='Al-Amal Medical Clinic',
            description_ar='عيادة طبية متخصصة تقدم خدمات شاملة في مجال الرعاية الصحية الأولية والتخصصات المختلفة',
            description_en='A specialized medical clinic providing comprehensive services in primary healthcare and various specialties',
            address_ar='شارع الملك فهد، الرياض، المملكة العربية السعودية',
            address_en='King Fahd Street, Riyadh, Saudi Arabia',
            city='الرياض',
            phone='+966112345678',
            email='info@alamal.clinic'
        )

        clinic2 = self.create_clinic(
            name_ar='مركز النور الطبي',
            name_en='Al-Nour Medical Center',
            description_ar='مركز طبي حديث مجهز بأحدث التقنيات الطبية ويضم نخبة من الأطباء المتخصصين',
            description_en='A modern medical center equipped with the latest medical technologies and staffed by elite specialized doctors',
            address_ar='طريق الملك عبدالعزيز، جدة، المملكة العربية السعودية',
            address_en='King Abdulaziz Road, Jeddah, Saudi Arabia',
            city='جدة',
            phone='+966126789012',
            email='contact@alnour.center'
        )

        # Create specializations
        self.stdout.write('Creating specializations...')
        spec_pediatrics = self.create_specialization(
            name_ar='طب الأطفال',
            name_en='Pediatrics',
            description_ar='تخصص طبي يهتم بصحة الأطفال من الولادة حتى سن المراهقة',
            description_en='Medical specialty focused on the health of children from birth to adolescence',
            icon='fa-baby'
        )

        spec_cardiology = self.create_specialization(
            name_ar='أمراض القلب',
            name_en='Cardiology',
            description_ar='تخصص طبي يعنى بدراسة وعلاج أمراض القلب والأوعية الدموية',
            description_en='Medical specialty dealing with disorders of the heart and blood vessels',
            icon='fa-heartbeat'
        )

        spec_dermatology = self.create_specialization(
            name_ar='الأمراض الجلدية',
            name_en='Dermatology',
            description_ar='تخصص طبي يركز على تشخيص وعلاج أمراض الجلد والشعر والأظافر',
            description_en='Medical specialty focused on diagnosing and treating skin, hair, and nail conditions',
            icon='fa-hand-holding-medical'
        )

        # Create doctors
        self.stdout.write('Creating doctors...')
        doctor1 = self.create_doctor(
            user=doctor_user1,
            clinic=clinic1,
            specialization=spec_pediatrics,
            license_number='MED-2020-12345',
            experience_years=8,
            bio_ar='طبيب أطفال متخصص مع خبرة 8 سنوات في علاج الأطفال والرضع. حاصل على شهادة البورد السعودي في طب الأطفال.',
            bio_en='Specialized pediatrician with 8 years of experience in treating children and infants. Saudi Board certified in Pediatrics.',
            education_ar='بكالوريوس الطب والجراحة - جامعة الملك سعود\nالبورد السعودي في طب الأطفال',
            education_en='MBBS - King Saud University\nSaudi Board in Pediatrics',
            consultation_fee=Decimal('300.00')
        )

        doctor2 = self.create_doctor(
            user=doctor_user2,
            clinic=clinic2,
            specialization=spec_cardiology,
            license_number='MED-2018-67890',
            experience_years=12,
            bio_ar='استشارية أمراض القلب مع خبرة واسعة في تشخيص وعلاج أمراض القلب والشرايين. متخصصة في القسطرة القلبية.',
            bio_en='Cardiology consultant with extensive experience in diagnosing and treating heart and artery diseases. Specialized in cardiac catheterization.',
            education_ar='بكالوريوس الطب والجراحة - جامعة الملك عبدالعزيز\nزمالة أمراض القلب - المملكة المتحدة',
            education_en='MBBS - King Abdulaziz University\nCardiology Fellowship - United Kingdom',
            consultation_fee=Decimal('500.00')
        )

        # Create services
        self.stdout.write('Creating services...')
        service1 = self.create_service(
            clinic=clinic1,
            name_ar='فحص شامل للأطفال',
            name_en='Comprehensive Child Checkup',
            description_ar='فحص طبي شامل للأطفال يشمل الفحص السريري والتطعيمات ومتابعة النمو',
            description_en='Comprehensive medical examination for children including clinical examination, vaccinations, and growth monitoring',
            preparation_instructions_ar='لا يوجد تحضيرات خاصة. يرجى إحضار دفتر التطعيمات إن وجد.',
            preparation_instructions_en='No special preparations needed. Please bring vaccination records if available.',
            duration_minutes=45,
            price=Decimal('250.00')
        )

        service2 = self.create_service(
            clinic=clinic2,
            name_ar='تخطيط القلب الكهربائي (ECG)',
            name_en='Electrocardiogram (ECG)',
            description_ar='فحص كهربائية القلب لتقييم النشاط الكهربائي للقلب واكتشاف أي مشاكل في نظم القلب',
            description_en='Heart electrical activity test to assess cardiac electrical activity and detect any rhythm problems',
            preparation_instructions_ar='تجنب المجهود البدني الشديد قبل الفحص بساعة. ارتداء ملابس مريحة.',
            preparation_instructions_en='Avoid strenuous physical activity one hour before the test. Wear comfortable clothing.',
            duration_minutes=30,
            price=Decimal('200.00')
        )

        service3 = self.create_service(
            clinic=clinic1,
            name_ar='فحص الدم الشامل',
            name_en='Complete Blood Count (CBC)',
            description_ar='فحص مختبري شامل للدم لتقييم الصحة العامة واكتشاف مجموعة متنوعة من الاضطرابات',
            description_en='Comprehensive laboratory blood test to assess overall health and detect a variety of disorders',
            preparation_instructions_ar='الصيام لمدة 8-12 ساعة قبل الفحص. يمكن شرب الماء فقط.',
            preparation_instructions_en='Fasting for 8-12 hours before the test. Water only is allowed.',
            duration_minutes=15,
            price=Decimal('150.00')
        )

        # Create appointments
        self.stdout.write('Creating appointments...')
        today = datetime.now().date()
        
        # Past appointment
        self.create_appointment(
            patient=patient_user1,
            doctor=doctor1,
            clinic=clinic1,
            service=service1,
            date=today - timedelta(days=5),
            start_time='10:00',
            symptoms_ar='ارتفاع في درجة الحرارة وسعال',
            symptoms_en='High temperature and cough',
            notes_ar='المريض يعاني من أعراض نزلة برد منذ 3 أيام',
            notes_en='Patient has been experiencing cold symptoms for 3 days',
            status='COMPLETED'
        )

        # Upcoming appointment
        self.create_appointment(
            patient=patient_user2,
            doctor=doctor2,
            clinic=clinic2,
            service=service2,
            date=today + timedelta(days=3),
            start_time='14:00',
            symptoms_ar='ألم في الصدر وضيق في التنفس',
            symptoms_en='Chest pain and shortness of breath',
            notes_ar='المريض يطلب فحص دوري للقلب',
            notes_en='Patient requests routine heart examination',
            status='CONFIRMED'
        )

        # Cancelled appointment
        self.create_appointment(
            patient=patient_user1,
            doctor=doctor1,
            clinic=clinic1,
            service=service3,
            date=today - timedelta(days=2),
            start_time='09:00',
            symptoms_ar='فحص دوري',
            symptoms_en='Routine checkup',
            notes_ar='فحص سنوي',
            notes_en='Annual checkup',
            status='CANCELED',
            cancellation_reason_ar='المريض غير قادر على الحضور بسبب ظروف طارئة',
            cancellation_reason_en='Patient unable to attend due to emergency circumstances'
        )

        self.stdout.write(self.style.SUCCESS('✅ Dummy data generation completed successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Created:'))
        self.stdout.write(f'  - {User.objects.count()} users')
        self.stdout.write(f'  - {Clinic.objects.count()} clinics')
        self.stdout.write(f'  - {Specialization.objects.count()} specializations')
        self.stdout.write(f'  - {Doctor.objects.count()} doctors')
        self.stdout.write(f'  - {Service.objects.count()} services')
        self.stdout.write(f'  - {Appointment.objects.count()} appointments')

    def create_or_get_user(self, email, first_name, last_name, is_staff=False, is_superuser=False):
        """Create or get existing user"""
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'is_staff': is_staff,
                'is_superuser': is_superuser,
                'is_active': True,
            }
        )
        if created:
            user.set_password('password123')  # Default password
            user.save()
            self.stdout.write(f'  ✓ Created user: {email}')
        else:
            self.stdout.write(f'  ℹ User already exists: {email}')
        return user

    def create_clinic(self, **kwargs):
        """Create or get existing clinic"""
        clinic, created = Clinic.objects.get_or_create(
            email=kwargs['email'],
            defaults=kwargs
        )
        if created:
            self.stdout.write(f'  ✓ Created clinic: {kwargs["name_ar"]}')
        else:
            self.stdout.write(f'  ℹ Clinic already exists: {kwargs["name_ar"]}')
        return clinic

    def create_specialization(self, **kwargs):
        """Create or get existing specialization"""
        # Extract name fields
        name_ar = kwargs.pop('name_ar')
        name_en = kwargs.pop('name_en')
        
        # Try to get existing by either name
        try:
            spec = Specialization.objects.get(name_ar=name_ar)
            self.stdout.write(f'  ℹ Specialization already exists: {name_ar}')
            return spec
        except Specialization.DoesNotExist:
            pass
        
        # Create new specialization
        # Set the main 'name' field to Arabic first for slug generation
        spec = Specialization(name=name_ar, **kwargs)
        spec.name_ar = name_ar
        spec.name_en = name_en
        spec.save()
        self.stdout.write(f'  ✓ Created specialization: {name_ar}')
        return spec

    def create_doctor(self, **kwargs):
        """Create or get existing doctor"""
        doctor, created = Doctor.objects.get_or_create(
            user=kwargs['user'],
            defaults=kwargs
        )
        if created:
            self.stdout.write(f'  ✓ Created doctor: Dr. {kwargs["user"].get_full_name()}')
        else:
            self.stdout.write(f'  ℹ Doctor already exists: Dr. {kwargs["user"].get_full_name()}')
        return doctor

    def create_service(self, **kwargs):
        """Create service"""
        service = Service.objects.create(**kwargs)
        self.stdout.write(f'  ✓ Created service: {kwargs["name_ar"]}')
        return service

    def create_appointment(self, **kwargs):
        """Create appointment"""
        appointment = Appointment.objects.create(**kwargs)
        self.stdout.write(f'  ✓ Created appointment: {kwargs["patient"].get_full_name()} - Dr. {kwargs["doctor"].user.get_full_name()}')
        return appointment
