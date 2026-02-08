from django.views.generic import TemplateView
from django.shortcuts import render
from django.db.models import Q
from apps.doctors.models import Doctor, Specialization
from apps.clinics.models import Clinic


class HomeView(TemplateView):
    """Home page"""
    template_name = 'home.html'


class SearchView(TemplateView):
    """Global search"""
    template_name = 'partials/search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')

        if query:
            # Search doctors
            context['doctors'] = Doctor.objects.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(bio__icontains=query) |
                Q(specialization__name__icontains=query),
                is_available=True,
                is_verified=True
            ).select_related('user', 'specialization', 'clinic')[:5]

            # Search clinics
            context['clinics'] = Clinic.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(city__icontains=query),
                is_active=True
            )[:5]

            # Search specializations
            context['specializations'] = Specialization.objects.filter(
                name__icontains=query
            )[:5]

        return context


class AboutView(TemplateView):
    """About page"""
    template_name = 'about.html'


class ContactView(TemplateView):
    """Contact page"""
    template_name = 'contact.html'


# Error handlers
def error_404(request, exception):
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    return render(request, 'errors/500.html', status=500)


def error_403(request, exception):
    return render(request, 'errors/403.html', status=403)


def error_400(request, exception):
    return render(request, 'errors/400.html', status=400)