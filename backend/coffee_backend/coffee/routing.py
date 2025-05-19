from django.urls import re_path
from .consumers import CoffeeConsumer

websocket_urlpatterns = [
    re_path(r"ws/coffee/$", CoffeeConsumer.as_asgi()),
]
