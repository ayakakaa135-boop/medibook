from django.urls import path
from . import views

app_name = 'clinics'

urlpatterns = [
    # List & Detail
    path('', views.ClinicListView.as_view(), name='list'),
    path('<slug:slug>/', views.ClinicDetailView.as_view(), name='detail'),

    # HTMX endpoints
    path('<int:pk>/doctors/', views.ClinicDoctorsView.as_view(), name='doctors'),
    path('<int:pk>/services/', views.ClinicServicesView.as_view(), name='services'),
]

