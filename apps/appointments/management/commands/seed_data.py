from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker

from apps.clinics.models import Clinic
from apps.doctors.models import Doctor, Specialization, WorkingHour
from apps.services.models import Service
from apps.appointments.models import Appointment

from datetime import datetime
from collections import defaultdict
import random

User = get_user_model()
fake = Faker(['en_US'])


def safe(value: str, max_len: int) -> str:
    return value[:max_len]


class Command(BaseCommand):
    help = 'Seed database with fast, safe, non-blocking fake data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting seeding...')

        self.clear_data()

        self.stdout.write('→ Specializations')
        specs = self.create_specializations()

        self.stdout.write('→ Clinics')
        clinics = self.create_clinics()

        self.stdout.write('→ Doctors & Working Hours')
        doctors = self.create_doctors(clinics, specs)

        self.stdout.write('→ Services')
        services = self.create_services(clinics)

        self.stdout.write('→ Patients')
        patients = self.create_patients()

        self.stdout.write('→ Appointments')
        self.create_appointments(doctors, services, patients)

        self.stdout.write(self.style.SUCCESS('✅ Seeding finished successfully'))

    # -------------------------
    # Clear
    # -------------------------
    def clear_data(self):
        Appointment.objects.all().delete()
        Service.objects.all().delete()
        WorkingHour.objects.all().delete()
        Doctor.objects.all().delete()
        Clinic.objects.all().delete()
        Specialization.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    # -------------------------
    # Specializations
    # -------------------------
    def create_specializations(self):
        names = [
            'Cardiology', 'Dermatology', 'Pediatrics', 'Orthopedics',
            'Neurology', 'Ophthalmology', 'Dentistry', 'General Medicine',
            'Gynecology', 'Psychiatry'
        ]

        return [
            Specialization.objects.create(
                name=name,
                description=safe(fake.text(150), 200),
                icon='mdi:medical-bag'
            )
            for name in names
        ]

    # -------------------------
    # Clinics
    # -------------------------
    def create_clinics(self):
        cities = ['Riyadh', 'Jeddah', 'Dammam', 'Mecca', 'Medina']
        clinics = []

        for _ in range(20):
            clinic = Clinic.objects.create(
                name=safe(fake.company() + ' Medical Center', 200),
                description=safe(fake.text(250), 300),
                address=safe(fake.address().replace('\n', ' '), 500),
                city=random.choice(cities),
                phone=fake.numerify('##########'),
                email=fake.email(),
                rating=round(random.uniform(3.5, 5.0), 2),
                total_reviews=random.randint(10, 500),
            )
            clinics.append(clinic)

        return clinics

    # -------------------------
    # Doctors + Working Hours
    # -------------------------
    def create_doctors(self, clinics, specs):
        doctors = []
        working_hours = []

        for i in range(80):
            user = User.objects.create_user(
                email=f"doctor{i}@medibook.com",
                password="password123",
                first_name=safe(fake.first_name(), 30),
                last_name=safe(fake.last_name(), 30),
                role=User.Role.DOCTOR,
            )

            doctor = Doctor.objects.create(
                user=user,
                clinic=random.choice(clinics),
                specialization=random.choice(specs),
                license_number=f"LIC{i:05d}",
                experience_years=random.randint(1, 30),
                education=safe(fake.text(120), 200),
                bio=safe(fake.text(300), 500),
                consultation_fee=random.randint(100, 500),
                rating=round(random.uniform(3.0, 5.0), 2),
                total_reviews=random.randint(5, 200),
                total_patients=random.randint(50, 2000),
                is_verified=True,
            )

            doctors.append(doctor)

            for day in range(6):
                if random.random() > 0.25:
                    working_hours.append(
                        WorkingHour(
                            doctor=doctor,
                            day_of_week=day,
                            start_time=datetime.strptime('09:00', '%H:%M').time(),
                            end_time=datetime.strptime('17:00', '%H:%M').time(),
                        )
                    )

        # 🔥 السرعة هنا
        WorkingHour.objects.bulk_create(working_hours)

        return doctors

    # -------------------------
    # Services
    # -------------------------
    def create_services(self, clinics):
        names = [
            'General Consultation', 'Follow-up Visit', 'Emergency Visit',
            'Lab Tests', 'X-Ray', 'MRI', 'Ultrasound', 'ECG'
        ]

        services = []
        for clinic in clinics:
            for _ in range(random.randint(4, 6)):
                services.append(
                    Service.objects.create(
                        clinic=clinic,
                        name=random.choice(names),
                        description=safe(fake.text(120), 150),
                        duration_minutes=random.choice([15, 30, 45, 60]),
                        price=random.randint(50, 300),
                    )
                )
        return services

    # -------------------------
    # Patients
    # -------------------------
    def create_patients(self):
        return [
            User.objects.create_user(
                email=f"patient{i}@medibook.com",
                password="password123",
                first_name=safe(fake.first_name(), 30),
                last_name=safe(fake.last_name(), 30),
                role=User.Role.PATIENT,
            )
            for i in range(50)
        ]

    # -------------------------
    # Appointments (Optimized)
    # -------------------------
    def create_appointments(self, doctors, services, patients):
        statuses = list(Appointment.Status.values)

        services_by_clinic = defaultdict(list)
        for service in services:
            services_by_clinic[service.clinic_id].append(service)

        for _ in range(300):
            doctor = random.choice(doctors)
            clinic_services = services_by_clinic.get(doctor.clinic_id)
            if not clinic_services:
                continue

            Appointment.objects.create(
                patient=random.choice(patients),
                doctor=doctor,
                clinic=doctor.clinic,
                service=random.choice(clinic_services),
                date=fake.date_between('-14d', '+14d'),
                start_time=datetime.strptime('10:00', '%H:%M').time(),
                symptoms='Routine check',
                status=random.choice(statuses),
            )
