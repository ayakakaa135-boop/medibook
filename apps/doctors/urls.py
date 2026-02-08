from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    # List & Detail
    path('', views.DoctorListView.as_view(), name='list'),
    path('<int:pk>/', views.DoctorDetailView.as_view(), name='detail'),

    # Specializations
    path('specializations/', views.SpecializationListView.as_view(), name='specialization_list'),

    path('specializations/<slug:slug>/', views.SpecializationDetailView.as_view(), name='specialization_detail'),

    # HTMX endpoints

    path('top-rated/', views.TopRatedDoctorsView.as_view(), name='top_rated'),
    path('<int:pk>/available-slots/', views.available_slots, name='available_slots'),
    path('<int:pk>/reviews/', views.DoctorReviewsView.as_view(), name='reviews'),

    # Doctor Dashboard
    path('dashboard/', views.DoctorDashboardView.as_view(), name='dashboard'),
    path('dashboard/appointments/', views.DoctorAppointmentsView.as_view(), name='dashboard_appointments'),
    path('dashboard/schedule/', views.DoctorScheduleView.as_view(), name='dashboard_schedule'),
    path('dashboard/working-hours/', views.WorkingHoursManageView.as_view(), name='working_hours'),
    path('dashboard/days-off/', views.DaysOffManageView.as_view(), name='days_off'),
    path('dashboard/days-off/create/', views.DayOffCreateView.as_view(), name='day_off_create'),
    path('dashboard/days-off/<int:pk>/delete/', views.DayOffDeleteView.as_view(), name='days_off_delete'),
   path(
    'dashboard/working-hours/<int:pk>/delete/',
    views.WorkingHourDeleteView.as_view(),
    name='working_hours_delete'
),
# doctors/urls.py
path('dashboard/days-off/<int:pk>/delete/', views.DayOffDeleteView.as_view(), name='day_off_delete'),


]

