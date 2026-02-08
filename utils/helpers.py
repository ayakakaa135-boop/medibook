from datetime import datetime, timedelta
from django.utils import timezone



def get_available_time_slots(doctor, date, duration_minutes=30):
    from apps.doctors.models import WorkingHour, DayOff
    from apps.appointments.models import Appointment
    from datetime import datetime, timedelta

    # 1. إذا كان يوم إجازة، لا توجد فترات
    if DayOff.objects.filter(doctor=doctor, date=date).exists():
        return []

    # 2. جلب ساعات العمل ووجود مواعيد مسبقة
    day_of_week = date.weekday()
    working_hours = WorkingHour.objects.filter(doctor=doctor, day_of_week=day_of_week, is_active=True)
    existing_appointments = Appointment.objects.filter(
        doctor=doctor, date=date, status__in=['PENDING', 'CONFIRMED']
    ).values_list('start_time', flat=True)

    slots = []
    now = datetime.now()

    for wh in working_hours:
        current_time = datetime.combine(date, wh.start_time)
        end_time = datetime.combine(date, wh.end_time)

        while current_time < end_time:
            slot_time = current_time.time()

            # تحسين: منع عرض أوقات قديمة في نفس اليوم
            is_past = (date == now.date() and slot_time < now.time())

            if slot_time not in existing_appointments and not is_past:
                slots.append({
                    'time': slot_time.strftime('%H:%M'),
                    'formatted': current_time.strftime('%I:%M %p')
                })
            current_time += timedelta(minutes=duration_minutes)
    return slots


def calculate_appointment_end_time(start_time, duration_minutes):
    """Calculate appointment end time"""
    start_datetime = datetime.combine(datetime.today(), start_time)
    end_datetime = start_datetime + timedelta(minutes=duration_minutes)
    return end_datetime.time()


def is_appointment_in_working_hours(doctor, date, start_time):
    """Check if appointment time is within doctor's working hours"""
    from apps.doctors.models import WorkingHour

    day_of_week = date.weekday()
    working_hours = WorkingHour.objects.filter(
        doctor=doctor,
        day_of_week=day_of_week,
        is_active=True
    )

    for wh in working_hours:
        if wh.start_time <= start_time < wh.end_time:
            return True

    return False