from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Admin interface for Appointments"""
    
    list_display = [
        'id',
        'patient_name',
        'doctor_name',
        'clinic_name',
        'date',
        'start_time',
        'status_badge',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'date',
        'created_at',
        'doctor__specialization',
        'clinic'
    ]
    
    search_fields = [
        'patient__first_name',
        'patient__last_name',
        'patient__email',
        'doctor__user__first_name',
        'doctor__user__last_name',
        'clinic__name',
        'symptoms'
    ]
    
    date_hierarchy = 'date'
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'confirmed_at',
        'canceled_at'
    ]
    
    fieldsets = (
        (_('Appointment Information'), {
            'fields': (
                'patient',
                'doctor',
                'clinic',
                'service',
                'status'
            )
        }),
        (_('Schedule'), {
            'fields': (
                'date',
                'start_time',
                'end_time'
            )
        }),
        (_('Details'), {
            'fields': (
                'symptoms',
                'notes'
            )
        }),
        (_('Cancellation'), {
            'fields': (
                'cancellation_reason',
                'canceled_at'
            ),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': (
                'created_at',
                'updated_at',
                'confirmed_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    list_per_page = 25
    
    actions = [
        'confirm_appointments',
        'cancel_appointments',
        'complete_appointments'
    ]

    def patient_name(self, obj):
        """Display patient name"""
        return obj.patient.get_full_name()
    patient_name.short_description = _('Patient')
    patient_name.admin_order_field = 'patient__first_name'

    def doctor_name(self, obj):
        """Display doctor name"""
        return f"Dr. {obj.doctor.user.get_full_name()}"
    doctor_name.short_description = _('Doctor')
    doctor_name.admin_order_field = 'doctor__user__first_name'

    def clinic_name(self, obj):
        """Display clinic name"""
        return obj.clinic.name
    clinic_name.short_description = _('Clinic')
    clinic_name.admin_order_field = 'clinic__name'

    def status_badge(self, obj):
        """Display colored status badge"""
        colors = {
            'PENDING': 'orange',
            'CONFIRMED': 'green',
            'CANCELED': 'red',
            'COMPLETED': 'blue',
            'NO_SHOW': 'gray'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = _('Status')
    status_badge.admin_order_field = 'status'

    def confirm_appointments(self, request, queryset):
        """Bulk confirm appointments"""
        from django.utils import timezone
        updated = queryset.filter(
            status=Appointment.Status.PENDING
        ).update(
            status=Appointment.Status.CONFIRMED,
            confirmed_at=timezone.now()
        )
        self.message_user(
            request,
            _('%(count)d appointment(s) confirmed successfully') % {'count': updated}
        )
    confirm_appointments.short_description = _('Confirm selected appointments')

    def cancel_appointments(self, request, queryset):
        """Bulk cancel appointments"""
        from django.utils import timezone
        updated = queryset.filter(
            status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
        ).update(
            status=Appointment.Status.CANCELED,
            canceled_at=timezone.now()
        )
        self.message_user(
            request,
            _('%(count)d appointment(s) canceled successfully') % {'count': updated}
        )
    cancel_appointments.short_description = _('Cancel selected appointments')

    def complete_appointments(self, request, queryset):
        """Bulk complete appointments"""
        updated = queryset.filter(
            status=Appointment.Status.CONFIRMED
        ).update(
            status=Appointment.Status.COMPLETED
        )
        self.message_user(
            request,
            _('%(count)d appointment(s) marked as completed') % {'count': updated}
        )
    complete_appointments.short_description = _('Mark selected as completed')

    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related(
            'patient',
            'doctor__user',
            'doctor__specialization',
            'clinic',
            'service'
        )
