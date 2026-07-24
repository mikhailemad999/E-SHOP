"""
Shipping serializers — DeliveryAssignment & DeliveryLocationPing.
"""

from rest_framework import serializers
from .models import DeliveryAssignment, DeliveryLocationPing


class DeliveryLocationPingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryLocationPing
        fields = ["id", "assignment", "lat", "lng", "recorded_at"]
        read_only_fields = ["id", "recorded_at"]


class DeliveryAssignmentSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(source="agent.get_full_name", read_only=True)
    agent_phone = serializers.CharField(source="agent.phone", read_only=True)
    latest_ping = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryAssignment
        fields = [
            "id", "suborder", "order", "agent", "agent_name", "agent_phone",
            "tracking_number", "status", "proof_image", "notes",
            "latest_ping", "assigned_at", "picked_up_at", "delivered_at",
        ]
        read_only_fields = ["id", "tracking_number", "assigned_at", "picked_up_at", "delivered_at"]

    def get_latest_ping(self, obj):
        latest = obj.location_pings.first()
        if latest:
            return DeliveryLocationPingSerializer(latest).data
        return None
