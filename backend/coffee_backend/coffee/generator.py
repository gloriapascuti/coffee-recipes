import threading
import time
import random
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from faker import Faker

from .models.coffee import Coffee, Origin
from .serializers import CoffeeSerializer

# the lists your thread will pick from
NAMES = [
    "Espresso", "Latte", "Mocha", "Flat White",
    "Cappuccino", "Macchiato", "V60", "Aeropress",
    "Filter", "Cold Brew"
]
ORIGINS = [
    "Italy", "Brazil", "Colombia", "Ethiopia",
    "France", "USA", "Puerto Rico", "Costa Rica",
    "Yemen", "Mexico"
]

def generate_coffee():
    faker = Faker()
    while True:
        try:
            # 1) pick or create a real Origin
            origin_name = random.choice(ORIGINS)
            origin_obj, _ = Origin.objects.get_or_create(name=origin_name)

            # 2) now create a Coffee with that Origin instance
            coffee = Coffee.objects.create(
                name=random.choice(NAMES),
                origin=origin_obj,
                description=faker.sentence(nb_words=6)
            )
            print("✔️ Created new coffee:", coffee)

            # 3) serialize & broadcast
            data = CoffeeSerializer(coffee).data
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "coffee_updates",
                {
                    "type": "coffee.update",
                    "coffee": data
                }
            )

        except Exception as e:
            # this should no longer be your origin‐null error
            print(f"🔴 Failed to create coffee: {e}")

        # 4) wait before next one
        time.sleep(100000)

def start_coffee_thread():
    thread = threading.Thread(
        target=generate_coffee,
        daemon=True
    )
    thread.start()
