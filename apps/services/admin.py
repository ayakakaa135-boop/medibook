from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Service
from django.utils.translation import gettext_lazy as _


@admin.register(Service)
class ServiceAdmin(TranslationAdmin):
    """Service Admin"""

    list_display = ['name', 'clinic', 'duration_minutes', 'price', 'is_active', 'created_at']
    list_filter = ['is_active', 'clinic', 'duration_minutes']
    search_fields = ['name', 'clinic__name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active', 'price']

    fieldsets = (
        (_('Basic Info'), {
            'fields': ('clinic', 'name', 'slug', 'description')
        }),
        (_('Details'), {
            'fields': ('duration_minutes', 'price')
        }),
        (_('Requirements'), {
            'fields': ('requires_fasting', 'preparation_instructions')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
