"""Reviews models — Review, Favorite (Phase 4 implementation)."""
from django.conf import settings
from django.db import models


class Review(models.Model):
    """Product review — only verified purchasers can review."""

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    listing = models.ForeignKey(
        "catalog.Listing", on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    seller_response = models.TextField(blank=True)
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reviews"
        unique_together = ["customer", "listing"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review by {self.customer.email} — {self.rating}★"


class Favorite(models.Model):
    """Customer favorites / wishlist."""

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites"
    )
    listing = models.ForeignKey(
        "catalog.Listing", on_delete=models.CASCADE, related_name="favorited_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "favorites"
        unique_together = ["customer", "listing"]

    def __str__(self):
        return f"{self.customer.email} ♥ {self.listing}"
