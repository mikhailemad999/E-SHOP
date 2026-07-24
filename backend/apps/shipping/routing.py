"""WebSocket routing for real-time delivery tracking."""
from django.urls import re_path
from .consumers import DeliveryTrackingConsumer

websocket_urlpatterns = [
    re_path(r"^ws/delivery/(?P<tracking_number>[\w-]+)/$", DeliveryTrackingConsumer.as_async()),
]
