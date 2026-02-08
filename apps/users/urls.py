from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Profile
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('profile/avatar/', views.AvatarUpdateView.as_view(), name='avatar_update'),

    # Settings
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('settings/password/', views.PasswordChangeView.as_view(), name='password_change'),
    path('settings/notifications/', views.NotificationSettingsView.as_view(), name='notification_settings'),
]