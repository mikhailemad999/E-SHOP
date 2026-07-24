"""
Django Channels WebSocket Consumer for live delivery GPS tracking.
Clients subscribe to `ws/delivery/{tracking_number}/`.
Delivery Agents push location pings; consumer broadcasts to all subscribed customers/managers.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class DeliveryTrackingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.tracking_number = self.scope["url_route"]["kwargs"]["tracking_number"]
        self.group_name = f"delivery_{self.tracking_number}"

        # Join tracking group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave tracking group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Receive GPS ping from agent or status update request from client."""
        data = json.loads(text_data)
        event_type = data.get("type")

        if event_type == "location_ping":
            # Broadcast new GPS location to all group members
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "delivery_location_update",
                    "lat": data.get("lat"),
                    "lng": data.get("lng"),
                    "status": data.get("status"),
                    "timestamp": data.get("timestamp"),
                }
            )

    async def delivery_location_update(self, event):
        """Handler for broadcasted location update message."""
        await self.send(text_data=json.dumps({
            "type": "location_update",
            "lat": event["lat"],
            "lng": event["lng"],
            "status": event.get("status"),
            "timestamp": event.get("timestamp"),
        }))
