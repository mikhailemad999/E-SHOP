"""
Shipping views — Delivery Assignment, Status Updates, GPS Location Ping ingestion.
"""

import uuid
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsDeliveryAgent, IsDeliveryManager
from apps.notifications.models import Notification
from .models import DeliveryAssignment, DeliveryLocationPing
from .serializers import DeliveryAssignmentSerializer, DeliveryLocationPingSerializer


class DispatchAssignmentCreateView(generics.CreateAPIView):
    """Delivery Manager assigns a SubOrder/Order to a Delivery Agent."""

    serializer_class = DeliveryAssignmentSerializer
    permission_classes = [IsDeliveryManager]

    def perform_create(self, serializer):
        tracking_number = f"TRK-{uuid.uuid4().hex[:10].upper()}"
        serializer.save(tracking_number=tracking_number, status=DeliveryAssignment.Status.ASSIGNED)


class AgentQueueView(generics.ListAPIView):
    """Delivery Agent views their assigned active deliveries."""

    serializer_class = DeliveryAssignmentSerializer
    permission_classes = [IsDeliveryAgent]

    def get_queryset(self):
        return DeliveryAssignment.objects.filter(
            agent=self.request.user
        ).exclude(status=DeliveryAssignment.Status.DELIVERED).prefetch_related("location_pings").order_by("-assigned_at")


class DeliveryStatusUpdateView(APIView):
    """Delivery Agent updates status (picked_up, in_transit, delivered, failed)."""

    permission_classes = [IsDeliveryAgent]

    def post(self, request, tracking_number):
        try:
            assignment = DeliveryAssignment.objects.get(tracking_number=tracking_number, agent=request.user)
        except DeliveryAssignment.DoesNotExist:
            return Response({"error": "Delivery assignment not found."}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")
        proof_image = request.FILES.get("proof_image")

        if new_status in dict(DeliveryAssignment.Status.choices):
            assignment.status = new_status
            if new_status == DeliveryAssignment.Status.PICKED_UP:
                assignment.picked_up_at = timezone.now()
            elif new_status == DeliveryAssignment.Status.DELIVERED:
                assignment.delivered_at = timezone.now()
                if proof_image:
                    assignment.proof_image = proof_image

            assignment.save()

            try:
                customer = (
                    assignment.suborder.order.customer
                    if assignment.suborder
                    else (assignment.order.customer if assignment.order else None)
                )
                if customer:
                    notif_type = (
                        Notification.Type.DELIVERY_COMPLETE
                        if new_status == DeliveryAssignment.Status.DELIVERED
                        else Notification.Type.SHIPMENT_UPDATE
                    )
                    Notification.objects.create(
                        user=customer,
                        type=notif_type,
                        title=f"Delivery {new_status.replace('_', ' ').capitalize()}",
                        message=f"Tracking #{assignment.tracking_number} status updated to {new_status.replace('_', ' ')}.",
                        payload={"tracking_number": assignment.tracking_number, "status": new_status},
                    )
            except Exception:
                pass

            return Response({"message": f"Delivery status updated to {new_status}."})

        return Response({"error": "Invalid status value."}, status=status.HTTP_400_BAD_REQUEST)


class LocationPingIngestView(generics.CreateAPIView):
    """Delivery Agent REST fallback endpoint for pushing GPS pings."""

    serializer_class = DeliveryLocationPingSerializer
    permission_classes = [IsDeliveryAgent]


class CustomerTrackingDetailView(generics.RetrieveAPIView):
    """Customer views live tracking details for an assignment by tracking_number."""

    serializer_class = DeliveryAssignmentSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "tracking_number"
    queryset = DeliveryAssignment.objects.all()


class DeliveryManagerAgentsView(APIView):
    """
    Delivery Manager endpoint to view & register Delivery Agents (Delivery Boys).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from apps.accounts.models import DeliveryAgentProfile, User
        agents = User.objects.filter(role=User.Role.DELIVERY_AGENT).select_related("delivery_agent_profile")
        data = []
        for agent in agents:
            profile = getattr(agent, "delivery_agent_profile", None)
            data.append({
                "id": agent.id,
                "username": agent.username,
                "email": agent.email,
                "first_name": agent.first_name,
                "last_name": agent.last_name,
                "phone": agent.phone,
                "vehicle_type": profile.vehicle_type if profile else "N/A",
                "license_plate": profile.license_plate if profile else "N/A",
                "manager": profile.delivery_manager.username if profile and profile.delivery_manager else "N/A",
            })
        return Response(data)

    def post(self, request):
        from apps.accounts.models import DeliveryAgentProfile, User
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password", "AgentPass123!")
        first_name = request.data.get("first_name", "")
        last_name = request.data.get("last_name", "")
        phone = request.data.get("phone", "")
        vehicle_type = request.data.get("vehicle_type", "motorcycle")
        license_plate = request.data.get("license_plate", "PLATE-NEW")

        if not username or not email:
            return Response({"error": "Username and Email are required."}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists."}, status=400)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=User.Role.DELIVERY_AGENT,
        )

        DeliveryAgentProfile.objects.create(
            user=user,
            delivery_manager=request.user if request.user.role == User.Role.DELIVERY_MANAGER else None,
            vehicle_type=vehicle_type,
            license_plate=license_plate,
        )

        return Response({
            "message": f"Delivery Agent '{username}' registered successfully!",
            "agent_id": user.id,
            "email": user.email,
        }, status=201)
