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
    get_favorites,
    get_my_recipes,
    toggle_privacy,
    most_popular_recipes,
    challenge_list,
    respond_to_challenge,
    submit_recipe,
    vote_challenge,
    user_notifications,
    mark_notification_read,
    available_users,
    add_consumed_coffee,
    add_custom_consumed_coffee,
    remove_consumed_coffee,
    get_consumed_coffees,
    health_profile,
    add_blood_pressure,
    get_blood_pressure_entries,
    generate_prediction,
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
    
    # Like system (favorites)
    path('favorites/', get_favorites, name='get-favorites'),
    path('like/<int:coffee_id>/', toggle_like, name='toggle-like'),
    # My Recipes (includes private recipes)
    path('my-recipes/', get_my_recipes, name='get-my-recipes'),
    # Privacy
    path('privacy/<int:coffee_id>/', toggle_privacy, name='toggle-privacy'),
    
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
    
    # Consumed coffees
    path('consumed/<int:coffee_id>/', add_consumed_coffee, name='add-consumed-coffee'),
    path('consumed/custom/', add_custom_consumed_coffee, name='add-custom-consumed-coffee'),
    path('consumed/remove/<int:consumed_id>/', remove_consumed_coffee, name='remove-consumed-coffee'),
    path('consumed/', get_consumed_coffees, name='get-consumed-coffees'),
    
    # Health profile
    path('health-profile/', health_profile, name='health-profile'),
    path('blood-pressure/', add_blood_pressure, name='add-blood-pressure'),
    path('blood-pressure/list/', get_blood_pressure_entries, name='get-blood-pressure-entries'),
    
    # Prediction
    path('prediction/', generate_prediction, name='generate-prediction'),
]
