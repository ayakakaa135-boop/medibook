from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Main Dashboard (redirects based on role)
    path('', views.DashboardRedirectView.as_view(), name='index'),

    # Patient Dashboard
    path('patient/', views.PatientDashboardView.as_view(), name='patient'),

    # Doctor Dashboard
    path('doctor/', views.DoctorDashboardView.as_view(), name='doctor'),
    path('doctor/analytics/', views.DoctorAnalyticsView.as_view(), name='doctor_analytics'),
    path('doctor/patients/', views.DoctorPatientsView.as_view(), name='doctor_patients'),

    # Admin Dashboard
    path('admin/', views.AdminDashboardView.as_view(), name='admin'),
    path('admin/statistics/', views.AdminStatisticsView.as_view(), name='admin_statistics'),
    path('admin/reports/', views.AdminReportsView.as_view(), name='admin_reports'),
    path('admin/analytics/', views.AdminAnalyticsView.as_view(), name='admin_analytics'),

    # HTMX endpoints for charts
    path('admin/chart/appointments/', views.appointments_chart_data, name='appointments_chart'),
    path('admin/chart/revenue/', views.revenue_chart_data, name='revenue_chart'),
]