"""Notification model — in-app notifications with JSONB payload."""
from django.conf import settings
from django.db import models


class Notification(models.Model):
    """In-app notification for any user role."""

    class Type(models.TextChoices):
        ORDER_PLACED = "order_placed", "Order Placed"
        ORDER_ACCEPTED = "order_accepted", "Order Accepted"
        ORDER_DENIED = "order_denied", "Order Denied"
        SHIPMENT_UPDATE = "shipment_update", "Shipment Update"
        DELIVERY_COMPLETE = "delivery_complete", "Delivery Complete"
        RETURN_UPDATE = "return_update", "Return Update"
        NEW_PRODUCT = "new_product", "New Product (Followed Shop)"
        LOW_STOCK = "low_stock", "Low Stock Alert"
        PAYOUT = "payout", "Payout Processed"
        SYSTEM = "system", "System"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    type = models.CharField(max_length=30, choices=Type.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    payload = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_type_display()} → {self.user.email}"
