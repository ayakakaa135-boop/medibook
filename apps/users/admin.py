from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Profile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin"""

    list_display = ['email', 'get_full_name', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'role')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.email

    get_full_name.short_description = _('Full Name')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Profile Admin"""

    list_display = ['user', 'phone', 'city', 'language', 'created_at']
    list_filter = ['language', 'country', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'phone']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (_('User'), {'fields': ('user',)}),
        (_('Contact Info'), {'fields': ('phone', 'address', 'city', 'country')}),
        (_('Personal Info'), {'fields': ('avatar', 'date_of_birth', 'bio')}),
        (_('Preferences'), {'fields': ('language', 'timezone', 'email_notifications', 'sms_notifications')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )
