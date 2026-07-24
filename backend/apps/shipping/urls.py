from django.urls import path
from apps.shipping.views import (
    AgentQueueView,
    CustomerTrackingDetailView,
    DeliveryManagerAgentsView,
    DeliveryStatusUpdateView,
    DispatchAssignmentCreateView,
    LocationPingIngestView,
)

urlpatterns = [
    path("agents/", DeliveryManagerAgentsView.as_view(), name="delivery-manager-agents"),
    path("dispatch/", DispatchAssignmentCreateView.as_view(), name="dispatch-create"),
    path("agent/queue/", AgentQueueView.as_view(), name="agent-queue"),
    path("<str:tracking_number>/status/", DeliveryStatusUpdateView.as_view(), name="delivery-status-update"),
    path("ping/", LocationPingIngestView.as_view(), name="location-ping"),
    path("track/<str:tracking_number>/", CustomerTrackingDetailView.as_view(), name="customer-tracking"),
]
