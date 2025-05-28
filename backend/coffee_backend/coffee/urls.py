from django.urls import path
from .views import (
    healthcheck,
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

    # Coffee CRUD
    path('',          CoffeeViewSet.as_view(), name='coffee-list'),
    path('<int:pk>/', CoffeeViewSet.as_view(), name='coffee-detail'),

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
