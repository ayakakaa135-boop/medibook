"""
============================================
apps/dashboard/views.py - لوحات التحكم الكاملة
============================================
"""
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Sum, Avg, Q, Max
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta

from apps.users.models import User
from apps.clinics.models import Clinic
from apps.doctors.models import Doctor, Specialization
from apps.appointments.models import Appointment
from apps.services.models import Service


class DashboardRedirectView(LoginRequiredMixin, TemplateView):
    """Redirect to appropriate dashboard based on user role"""

    def get(self, request, *args, **kwargs):
        user = request.user

        if user.is_admin_user:
            return redirect('dashboard:admin')
        elif user.is_doctor:
            return redirect('dashboard:doctor')
        else:
            return redirect('dashboard:patient')


# ============================================
# Patient Dashboard
# ============================================

class PatientDashboardView(LoginRequiredMixin, TemplateView):
    """Patient dashboard"""
    template_name = 'dashboard/patient.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.now().date()

        # Get patient's appointments
        appointments = Appointment.objects.filter(patient=user)

        # Upcoming appointments
        context['upcoming_appointments'] = appointments.filter(
            date__gte=today,
            status__in=['PENDING', 'CONFIRMED']
        ).select_related(
            'doctor__user',
            'doctor__specialization',
            'clinic',
            'service'
        ).order_by('date', 'start_time')[:5]

        # Statistics
        context['stats'] = {
            'total_appointments': appointments.count(),
            'upcoming': appointments.filter(
                date__gte=today,
                status__in=['PENDING', 'CONFIRMED']
            ).count(),
            'completed': appointments.filter(status='COMPLETED').count(),
            'canceled': appointments.filter(status='CANCELED').count(),
        }

        # Recent appointments
        context['recent_appointments'] = appointments.select_related(
            'doctor__user',
            'doctor__specialization',
            'clinic'
        ).order_by('-created_at')[:5]

        # Favorite doctors (most visited)
        context['favorite_doctors'] = Doctor.objects.filter(
            appointments__patient=user
        ).annotate(
            visit_count=Count('appointments')
        ).select_related('user', 'specialization', 'clinic').order_by('-visit_count')[:3]

        return context


# ============================================
# Doctor Dashboard
# ============================================

class DoctorDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Doctor dashboard"""
    template_name = 'dashboard/doctor.html'

    def test_func(self):
        return self.request.user.is_doctor

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        doctor = Doctor.objects.select_related('clinic', 'specialization').get(user=user)

        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        # Today's appointments
        context['today_appointments'] = Appointment.objects.filter(
            doctor=doctor,
            date=today,
            status__in=['PENDING', 'CONFIRMED']
        ).select_related('patient', 'service').order_by('start_time')

        # This week's appointments
        context['week_appointments'] = Appointment.objects.filter(
            doctor=doctor,
            date__range=[week_start, week_end],
            status__in=['PENDING', 'CONFIRMED']
        ).select_related('patient', 'service').order_by('date', 'start_time')

        # Pending appointments (need confirmation)
        context['pending_appointments'] = Appointment.objects.filter(
            doctor=doctor,
            status='PENDING',
            date__gte=today
        ).select_related('patient', 'service').order_by('date', 'start_time')[:5]

        # Statistics
        context['stats'] = {
            'today_count': context['today_appointments'].count(),
            'week_count': context['week_appointments'].count(),
            'pending_count': context['pending_appointments'].count(),
            'total_patients': doctor.total_patients,
            'rating': doctor.rating,
            'total_reviews': doctor.total_reviews,
        }

        # Monthly statistics
        current_month_start = today.replace(day=1)
        context['monthly_stats'] = {
            'appointments': Appointment.objects.filter(
                doctor=doctor,
                date__gte=current_month_start
            ).count(),
            'completed': Appointment.objects.filter(
                doctor=doctor,
                date__gte=current_month_start,
                status='COMPLETED'
            ).count(),
            'revenue': Appointment.objects.filter(
                doctor=doctor,
                date__gte=current_month_start,
                status='COMPLETED'
            ).aggregate(
                total=Sum('service__price')
            )['total'] or 0,
        }

        context['doctor'] = doctor
        return context


class DoctorAnalyticsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Doctor analytics and reports"""
    template_name = 'dashboard/doctor_analytics.html'

    def test_func(self):
        return self.request.user.is_doctor

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = Doctor.objects.get(user=self.request.user)

        # Last 6 months data
        today = timezone.now().date()
        six_months_ago = today - timedelta(days=180)

        # Appointments by month
        appointments_by_month = Appointment.objects.filter(
            doctor=doctor,
            date__gte=six_months_ago
        ).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')

        context['appointments_by_month'] = list(appointments_by_month)

        # Appointments by status
        appointments_by_status = Appointment.objects.filter(
            doctor=doctor
        ).values('status').annotate(
            count=Count('id')
        )

        context['appointments_by_status'] = list(appointments_by_status)

        # Peak hours
        peak_hours = Appointment.objects.filter(
            doctor=doctor,
            status='COMPLETED'
        ).extra(
            select={'hour': 'EXTRACT(hour FROM start_time)'}
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        context['peak_hours'] = list(peak_hours)

        return context


class DoctorPatientsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Doctor's patients list"""
    template_name = 'dashboard/doctor_patients.html'
    context_object_name = 'patients'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_doctor

    def get_queryset(self):
        doctor = Doctor.objects.get(user=self.request.user)

        # Get unique patients with their last appointment
        patients = User.objects.filter(
            appointments__doctor=doctor
        ).distinct().annotate(
            last_visit=Max('appointments__date'),
            total_visits=Count('appointments')
        ).order_by('-last_visit')

        return patients


# ============================================
# Admin Dashboard
# ============================================

class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Admin main dashboard"""
    template_name = 'dashboard/admin.html'

    def test_func(self):
        return self.request.user.is_admin_user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        # Overview statistics
        context['stats'] = {
            'total_clinics': Clinic.objects.filter(is_active=True).count(),
            'total_doctors': Doctor.objects.filter(is_available=True, is_verified=True).count(),
            'total_patients': User.objects.filter(role=User.Role.PATIENT).count(),
            'total_appointments': Appointment.objects.count(),
            'today_appointments': Appointment.objects.filter(date=today).count(),
            'pending_appointments': Appointment.objects.filter(status='PENDING').count(),
            'total_specializations': Specialization.objects.count(),
            'total_services': Service.objects.filter(is_active=True).count(),
        }

        # Revenue statistics
        context['revenue'] = {
            'today': Appointment.objects.filter(
                date=today,
                status='COMPLETED'
            ).aggregate(total=Sum('service__price'))['total'] or 0,

            'this_month': Appointment.objects.filter(
                date__month=today.month,
                date__year=today.year,
                status='COMPLETED'
            ).aggregate(total=Sum('service__price'))['total'] or 0,

            'total': Appointment.objects.filter(
                status='COMPLETED'
            ).aggregate(total=Sum('service__price'))['total'] or 0,
        }

        # Recent appointments
        context['recent_appointments'] = Appointment.objects.select_related(
            'patient',
            'doctor__user',
            'clinic',
            'service'
        ).order_by('-created_at')[:10]

        # Top doctors by appointments
        context['top_doctors'] = Doctor.objects.annotate(
            appointment_count=Count('appointments')
        ).select_related('user', 'specialization', 'clinic').order_by('-appointment_count')[:5]

        # Top specializations
        context['top_specializations'] = Specialization.objects.annotate(
            appointment_count=Count('doctors__appointments')
        ).order_by('-appointment_count')[:5]

        # Top clinics
        context['top_clinics'] = Clinic.objects.annotate(
            appointment_count=Count('appointments')
        ).order_by('-appointment_count')[:5]

        return context


class AdminStatisticsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Admin detailed statistics"""
    template_name = 'dashboard/admin_statistics.html'

    def test_func(self):
        return self.request.user.is_admin_user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Appointment statistics by status
        context['appointments_by_status'] = Appointment.objects.values(
            'status'
        ).annotate(
            count=Count('id')
        ).order_by('-count')

        # Appointments by specialization
        context['appointments_by_specialization'] = Specialization.objects.annotate(
            appointment_count=Count('doctors__appointments')
        ).order_by('-appointment_count')

        # User growth (last 12 months)
        twelve_months_ago = timezone.now() - timedelta(days=365)
        context['user_growth'] = User.objects.filter(
            date_joined__gte=twelve_months_ago
        ).annotate(
            month=TruncMonth('date_joined')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')

        # Appointment distribution by hour
        context['appointments_by_hour'] = Appointment.objects.extra(
            select={'hour': 'EXTRACT(hour FROM start_time)'}
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('hour')

        return context


class AdminReportsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Admin reports"""
    template_name = 'dashboard/admin_reports.html'

    def test_func(self):
        return self.request.user.is_admin_user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        # Daily report
        context['daily_report'] = {
            'date': today,
            'appointments': Appointment.objects.filter(date=today).count(),
            'completed': Appointment.objects.filter(date=today, status='COMPLETED').count(),
            'canceled': Appointment.objects.filter(date=today, status='CANCELED').count(),
            'revenue': Appointment.objects.filter(
                date=today, status='COMPLETED'
            ).aggregate(total=Sum('service__price'))['total'] or 0,
        }

        # Weekly report
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        context['weekly_report'] = {
            'week_start': week_start,
            'week_end': week_end,
            'appointments': Appointment.objects.filter(
                date__range=[week_start, week_end]
            ).count(),
            'completed': Appointment.objects.filter(
                date__range=[week_start, week_end],
                status='COMPLETED'
            ).count(),
            'revenue': Appointment.objects.filter(
                date__range=[week_start, week_end],
                status='COMPLETED'
            ).aggregate(total=Sum('service__price'))['total'] or 0,
        }

        # Monthly report
        month_start = today.replace(day=1)

        context['monthly_report'] = {
            'month': month_start,
            'appointments': Appointment.objects.filter(
                date__month=today.month,
                date__year=today.year
            ).count(),
            'completed': Appointment.objects.filter(
                date__month=today.month,
                date__year=today.year,
                status='COMPLETED'
            ).count(),
            'revenue': Appointment.objects.filter(
                date__month=today.month,
                date__year=today.year,
                status='COMPLETED'
            ).aggregate(total=Sum('service__price'))['total'] or 0,
        }

        return context


class AdminAnalyticsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Admin analytics dashboard"""
    template_name = 'dashboard/admin_analytics.html'

    def test_func(self):
        return self.request.user.is_admin_user


# ============================================
# HTMX Chart Data Endpoints
# ============================================

def appointments_chart_data(request):
    """Get appointments chart data (HTMX)"""
    if not request.user.is_admin_user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    # Last 30 days
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)

    data = Appointment.objects.filter(
        date__gte=thirty_days_ago
    ).annotate(
        day=TruncDate('date')
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')

    labels = [d['day'].strftime('%Y-%m-%d') for d in data]
    values = [d['count'] for d in data]

    return JsonResponse({
        'labels': labels,
        'values': values
    })


def revenue_chart_data(request):
    """Get revenue chart data (HTMX)"""
    if not request.user.is_admin_user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    # Last 12 months
    today = timezone.now().date()
    twelve_months_ago = today - timedelta(days=365)

    data = Appointment.objects.filter(
        date__gte=twelve_months_ago,
        status='COMPLETED'
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('service__price')
    ).order_by('month')

    labels = [d['month'].strftime('%b %Y') for d in data]
    values = [float(d['total']) if d['total'] else 0 for d in data]

    return JsonResponse({
        'labels': labels,
        'values': values
    })