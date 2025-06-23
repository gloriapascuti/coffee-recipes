from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    UserDetailView,
    ProfileView,
    setup_2fa,
    verify_2fa_setup,
    login_view,
    verify_2fa_login,
    disable_2fa,
    get_2fa_status,
    LoginView,
    admin_users_list,
    verify_user_activity,
    ban_user,
    get_user_notification_status
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', login_view, name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserDetailView.as_view(), name='user-detail'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('setup-2fa/', setup_2fa, name='setup-2fa'),
    path('verify-2fa-setup/', verify_2fa_setup, name='verify-2fa-setup'),
    path('verify-2fa-login/', verify_2fa_login, name='verify-2fa-login'),
    path('disable-2fa/', disable_2fa, name='disable-2fa'),
    path('2fa-status/', get_2fa_status, name='2fa-status'),
    path('login/', LoginView.as_view(), name='login'),
    path('admin/users/', admin_users_list, name='admin-users-list'),
    path('admin/verify-user/<int:user_id>/', verify_user_activity, name='verify-user-activity'),
    path('admin/ban-user/<int:user_id>/', ban_user, name='ban-user'),
    path('notification-status/', get_user_notification_status, name='user-notification-status'),
] 