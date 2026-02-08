from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta

from .models import Doctor, Specialization, WorkingHour, DayOff
from .forms import WorkingHourForm, DayOffForm, DoctorSearchForm
from apps.appointments.models import Appointment
from utils.helpers import get_available_time_slots
from utils.mixins import DoctorRequiredMixin


class DoctorListView(ListView):
    """List all doctors"""
    model = Doctor
    template_name = 'doctors/list.html'
    context_object_name = 'doctors'
    paginate_by = 12

    def get_queryset(self):
        queryset = Doctor.objects.filter(
            is_available=True,
            is_verified=True
        ).select_related(
            'user__profile',
            'clinic',
            'specialization'
        ).prefetch_related('working_hours')

        # Search
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(bio__icontains=search) |
                Q(specialization__name__icontains=search)
            )

        # Filter by specialization
        specialization = self.request.GET.get('specialization', '')
        if specialization:
            queryset = queryset.filter(specialization__slug=specialization)

        # Filter by clinic
        clinic = self.request.GET.get('clinic', '')
        if clinic:
            queryset = queryset.filter(clinic__slug=clinic)

        # Price range
        min_price = self.request.GET.get('min_price', '')
        max_price = self.request.GET.get('max_price', '')
        if min_price:
            queryset = queryset.filter(consultation_fee__gte=min_price)
        if max_price:
            queryset = queryset.filter(consultation_fee__lte=max_price)

        # Min rating
        min_rating = self.request.GET.get('min_rating', '')
        if min_rating:
            queryset = queryset.filter(rating__gte=min_rating)

        # Ordering
        order = self.request.GET.get('order', '-rating')
        queryset = queryset.order_by(order)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = DoctorSearchForm(self.request.GET)
        context['specializations'] = Specialization.objects.all()
        return context

    def get_template_names(self):
        if self.request.htmx:
            return ['doctors/partials/doctor_list.html']
        return ['doctors/list.html']


class DoctorDetailView(DetailView):
    """Doctor detail page"""
    model = Doctor
    template_name = 'doctors/detail.html'
    context_object_name = 'doctor'

    def get_queryset(self):
        return Doctor.objects.select_related(
            'user__profile',
            'clinic',
            'specialization'
        ).prefetch_related('working_hours', 'days_off')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = self.object

        # Get working schedule
        context['working_hours'] = doctor.working_hours.filter(
            is_active=True
        ).order_by('day_of_week')

        # Recent reviews (if implemented)
        # context['reviews'] = doctor.reviews.all()[:5]

        # Statistics
        context['stats'] = {
            'total_patients': doctor.total_patients,
            'experience_years': doctor.experience_years,
            'rating': doctor.rating,
            'total_reviews': doctor.total_reviews,
        }

        return context


class SpecializationListView(ListView):
    """List all specializations"""
    model = Specialization
    template_name = 'doctors/specializations.html'
    context_object_name = 'specializations'

    def get_queryset(self):
        return Specialization.objects.annotate(
            doctor_count=Count('doctors')
        ).order_by('name')

    def get_template_names(self):
        if self.request.htmx:
            return ['doctors/partials/specialization_list.html']
        return ['doctors/specializations.html']


class SpecializationDetailView(DetailView):
    """Specialization detail with doctors"""
    model = Specialization
    template_name = 'doctors/specialization_detail.html'
    context_object_name = 'specialization'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['doctors'] = Doctor.objects.filter(
            specialization=self.object,
            is_available=True,
            is_verified=True
        ).select_related('user', 'clinic')
        return context


class TopRatedDoctorsView(ListView):
    """Top rated doctors (HTMX)"""
    template_name = 'doctors/partials/top_doctors.html'
    context_object_name = 'doctors'

    def get_queryset(self):
        return Doctor.objects.filter(
            is_available=True,
            is_verified=True
        ).select_related(
            'user__profile',
            'specialization',
            'clinic'
        ).order_by('-rating')[:8]


@login_required
def available_slots(request, pk):
    """Get available time slots for a doctor (HTMX)"""
    doctor = get_object_or_404(Doctor, pk=pk)
    date_str = request.GET.get('date')

    if not date_str:
        return JsonResponse({'error': 'Date is required'}, status=400)

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)

    # Use helper function
    slots = get_available_time_slots(doctor, date)

    return render(request, 'doctors/partials/available_slots.html', {
        'slots': slots,
        'doctor': doctor,
        'date': date
    })


class DoctorReviewsView(ListView):
    """Doctor reviews (HTMX)"""
    template_name = 'doctors/partials/reviews.html'
    context_object_name = 'reviews'

    def get_queryset(self):
        doctor_id = self.kwargs.get('pk')
        # Implement reviews model if needed
        return []


# ============================================
# Doctor Dashboard Views
# ============================================

class DoctorDashboardView(LoginRequiredMixin, DoctorRequiredMixin, DetailView):
    """Doctor's personal dashboard"""
    model = Doctor
    template_name = 'doctors/dashboard.html'
    context_object_name = 'doctor'

    def get_object(self):
        return get_object_or_404(Doctor, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = self.object
        today = datetime.now().date()

        # Today's appointments
        context['today_appointments'] = Appointment.objects.filter(
            doctor=doctor,
            date=today,
            status__in=['PENDING', 'CONFIRMED']
        ).select_related('patient__profile', 'service').order_by('start_time')

        # Upcoming appointments
        context['upcoming_appointments'] = Appointment.objects.filter(
            doctor=doctor,
            date__gte=today,
            status__in=['PENDING', 'CONFIRMED']
        ).select_related('patient__profile', 'service').order_by('date', 'start_time')[:10]

        # Statistics
        context['stats'] = {
            'today_count': context['today_appointments'].count(),
            'pending_count': Appointment.objects.filter(
                doctor=doctor,
                status='PENDING'
            ).count(),
            'total_patients': doctor.total_patients,
            'rating': doctor.rating,
        }

        return context


class DoctorAppointmentsView(LoginRequiredMixin, DoctorRequiredMixin, ListView):
    """Doctor's appointments list"""
    template_name = 'doctors/appointments.html'
    context_object_name = 'appointments'
    paginate_by = 20

    def get_queryset(self):
        doctor = get_object_or_404(Doctor, user=self.request.user)
        return Appointment.objects.filter(
            doctor=doctor
        ).select_related(
            'patient__profile',
            'service',
            'clinic'
        ).order_by('-date', '-start_time')


class DoctorScheduleView(LoginRequiredMixin, DoctorRequiredMixin, TemplateView):
    """Doctor's schedule view"""
    template_name = 'doctors/schedule.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = get_object_or_404(Doctor, user=self.request.user)

        context['working_hours'] = doctor.working_hours.filter(
            is_active=True
        ).order_by('day_of_week')

        context['days_off'] = doctor.days_off.filter(
            date__gte=datetime.now().date()
        ).order_by('date')

        return context


class WorkingHoursManageView(LoginRequiredMixin, DoctorRequiredMixin, TemplateView):
    """Manage working hours"""
    template_name = 'doctors/working_hours_manage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = get_object_or_404(Doctor, user=self.request.user)
        context['working_hours'] = doctor.working_hours.all().order_by('day_of_week')
        context['form'] = WorkingHourForm()
        return context

    def post(self, request, *args, **kwargs):
        doctor = get_object_or_404(Doctor, user=request.user)
        form = WorkingHourForm(request.POST)

        if form.is_valid():
            working_hour = form.save(commit=False)
            working_hour.doctor = doctor
            working_hour.save()
            messages.success(request, _('Working hours added successfully'))
            return redirect('doctors:working_hours')

        return self.get(request, *args, **kwargs)


class DaysOffManageView(LoginRequiredMixin, DoctorRequiredMixin, ListView):
    """Manage days off"""
    template_name = 'doctors/days_off_manage.html'
    context_object_name = 'days_off'

    def get_queryset(self):
        doctor = get_object_or_404(Doctor, user=self.request.user)
        return doctor.days_off.filter(
            date__gte=datetime.now().date()
        ).order_by('date')


import json

class DayOffCreateView(LoginRequiredMixin, DoctorRequiredMixin, CreateView):
    model = DayOff
    form_class = DayOffForm
    template_name = 'doctors/day_off_create.html'
    success_url = reverse_lazy('doctors:days_off')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = get_object_or_404(Doctor, user=self.request.user)
        # جلب كل التواريخ التي سجلها الطبيب كإجازة سابقاً
        existing_days = list(doctor.days_off.values_list('date', flat=True))
        # تحويلها إلى نصوص بصيغة YYYY-MM-DD لتفهمها JavaScript
        context['existing_days_json'] = json.dumps([d.strftime('%Y-%m-%d') for d in existing_days])
        return context

    def form_valid(self, form):
        form.instance.doctor = get_object_or_404(Doctor, user=self.request.user)
        messages.success(self.request, _('Day off added successfully'))
        return super().form_valid(form)


class DayOffDeleteView(LoginRequiredMixin, DoctorRequiredMixin, DeleteView):
    """Delete day off"""
    model = DayOff
    success_url = reverse_lazy('doctors:days_off')

    def get_queryset(self):
        doctor = get_object_or_404(Doctor, user=self.request.user)
        return DayOff.objects.filter(doctor=doctor)

    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Day off deleted successfully'))
        return super().delete(request, *args, **kwargs)


class WorkingHourDeleteView(LoginRequiredMixin, DoctorRequiredMixin, DeleteView):
    model = WorkingHour
    success_url = reverse_lazy('doctors:working_hours')

    def get_queryset(self):
        doctor = get_object_or_404(Doctor, user=self.request.user)
        return WorkingHour.objects.filter(doctor=doctor)

    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Working hours deleted successfully'))
        return super().delete(request, *args, **kwargs)
