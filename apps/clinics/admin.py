from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Clinic


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    """Clinic Admin"""

    list_display = ['name', 'city', 'phone', 'rating', 'is_active', 'created_at']
    list_filter = ['is_active', 'city', 'created_at']
    search_fields = ['name', 'city', 'email', 'phone']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'rating', 'total_reviews']
    list_editable = ['is_active']

    fieldsets = (
        (_('Basic Info'), {
            'fields': ('name', 'slug', 'description')
        }),
        (_('Contact'), {
            'fields': ('address', 'city', 'phone', 'email', 'website')
        }),
        (_('Media'), {
            'fields': ('logo', 'cover_image')
        }),
        (_('Operating Hours'), {
            'fields': ('opening_time', 'closing_time')
        }),
        (_('Status & Rating'), {
            'fields': ('is_active', 'rating', 'total_reviews')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
