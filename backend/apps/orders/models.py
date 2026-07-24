"""
Orders models — Order, SubOrder, Cart for multi-vendor checkout.

Architecture (from spec §5.4):
- Order = what the customer pays for and tracks
- SubOrder = one per seller (what each seller fulfills independently)
- Cart holds items from multiple sellers, split at checkout
"""

from django.conf import settings
from django.db import models


class Cart(models.Model):
    """Customer's shopping cart. One cart per customer."""

    customer = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "carts"

    def __str__(self):
        return f"Cart for {self.customer.email}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def item_count(self):
        return self.items.aggregate(total=models.Sum("quantity"))["total"] or 0


class CartItem(models.Model):
    """Individual item in a cart — references a Listing."""

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    listing = models.ForeignKey(
        "catalog.Listing", on_delete=models.CASCADE, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cart_items"
        unique_together = ["cart", "listing"]

    def __str__(self):
        return f"{self.quantity}x {self.listing}"

    @property
    def subtotal(self):
        return self.listing.price * self.quantity


class Order(models.Model):
    """
    What the customer pays for. Contains one or more SubOrders (one per seller).
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        PARTIALLY_SHIPPED = "partially_shipped", "Partially Shipped"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"

    class PaymentMethod(models.TextChoices):
        CARD = "card", "Credit/Debit Card"
        COD = "cod", "Cash on Delivery"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    order_number = models.CharField(max_length=20, unique=True, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PaymentMethod.choices,
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_address = models.JSONField(
        help_text="Snapshot of the shipping address at order time"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.order_number}"


class SubOrder(models.Model):
    """
    One seller's portion of an Order. Each SubOrder is fulfilled
    independently — it gets its own delivery assignment and tracking.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        DENIED = "denied", "Denied"
        PACKED = "packed", "Packed"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        RETURNED = "returned", "Returned"
        REFUNDED = "refunded", "Refunded"

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="suborders"
    )
    shop = models.ForeignKey(
        "catalog.Shop", on_delete=models.PROTECT, related_name="suborders"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    seller_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sub_orders"
        indexes = [
            models.Index(fields=["status", "shop"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"SubOrder {self.id} (Order {self.order.order_number}) — {self.shop.name}"


class SubOrderItem(models.Model):
    """Individual line item within a SubOrder."""

    suborder = models.ForeignKey(
        SubOrder, on_delete=models.CASCADE, related_name="items"
    )
    listing = models.ForeignKey(
        "catalog.Listing", on_delete=models.PROTECT, related_name="order_items"
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "sub_order_items"

    def __str__(self):
        return f"{self.quantity}x {self.listing.product.title}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity


class ReturnRequest(models.Model):
    """
    Return Merchandise Authorization — own object with status lifecycle.
    Scoped per SubOrderItem so multi-seller orders have independent return states.
    """

    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        SELLER_REVIEWING = "seller_reviewing", "Seller Reviewing"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        IN_TRANSIT_BACK = "in_transit_back", "In Transit Back"
        RECEIVED_BY_SELLER = "received_by_seller", "Received by Seller"
        REFUNDED = "refunded", "Refunded"
        EXCHANGED = "exchanged", "Exchanged"

    suborder_item = models.ForeignKey(
        SubOrderItem, on_delete=models.CASCADE, related_name="returns"
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="return_requests",
    )
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REQUESTED,
    )
    admin_notes = models.TextField(blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "return_requests"
        ordering = ["-requested_at"]

    def __str__(self):
        return f"Return #{self.id} — {self.get_status_display()}"
