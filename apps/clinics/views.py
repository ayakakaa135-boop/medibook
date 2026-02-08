from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q, Avg, Count
from .models import Clinic
from apps.doctors.models import Doctor
from apps.services.models import Service


class ClinicListView(ListView):
    """List all clinics"""
    model = Clinic
    template_name = 'clinics/list.html'
    context_object_name = 'clinics'
    paginate_by = 12

    def get_queryset(self):
        queryset = Clinic.objects.filter(is_active=True).annotate(
            doctor_count=Count('doctors'),
            avg_rating=Avg('doctors__rating')
        )

        # Search
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(city__icontains=search)
            )

        # Filter by city
        city = self.request.GET.get('city', '')
        if city:
            queryset = queryset.filter(city=city)

        # Ordering
        order = self.request.GET.get('order', '-rating')
        queryset = queryset.order_by(order)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cities'] = Clinic.objects.filter(
            is_active=True
        ).values_list('city', flat=True).distinct()
        return context

    def get_template_names(self):
        if self.request.htmx:
            return ['clinics/partials/clinic_list.html']
        return ['clinics/list.html']


class ClinicDetailView(DetailView):
    """Clinic detail page"""
    model = Clinic
    template_name = 'clinics/detail.html'
    context_object_name = 'clinic'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Clinic.objects.filter(is_active=True).prefetch_related(
            'doctors__user__profile',
            'doctors__specialization',
            'services'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clinic = self.object

        # Get doctors
        context['doctors'] = clinic.doctors.filter(
            is_available=True,
            is_verified=True
        ).select_related('user', 'specialization')

        # Get services
        context['services'] = clinic.services.filter(is_active=True)

        # Statistics
        context['stats'] = {
            'total_doctors': clinic.doctors.filter(is_verified=True).count(),
            'total_services': clinic.services.filter(is_active=True).count(),
            'avg_rating': clinic.doctors.aggregate(
                avg=Avg('rating')
            )['avg'] or 0,
        }

        return context


class ClinicDoctorsView(ListView):
    """Clinic doctors list (HTMX)"""
    template_name = 'clinics/partials/doctors.html'
    context_object_name = 'doctors'

    def get_queryset(self):
        clinic_id = self.kwargs.get('pk')
        return Doctor.objects.filter(
            clinic_id=clinic_id,
            is_available=True,
            is_verified=True
        ).select_related('user', 'specialization')


class ClinicServicesView(ListView):
    """Clinic services list (HTMX)"""
    template_name = 'clinics/partials/services.html'
    context_object_name = 'services'

    def get_queryset(self):
        clinic_id = self.kwargs.get('pk')
        return Service.objects.filter(
            clinic_id=clinic_id,
            is_active=True
        )

