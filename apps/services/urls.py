from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # List & Detail
    path('', views.ServiceListView.as_view(), name='list'),
    path('<int:pk>/', views.ServiceDetailView.as_view(), name='detail'),
    path('clinic/<int:clinic_id>/', views.ClinicServicesView.as_view(), name='by_clinic'),
]
