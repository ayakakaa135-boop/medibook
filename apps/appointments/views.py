from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from datetime import datetime, timedelta
import json

from .models import Appointment
from .forms import AppointmentCreateForm, AppointmentCancelForm, AppointmentFilterForm
from apps.doctors.models import Doctor, WorkingHour, DayOff

try:
    from django_htmx.http import HttpResponseClientRefresh
except ImportError:
    # Fallback if django-htmx not installed
    from django.http import HttpResponseRedirect
    def HttpResponseClientRefresh():
        return HttpResponseRedirect('/')


class MyAppointmentsView(LoginRequiredMixin, ListView):
    """User's appointments"""
    template_name = 'appointments/my_appointments.html'
    context_object_name = 'appointments'
    paginate_by = 10

    def get_queryset(self):
        queryset = Appointment.objects.filter(
            patient=self.request.user
        ).select_related(
            'doctor__user__profile',
            'doctor__specialization',
            'clinic',
            'service'
        ).order_by('-date', '-start_time')

        # Apply filters
        form = AppointmentFilterForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data.get('status'):
                queryset = queryset.filter(status=form.cleaned_data['status'])
            if form.cleaned_data.get('date_from'):
                queryset = queryset.filter(date__gte=form.cleaned_data['date_from'])
            if form.cleaned_data.get('date_to'):
                queryset = queryset.filter(date__lte=form.cleaned_data['date_to'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        today = timezone.now().date()

        # Upcoming appointments
        context['upcoming'] = queryset.filter(
            date__gte=today,
            status__in=['PENDING', 'CONFIRMED']
        )[:5]

        # Past appointments
        context['past'] = queryset.filter(
            Q(date__lt=today) |
            Q(status__in=['COMPLETED', 'CANCELED', 'NO_SHOW'])
        )[:5]

        # Filter form
        context['filter_form'] = AppointmentFilterForm(self.request.GET)

        return context


class UpcomingAppointmentsView(LoginRequiredMixin, ListView):
    """Upcoming appointments only"""
    template_name = 'appointments/upcoming.html'
    context_object_name = 'appointments'
    paginate_by = 20

    def get_queryset(self):
        today = timezone.now().date()
        return Appointment.objects.filter(
            patient=self.request.user,
            date__gte=today,
            status__in=['PENDING', 'CONFIRMED']
        ).select_related(
            'doctor__user__profile',
            'doctor__specialization',
            'clinic',
            'service'
        ).order_by('date', 'start_time')


class PastAppointmentsView(LoginRequiredMixin, ListView):
    """Past appointments"""
    template_name = 'appointments/past.html'
    context_object_name = 'appointments'
    paginate_by = 20

    def get_queryset(self):
        today = timezone.now().date()
        return Appointment.objects.filter(
            patient=self.request.user
        ).filter(
            Q(date__lt=today) |
            Q(status__in=['COMPLETED', 'CANCELED', 'NO_SHOW'])
        ).select_related(
            'doctor__user__profile',
            'doctor__specialization',
            'clinic',
            'service'
        ).order_by('-date', '-start_time')


class AppointmentCreateView(LoginRequiredMixin, CreateView):
    """Create appointment"""
    model = Appointment
    form_class = AppointmentCreateForm
    template_name = 'appointments/create.html'
    success_url = reverse_lazy('appointments:my_appointments')

    def dispatch(self, request, *args, **kwargs):
        """Check if user is a patient"""
        if not hasattr(request.user, 'role') or request.user.role != 'PATIENT':
            messages.error(request, _('Only patients can book appointments'))
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Pass user and doctor to form"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        
        # Get doctor from URL parameter
        doctor_id = self.request.GET.get('doctor')
        if doctor_id:
            try:
                kwargs['doctor'] = Doctor.objects.get(pk=doctor_id)
            except Doctor.DoesNotExist:
                pass
        
        return kwargs

    def form_valid(self, form):
        """Save appointment"""
        form.instance.patient = self.request.user
        form.instance.clinic = form.cleaned_data['doctor'].clinic

        # Set status
        form.instance.status = Appointment.Status.PENDING

        messages.success(
            self.request,
            _('Appointment booked successfully! You will receive a confirmation soon.')
        )

        # Handle HTMX request
        if hasattr(self.request, 'htmx') and self.request.htmx:
            response = super().form_valid(form)
            return HttpResponseClientRefresh()

        return super().form_valid(form)

    def form_invalid(self, form):
        """Handle invalid form"""
        messages.error(
            self.request,
            _('There was an error booking your appointment. Please check the form.')
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get doctor from URL parameter
        doctor_id = self.request.GET.get('doctor')
        if doctor_id:
            try:
                doctor = Doctor.objects.select_related(
                    'user__profile',
                    'specialization',
                    'clinic'
                ).get(pk=doctor_id)
                context['doctor'] = doctor

                # Get disabled dates (days off)
                disabled_dates = list(
                    DayOff.objects.filter(doctor=doctor)
                    .values_list('date', flat=True)
                )
                context['disabled_dates_json'] = json.dumps(
                    [d.strftime('%Y-%m-%d') for d in disabled_dates]
                )

                # Get available time slots for today (example)
                context['available_slots'] = get_available_time_slots(
                    doctor,
                    timezone.now().date()
                )

            except Doctor.DoesNotExist:
                messages.warning(self.request, _('Doctor not found'))

        context['today'] = timezone.now().date()
        
        return context


class AppointmentDetailView(LoginRequiredMixin, DetailView):
    """Appointment detail"""
    model = Appointment
    template_name = 'appointments/detail.html'
    context_object_name = 'appointment'

    def get_queryset(self):
        """Filter by patient"""
        return Appointment.objects.filter(
            patient=self.request.user
        ).select_related(
            'doctor__user__profile',
            'doctor__specialization',
            'clinic',
            'service'
        )


@login_required
def cancel_appointment(request, pk):
    """Cancel appointment"""
    appointment = get_object_or_404(
        Appointment,
        pk=pk,
        patient=request.user
    )

    if not appointment.can_cancel:
        messages.error(request, _('This appointment cannot be canceled'))
        if hasattr(request, 'htmx') and request.htmx:
            return HttpResponseClientRefresh()
        return redirect('appointments:detail', pk=pk)

    if request.method == 'POST':
        form = AppointmentCancelForm(request.POST)
        if form.is_valid():
            appointment.status = Appointment.Status.CANCELED
            appointment.canceled_at = timezone.now()
            appointment.cancellation_reason = form.cleaned_data.get('reason', '')
            appointment.save()

            messages.success(request, _('Appointment canceled successfully'))

            if hasattr(request, 'htmx') and request.htmx:
                return HttpResponseClientRefresh()
            return redirect('appointments:my_appointments')
    else:
        form = AppointmentCancelForm()

    return render(request, 'appointments/partials/cancel_modal.html', {
        'appointment': appointment,
        'form': form
    })


@login_required
def confirm_appointment(request, pk):
    """Confirm appointment (Doctor only)"""
    appointment = get_object_or_404(Appointment, pk=pk)

    # Check if user is the doctor
    if not hasattr(request.user, 'doctor_profile') or appointment.doctor != request.user.doctor_profile:
        messages.error(request, _('Unauthorized'))
        return redirect('dashboard:index')

    if not appointment.can_confirm:
        messages.error(request, _('This appointment cannot be confirmed'))
        return redirect('doctors:dashboard')

    if request.method == 'POST':
        appointment.status = Appointment.Status.CONFIRMED
        appointment.confirmed_at = timezone.now()
        appointment.save()

        messages.success(request, _('Appointment confirmed successfully'))

        if hasattr(request, 'htmx') and request.htmx:
            return HttpResponseClientRefresh()
        return redirect('doctors:dashboard')

    return render(request, 'appointments/partials/confirm_modal.html', {
        'appointment': appointment
    })


@login_required
def complete_appointment(request, pk):
    """Mark appointment as completed (Doctor only)"""
    appointment = get_object_or_404(Appointment, pk=pk)

    # Check if user is the doctor
    if not hasattr(request.user, 'doctor_profile') or appointment.doctor != request.user.doctor_profile:
        messages.error(request, _('Unauthorized'))
        return redirect('dashboard:index')

    if not appointment.can_complete:
        messages.error(request, _('This appointment cannot be completed'))
        return redirect('doctors:dashboard')

    if request.method == 'POST':
        appointment.status = Appointment.Status.COMPLETED
        appointment.save()

        messages.success(request, _('Appointment marked as completed'))

        if hasattr(request, 'htmx') and request.htmx:
            return HttpResponseClientRefresh()
        return redirect('doctors:dashboard')

    return render(request, 'appointments/partials/complete_modal.html', {
        'appointment': appointment
    })


@login_required
def check_availability(request):
    """Check appointment availability (HTMX/AJAX)"""
    doctor_id = request.GET.get('doctor')
    date_str = request.GET.get('date')
    time_str = request.GET.get('time')

    if not all([doctor_id, date_str, time_str]):
        return JsonResponse({
            'available': False,
            'message': _('Missing parameters')
        })

    try:
        doctor = Doctor.objects.get(pk=doctor_id)
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        time = datetime.strptime(time_str, '%H:%M').time()

        # Check if date is in the past
        if date < timezone.now().date():
            return JsonResponse({
                'available': False,
                'message': _('Cannot book appointments in the past')
            })

        # Check working hours
        day_of_week = date.weekday()
        working_hours = WorkingHour.objects.filter(
            doctor=doctor,
            day_of_week=day_of_week,
            is_active=True
        )

        if not working_hours.exists():
            return JsonResponse({
                'available': False,
                'message': _('Doctor is not available on this day')
            })

        # Check if time is within working hours
        is_valid_time = any(
            wh.start_time <= time < wh.end_time
            for wh in working_hours
        )

        if not is_valid_time:
            return JsonResponse({
                'available': False,
                'message': _('Selected time is outside working hours')
            })

        # Check day off
        if DayOff.objects.filter(doctor=doctor, date=date).exists():
            return JsonResponse({
                'available': False,
                'message': _('Doctor is not available on this date')
            })

        # Check conflicts
        conflicts = Appointment.objects.filter(
            doctor=doctor,
            date=date,
            start_time=time,
            status__in=['PENDING', 'CONFIRMED']
        )

        if conflicts.exists():
            return JsonResponse({
                'available': False,
                'message': _('This time slot is already booked')
            })

        return JsonResponse({
            'available': True,
            'message': _('This time slot is available')
        })

    except Doctor.DoesNotExist:
        return JsonResponse({
            'available': False,
            'message': _('Doctor not found')
        })
    except ValueError as e:
        return JsonResponse({
            'available': False,
            'message': _('Invalid date or time format')
        })
    except Exception as e:
        return JsonResponse({
            'available': False,
            'message': str(e)
        })


def get_available_time_slots(doctor, date):
    """
    Get available time slots for a doctor on a specific date
    
    Args:
        doctor: Doctor instance
        date: Date object
    
    Returns:
        List of available time slots (strings in HH:MM format)
    """
    # Get working hours for the day
    day_of_week = date.weekday()
    working_hours = WorkingHour.objects.filter(
        doctor=doctor,
        day_of_week=day_of_week,
        is_active=True
    )

    if not working_hours.exists():
        return []

    # Check if it's a day off
    if DayOff.objects.filter(doctor=doctor, date=date).exists():
        return []

    # Get all booked slots for this day
    booked_slots = Appointment.objects.filter(
        doctor=doctor,
        date=date,
        status__in=['PENDING', 'CONFIRMED']
    ).values_list('start_time', flat=True)

    # Generate available slots
    available_slots = []
    slot_duration = 30  # minutes

    for wh in working_hours:
        current_time = datetime.combine(date, wh.start_time)
        end_time = datetime.combine(date, wh.end_time)

        while current_time < end_time:
            slot_time = current_time.time()
            
            # Check if slot is not booked
            if slot_time not in booked_slots:
                # Check if slot is not in the past (for today)
                if date == timezone.now().date():
                    if slot_time > timezone.now().time():
                        available_slots.append(slot_time.strftime('%H:%M'))
                else:
                    available_slots.append(slot_time.strftime('%H:%M'))
            
            current_time += timedelta(minutes=slot_duration)

    return available_slots


@login_required
def get_available_slots_ajax(request):
    """Get available slots via AJAX/HTMX"""
    doctor_id = request.GET.get('doctor')
    date_str = request.GET.get('date')

    if not doctor_id or not date_str:
        return HttpResponse(
            '<option value="">%s</option>' % _('Please select a date'),
            content_type='text/html'
        )

    try:
        doctor = Doctor.objects.get(pk=doctor_id)
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        slots = get_available_time_slots(doctor, date)

        if not slots:
            return HttpResponse(
                '<option value="">%s</option>' % _('No available slots'),
                content_type='text/html'
            )

        # Build HTML options
        html = '<option value="">%s</option>' % _('Select time')
        for slot in slots:
            html += f'<option value="{slot}">{slot}</option>'

        return HttpResponse(html, content_type='text/html')

    except Doctor.DoesNotExist:
        return HttpResponse(
            '<option value="">%s</option>' % _('Doctor not found'),
            content_type='text/html'
        )
    except ValueError:
        return HttpResponse(
            '<option value="">%s</option>' % _('Invalid date format'),
            content_type='text/html'
        )
