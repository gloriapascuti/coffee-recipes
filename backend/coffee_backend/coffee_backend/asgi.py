# import os
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from coffee.routing import websocket_urlpatterns
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coffee_backend.settings')
#
# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             websocket_urlpatterns
#         )
#     ),
# })


# coffee_backend/asgi.py

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from coffee.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coffee_backend.settings')
django.setup()

application = ProtocolTypeRouter({
    # HTTP requests are handled by Django
    "http": get_asgi_application(),

    # WebSocket requests are handled by Channels (without auth middleware for now)
    "websocket": URLRouter(
        websocket_urlpatterns
    ),
})
