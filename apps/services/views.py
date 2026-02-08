from django.views.generic import ListView, DetailView
from .models import Service


class ServiceListView(ListView):
    """List all services"""
    model = Service
    template_name = 'services/list.html'
    context_object_name = 'services'
    paginate_by = 20

    def get_queryset(self):
        return Service.objects.filter(is_active=True).select_related('clinic')


class ServiceDetailView(DetailView):
    """Service detail"""
    model = Service
    template_name = 'services/detail.html'
    context_object_name = 'service'


class ClinicServicesView(ListView):
    """Services by clinic"""
    template_name = 'services/clinic_services.html'
    context_object_name = 'services'

    def get_queryset(self):
        clinic_id = self.kwargs.get('clinic_id')
        return Service.objects.filter(
            clinic_id=clinic_id,
            is_active=True
        )
