"""
Notification Serializer — Formats in-app notifications for users.
"""
from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "type",
            "type_display",
            "title",
            "message",
            "payload",
            "is_read",
            "read_at",
            "created_at",
        ]
        read_only_fields = ["id", "type", "title", "message", "payload", "created_at"]
