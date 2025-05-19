# from django.urls import path
# from .views import (
#     healthcheck,
#     RegisterView, LoginView,
#     CoffeeViewSets, OriginViewSet, FileUploadView,
#     UserList,
# )
#
# urlpatterns = [
#     # auth
#     path('auth/register/', RegisterView.as_view(), name='auth_register'),
#     path('auth/login/',    LoginView.as_view(),    name='auth_login'),
#
#     # coffee CRUD
#     path('coffee/',        CoffeeViewSets.as_view(),    name='coffee_list'),
#     path('coffee/<int:pk>/', CoffeeViewSets.as_view(),  name='coffee_detail'),
#
#     # origins
#     path('origins/',       OriginViewSet.as_view(),     name='origin_list'),
#
#     # file uploads
#     path('upload/',        FileUploadView.as_view(),    name='file_upload'),
#
#     # admin-only user list
#     path('users/',         UserList.as_view(),          name='user_list'),
# ]

# coffee/urls.py
# coffee/urls.py

from django.urls import path
from .views import (
    healthcheck,
    RegisterView,
    LoginView,
    CoffeeViewSet,
    OriginView,
    FileUploadView,
    UserList,
    OperationList,
    debug_users_and_operations,
    debug_all_operations,
    log_operation,
)

urlpatterns = [
    # Health check
    path('healthcheck/', healthcheck, name='healthcheck'),

    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/',    LoginView.as_view(),    name='login'),

    # Coffee CRUD
    path('coffee/',          CoffeeViewSet.as_view(), name='coffee-list'),
    path('coffee/<int:pk>/', CoffeeViewSet.as_view(), name='coffee-detail'),

    # Origins
    path('origins/', OriginView.as_view(), name='origins'),

    # File uploads
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('files/',  FileUploadView.as_view(), name='file-list'),

    # User listing (admin only)
    path('users/', UserList.as_view(), name='user-list'),

    # All operations
    path('operations/', OperationList.as_view(), name='operation-list'),

    # Debug users and operations
    path('debug-users-ops/', debug_users_and_operations),

    # Debug all operations
    path('debug-all-operations/', debug_all_operations),

    # Log operation
    path('log-operation/', log_operation),
]
