from django.urls import path
from . import views

from .payment_views import (
    AppointmentPaymentView,
    PaymentSuccessView,
    PaymentHistoryView,
    pay_with_saved_card,
    check_payment_status,
    cancel_appointment_with_fee,
    manage_payment_cards,
    delete_payment_card,
    set_default_card
)

app_name = 'appointments'

urlpatterns = [
    # Payment URLs
    path('<int:appointment_id>/payment/',
         AppointmentPaymentView.as_view(),
         name='payment'),

    path('<int:appointment_id>/pay-with-card/<int:card_id>/',
         pay_with_saved_card,
         name='pay_with_saved_card'),

    path('payment/<int:payment_id>/success/',
         PaymentSuccessView.as_view(),
         name='payment_success'),

    path('payment-history/',
         PaymentHistoryView.as_view(),
         name='payment_history'),

    path('<int:appointment_id>/payment-status/',
         check_payment_status,
         name='check_payment_status'),

    # Cancel with fee
    path('<int:pk>/cancel-with-fee/',
         cancel_appointment_with_fee,
         name='cancel_with_fee'),

    # Card Management
    path('cards/',
         manage_payment_cards,
         name='manage_cards'),

    path('cards/<int:card_id>/delete/',
         delete_payment_card,
         name='delete_card'),

    path('cards/<int:card_id>/set-default/',
         set_default_card,
         name='set_default_card'),
    # List Views
    path('', views.MyAppointmentsView.as_view(), name='my_appointments'),
    path('upcoming/', views.UpcomingAppointmentsView.as_view(), name='upcoming'),
    path('past/', views.PastAppointmentsView.as_view(), name='past'),

    # Create & Detail
    path('create/', views.AppointmentCreateView.as_view(), name='create'),
    path('<int:pk>/', views.AppointmentDetailView.as_view(), name='detail'),

    # Actions
    path('<int:pk>/cancel/', views.cancel_appointment, name='cancel'),
    path('<int:pk>/confirm/', views.confirm_appointment, name='confirm'),
    path('<int:pk>/complete/', views.complete_appointment, name='complete'),

    # AJAX/HTMX endpoints
    path('check-availability/', views.check_availability, name='check_availability'),
    path('get-slots/', views.get_available_slots_ajax, name='get_slots'),
]
