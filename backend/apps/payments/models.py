"""Payments models — Payment, SellerPayout (Phase 3 implementation)."""
from django.conf import settings
from django.db import models


class Payment(models.Model):
    """Payment record for an order."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    order = models.ForeignKey(
        "orders.Order", on_delete=models.CASCADE, related_name="payments"
    )
    provider = models.CharField(max_length=50, default="mock")
    provider_ref = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    method = models.CharField(max_length=10)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payments"

    def __str__(self):
        return f"Payment {self.provider_ref} — {self.get_status_display()}"


class SellerPayout(models.Model):
    """Tracks payouts to sellers after order fulfillment."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    shop = models.ForeignKey(
        "catalog.Shop", on_delete=models.PROTECT, related_name="payouts"
    )
    suborder = models.ForeignKey(
        "orders.SubOrder", on_delete=models.PROTECT, related_name="payouts"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "seller_payouts"

    def __str__(self):
        return f"Payout to {self.shop.name} — ${self.amount}"
