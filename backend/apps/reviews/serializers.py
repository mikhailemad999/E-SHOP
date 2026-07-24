"""
Reviews & Favorites serializers.
"""

from rest_framework import serializers
from apps.catalog.serializers import ListingSerializer
from .models import Favorite, Review


class ReviewSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.get_full_name", read_only=True)
    customer_avatar = serializers.ImageField(source="customer.avatar", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id", "customer", "customer_name", "customer_avatar",
            "listing", "rating", "comment", "seller_response",
            "is_verified_purchase", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "customer", "is_verified_purchase", "seller_response", "created_at", "updated_at"]


class FavoriteSerializer(serializers.ModelSerializer):
    listing_detail = ListingSerializer(source="listing", read_only=True)

    class Meta:
        model = Favorite
        fields = ["id", "customer", "listing", "listing_detail", "created_at"]
        read_only_fields = ["id", "customer", "created_at"]
