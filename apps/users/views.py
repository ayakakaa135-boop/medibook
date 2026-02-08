from django.shortcuts import render, redirect
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from .models import User, Profile
from .forms import ProfileUpdateForm, UserUpdateForm


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view"""
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['profile'] = self.request.user.profile
        return context


class ProfileEditView(LoginRequiredMixin, TemplateView):
    """Edit user profile"""
    template_name = 'users/profile_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_form'] = UserUpdateForm(instance=self.request.user)
        context['profile_form'] = ProfileUpdateForm(instance=self.request.user.profile)
        return context

    def post(self, request, *args, **kwargs):
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _('Profile updated successfully'))
            return redirect('users:profile')

        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form
        })


class AvatarUpdateView(LoginRequiredMixin, TemplateView):
    """Update user avatar via HTMX"""
    template_name = 'users/partials/avatar_update.html'

    def post(self, request, *args, **kwargs):
        if 'avatar' in request.FILES:
            profile = request.user.profile
            profile.avatar = request.FILES['avatar']
            profile.save()
            messages.success(request, _('Avatar updated successfully'))

        return render(request, self.template_name, {
            'profile': request.user.profile
        })


class SettingsView(LoginRequiredMixin, TemplateView):
    """User settings"""
    template_name = 'users/settings.html'


class PasswordChangeView(LoginRequiredMixin, TemplateView):
    """Change password"""
    template_name = 'users/password_change.html'


class NotificationSettingsView(LoginRequiredMixin, TemplateView):
    """Notification settings"""
    template_name = 'users/notification_settings.html'

    def post(self, request, *args, **kwargs):
        profile = request.user.profile
        profile.email_notifications = request.POST.get('email_notifications') == 'on'
        profile.sms_notifications = request.POST.get('sms_notifications') == 'on'
        profile.save()

        messages.success(request, _('Notification settings updated'))
        return redirect('users:notification_settings')
