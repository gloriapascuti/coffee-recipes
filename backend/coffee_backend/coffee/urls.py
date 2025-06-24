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
    generate_ai_recipe,
    toggle_like,
    most_popular_recipes,
    challenge_list,
    respond_to_challenge,
    submit_recipe,
    vote_challenge,
    user_notifications,
    mark_notification_read,
    available_users,
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
    path('upload/<str:filename>/', FileUploadView.as_view(), name='file-delete'),
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
    
    # AI recipe generation
    path('generate-ai-recipe/', generate_ai_recipe, name='generate-ai-recipe'),
    
    # Like system
    path('like/<int:coffee_id>/', toggle_like, name='toggle-like'),
    
    # Most popular recipes
    path('most-popular/', most_popular_recipes, name='most-popular-recipes'),
    
    # Challenge system
    path('challenges/', challenge_list, name='challenge-list'),
    path('challenges/<int:challenge_id>/respond/', respond_to_challenge, name='respond-to-challenge'),
    path('challenges/<int:challenge_id>/submit-recipe/', submit_recipe, name='submit-recipe'),
    path('challenges/<int:challenge_id>/vote/', vote_challenge, name='vote-challenge'),
    path('notifications/', user_notifications, name='user-notifications'),
    path('notifications/<int:notification_id>/read/', mark_notification_read, name='mark-notification-read'),
    path('available-users/', available_users, name='available-users'),
]
