"""
Payments serializers — Payment & SellerPayout.
"""

from rest_framework import serializers
from .models import Payment, SellerPayout


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id", "order", "provider", "provider_ref",
            "amount", "status", "method", "metadata",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "provider_ref", "created_at", "updated_at"]


class SellerPayoutSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source="shop.name", read_only=True)

    class Meta:
        model = SellerPayout
        fields = [
            "id", "shop", "shop_name", "suborder",
            "amount", "platform_fee", "status", "paid_at", "created_at",
        ]
        read_only_fields = ["id", "created_at"]
