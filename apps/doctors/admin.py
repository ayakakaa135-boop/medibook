from django.contrib import admin
from .models import Specialization, Doctor, WorkingHour, DayOff
from django.utils.translation import gettext_lazy as _

@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    """Specialization Admin"""

    list_display = ['name', 'slug', 'icon', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']


class WorkingHourInline(admin.TabularInline):
    """Inline for Working Hours"""
    model = WorkingHour
    extra = 1
    fields = ['day_of_week', 'start_time', 'end_time', 'is_active']


class DayOffInline(admin.TabularInline):
    """Inline for Days Off"""
    model = DayOff
    extra = 0
    fields = ['date', 'reason', 'is_recurring']


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    """Doctor Admin"""

    list_display = ['get_full_name', 'specialization', 'clinic', 'rating', 'is_verified', 'is_available']
    list_filter = ['specialization', 'clinic', 'is_verified', 'is_available', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'license_number']
    readonly_fields = ['created_at', 'updated_at', 'rating', 'total_reviews', 'total_patients']
    list_editable = ['is_verified', 'is_available']
    inlines = [WorkingHourInline, DayOffInline]

    fieldsets = (
        (_('User & Clinic'), {
            'fields': ('user', 'clinic', 'specialization')
        }),
        (_('Professional Info'), {
            'fields': ('license_number', 'experience_years', 'education', 'bio')
        }),
        (_('Consultation'), {
            'fields': ('consultation_fee',)
        }),
        (_('Statistics'), {
            'fields': ('total_patients', 'rating', 'total_reviews')
        }),
        (_('Status'), {
            'fields': ('is_available', 'is_verified')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    get_full_name.short_description = _('Doctor Name')


@admin.register(WorkingHour)
class WorkingHourAdmin(admin.ModelAdmin):
    """Working Hours Admin"""

    list_display = ['doctor', 'get_day_display', 'start_time', 'end_time', 'is_active']
    list_filter = ['day_of_week', 'is_active']
    search_fields = ['doctor__user__first_name', 'doctor__user__last_name']
    list_editable = ['is_active']

    def get_day_display(self, obj):
        return obj.get_day_of_week_display()

    get_day_display.short_description = _('Day')


@admin.register(DayOff)
class DayOffAdmin(admin.ModelAdmin):
    """Days Off Admin"""

    list_display = ['doctor', 'date', 'reason', 'is_recurring', 'created_at']
    list_filter = ['is_recurring', 'date']
    search_fields = ['doctor__user__first_name', 'doctor__user__last_name', 'reason']
    date_hierarchy = 'date'

