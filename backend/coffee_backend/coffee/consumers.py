# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
#
# class CoffeeConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         print("WebSocket connecting...")
#         await self.channel_layer.group_add(
#             "coffee_updates",
#             self.channel_name
#         )
#         await self.accept()
#         print("WebSocket connected!")
#
#     async def disconnect(self, close_code):
#         print("WebSocket disconnecting...")
#         await self.channel_layer.group_discard(
#             "coffee_updates",
#             self.channel_name
#         )
#         print("WebSocket disconnected!")
#
#     async def coffee_update(self, event):
#         print("Sending coffee update...")
#         await self.send(text_data=json.dumps(event["coffee"]))
#         print("Coffee update sent!")


# coffee/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CoffeeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join group for broadcasting coffee updates
        self.group_name = "coffee_updates"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        print(f"WebSocket connected: {self.channel_name}")

    async def disconnect(self, close_code):
        # Leave the coffee_updates group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        print(f"WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        """
        Optional: if you want clients to send messages that
        get broadcast back out to the group, handle them here.
        """
        data = json.loads(text_data)
        # Broadcast the incoming message to the group
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "coffee_update",
                "coffee": data
            }
        )

    async def coffee_update(self, event):
        """
        Handler for events sent to the group.
        Sends the `coffee` payload as JSON back to the client.
        """
        await self.send(text_data=json.dumps(event["coffee"]))
