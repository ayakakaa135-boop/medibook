"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import TemplateView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Health check
    path('health/', TemplateView.as_view(template_name='health.html'), name='health'),
    path('i18n/', include('django.conf.urls.i18n')),
]

# i18n patterns - مع دعم اللغات
urlpatterns += i18n_patterns(
    # Authentication (django-allauth)
    path('accounts/', include('allauth.urls')),

    # Home
    path('', include('apps.core.urls')),  # Home page

    # Apps
    path('users/', include('apps.users.urls')),
    path('clinics/', include('apps.clinics.urls')),
    path('doctors/', include('apps.doctors.urls')),
    path('services/', include('apps.services.urls')),
    path('appointments/', include('apps.appointments.urls')),
    path('dashboard/', include('apps.dashboard.urls')),

    prefix_default_language=True,
)

# Static and Media files (development only)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
                          path('__debug__/', include(debug_toolbar.urls)),
                      ] + urlpatterns

# Custom error handlers
handler404 = 'apps.core.views.error_404'
handler500 = 'apps.core.views.error_500'
handler403 = 'apps.core.views.error_403'
handler400 = 'apps.core.views.error_400'

