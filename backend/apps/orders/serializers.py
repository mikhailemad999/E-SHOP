"""
Orders serializers — Cart, Checkout, Order, SubOrder (per-seller), and ReturnRequest.
"""

from rest_framework import serializers
from apps.catalog.serializers import ListingSerializer
from .models import Cart, CartItem, Order, ReturnRequest, SubOrder, SubOrderItem


class CartItemSerializer(serializers.ModelSerializer):
    """Cart item serializer with nested listing detail."""

    listing_detail = ListingSerializer(source="listing", read_only=True)
    product_title = serializers.CharField(source="listing.product.title", read_only=True)
    shop_name = serializers.CharField(source="listing.shop.name", read_only=True)
    shop_id = serializers.IntegerField(source="listing.shop.id", read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = [
            "id", "listing", "listing_detail", "product_title",
            "shop_id", "shop_name", "quantity", "subtotal", "added_at",
        ]


class CartSerializer(serializers.ModelSerializer):
    """Customer cart with items grouped by seller."""

    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items", "total", "item_count", "updated_at"]


class SubOrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="listing.product.title", read_only=True)
    sku = serializers.CharField(source="listing.sku", read_only=True)

    class Meta:
        model = SubOrderItem
        fields = ["id", "listing", "product_title", "sku", "quantity", "unit_price", "subtotal"]


class SubOrderSerializer(serializers.ModelSerializer):
    """One seller's suborder."""

    shop_name = serializers.CharField(source="shop.name", read_only=True)
    items = SubOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = SubOrder
        fields = [
            "id", "order", "shop", "shop_name", "status",
            "subtotal", "seller_notes", "items", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "order", "shop", "subtotal", "created_at", "updated_at"]


class OrderDetailSerializer(serializers.ModelSerializer):
    """Customer-facing full order with nested SubOrders."""

    suborders = SubOrderSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "order_number", "status", "payment_method",
            "total_amount", "shipping_address", "notes",
            "suborders", "created_at", "updated_at",
        ]


class CheckoutSerializer(serializers.Serializer):
    """
    Checkout payload serializer:
    Customer passes shipping address ID (or raw address object) + payment_method.
    Splits multi-seller cart into one Order + multiple SubOrders in a single DB transaction.
    """

    address_id = serializers.IntegerField(required=False)
    shipping_address = serializers.JSONField(required=False)
    payment_method = serializers.ChoiceField(choices=Order.PaymentMethod.choices)
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, attrs):
        if not attrs.get("address_id") and not attrs.get("shipping_address"):
            raise serializers.ValidationError("Either address_id or shipping_address is required.")
        return attrs


class ReturnRequestSerializer(serializers.ModelSerializer):
    """Return Merchandise Authorization serializer."""

    product_title = serializers.CharField(source="suborder_item.listing.product.title", read_only=True)
    product_image = serializers.SerializerMethodField()
    shop_name = serializers.CharField(source="suborder_item.suborder.shop.name", read_only=True)
    shop_id = serializers.IntegerField(source="suborder_item.suborder.shop.id", read_only=True)
    order_number = serializers.CharField(source="suborder_item.suborder.order.order_number", read_only=True)
    customer_email = serializers.EmailField(source="customer.email", read_only=True)
    customer_name = serializers.SerializerMethodField()
    unit_price = serializers.DecimalField(source="suborder_item.unit_price", max_digits=12, decimal_places=2, read_only=True)
    quantity = serializers.IntegerField(source="suborder_item.quantity", read_only=True)

    class Meta:
        model = ReturnRequest
        fields = [
            "id", "suborder_item", "product_title", "product_image",
            "shop_name", "shop_id", "order_number", "customer_email",
            "customer_name", "unit_price", "quantity", "reason",
            "status", "admin_notes", "requested_at", "resolved_at",
        ]
        read_only_fields = ["id", "status", "requested_at", "resolved_at"]

    def get_customer_name(self, obj):
        name = f"{obj.customer.first_name} {obj.customer.last_name}".strip()
        return name if name else obj.customer.username

    def get_product_image(self, obj):
        listing = obj.suborder_item.listing
        img = listing.images.first()
        if img:
            return str(img.image)
        return None

