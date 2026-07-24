"""Shipping models — DeliveryAssignment, DeliveryLocationPing (Phase 2)."""
from django.conf import settings
from django.db import models


class DeliveryAssignment(models.Model):
    """Assignment of a SubOrder (or full Order) to a delivery agent."""

    class Status(models.TextChoices):
        ASSIGNED = "assigned", "Assigned"
        PICKED_UP = "picked_up", "Picked Up"
        IN_TRANSIT = "in_transit", "In Transit"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"

    suborder = models.ForeignKey(
        "orders.SubOrder", on_delete=models.CASCADE, related_name="delivery_assignments",
        null=True, blank=True,
    )
    order = models.ForeignKey(
        "orders.Order", on_delete=models.CASCADE, related_name="delivery_assignments",
        null=True, blank=True,
        help_text="Set for multi-stop pickup (one agent, whole order)",
    )
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="delivery_assignments",
        limit_choices_to={"role": "DELIVERY_AGENT"},
    )
    tracking_number = models.CharField(max_length=30, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ASSIGNED)
    proof_image = models.ImageField(upload_to="delivery_proofs/", blank=True, null=True)
    notes = models.TextField(blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "delivery_assignments"
        indexes = [
            models.Index(fields=["agent", "status"]),
        ]

    def __str__(self):
        return f"Delivery {self.tracking_number} — {self.get_status_display()}"


class DeliveryLocationPing(models.Model):
    """GPS location pings from delivery agents. High-write table."""

    assignment = models.ForeignKey(
        DeliveryAssignment, on_delete=models.CASCADE, related_name="location_pings"
    )
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lng = models.DecimalField(max_digits=9, decimal_places=6)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "delivery_location_pings"
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"Ping {self.lat},{self.lng} at {self.recorded_at}"
