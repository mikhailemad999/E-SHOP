"""
Orders views — Cart management, Multi-Vendor Checkout, Order history, Seller SubOrder management, and Returns (RMA).
"""

import uuid
from collections import defaultdict
from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Address
from apps.accounts.permissions import IsCustomer, IsSeller, IsAdminOrSuperAdmin
from apps.catalog.models import Listing
from apps.notifications.models import Notification
from .models import Cart, CartItem, Order, ReturnRequest, SubOrder, SubOrderItem
from .serializers import (
    CartItemSerializer,
    CartSerializer,
    CheckoutSerializer,
    OrderDetailSerializer,
    ReturnRequestSerializer,
    SubOrderSerializer,
)


# ─── Cart Views ───────────────────────────────────────────────────
class CartDetailView(generics.RetrieveAPIView):
    """Customer gets their current active cart."""

    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(customer=self.request.user)
        return cart


class CartItemAddView(APIView):
    """Add a listing to customer cart or increment quantity."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        listing_id = request.data.get("listing_id")
        quantity = int(request.data.get("quantity", 1))

        try:
            listing = Listing.objects.get(id=listing_id, status=Listing.Status.LIVE)
        except Listing.DoesNotExist:
            return Response({"error": "Listing not available or out of stock."}, status=status.HTTP_404_NOT_FOUND)

        if listing.stock_qty < quantity:
            return Response({"error": f"Only {listing.stock_qty} items available in stock."}, status=status.HTTP_400_BAD_REQUEST)

        cart, _ = Cart.objects.get_or_create(customer=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, listing=listing, defaults={"quantity": quantity})

        if not created:
            if listing.stock_qty < cart_item.quantity + quantity:
                return Response({"error": f"Cannot add more than {listing.stock_qty} items to cart."}, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity += quantity
            cart_item.save()

        return Response(CartSerializer(cart, context={"request": request}).data, status=status.HTTP_200_OK)


class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Update quantity or remove an item from customer cart."""

    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__customer=self.request.user)


# ─── Checkout View (Multi-Vendor Splitting) ──────────────────────
class CheckoutView(APIView):
    """
    Multi-Vendor Checkout Engine:
    1. Reads items from customer's Cart.
    2. Group items by Seller (Shop).
    3. Creates 1 parent Order + N SubOrders (one per seller).
    4. Decrements stock for each Listing.
    5. Clears the customer's Cart.
    All executed atomically inside @transaction.atomic!
    """

    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        cart, _ = Cart.objects.get_or_create(customer=request.user)
        cart_items = cart.items.select_related("listing__shop", "listing__product").all()

        # If DB cart is empty, populate from request items array if provided
        if not cart_items.exists() and request.data.get("items"):
            for raw_item in request.data.get("items", []):
                lid = raw_item.get("listing_id") or raw_item.get("id")
                qty = raw_item.get("quantity", 1)
                if lid:
                    try:
                        listing_obj = Listing.objects.get(id=lid, status=Listing.Status.LIVE)
                        CartItem.objects.create(cart=cart, listing=listing_obj, quantity=qty)
                    except Listing.DoesNotExist:
                        continue
            cart_items = cart.items.select_related("listing__shop", "listing__product").all()

        if not cart_items.exists():
            return Response({"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        # Resolve Shipping Address
        if data.get("address_id"):
            try:
                addr = Address.objects.get(id=data["address_id"], user=request.user)
                address_data = {
                    "full_name": addr.full_name,
                    "phone": addr.phone,
                    "address_line1": addr.address_line1,
                    "address_line2": addr.address_line2,
                    "city": addr.city,
                    "state": addr.state,
                    "postal_code": addr.postal_code,
                    "country": addr.country,
                }
            except Address.DoesNotExist:
                return Response({"error": "Address not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            address_data = data["shipping_address"]

        # Validate stock & group items by Shop
        items_by_shop = defaultdict(list)
        total_amount = 0

        for item in cart_items:
            listing = item.listing
            if listing.stock_qty < item.quantity or listing.status != Listing.Status.LIVE:
                return Response(
                    {"error": f"Item '{listing.product.title}' by {listing.shop.name} is no longer available in the requested quantity."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            items_by_shop[listing.shop].append(item)
            total_amount += listing.price * item.quantity

        # Create parent Order
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        order = Order.objects.create(
            customer=request.user,
            order_number=order_number,
            payment_method=data["payment_method"],
            total_amount=total_amount,
            shipping_address=address_data,
            notes=data.get("notes", ""),
            status=Order.Status.PENDING,
        )

        # Create SubOrders per Shop & update stock
        for shop, items in items_by_shop.items():
            subtotal = sum(i.listing.price * i.quantity for i in items)
            suborder = SubOrder.objects.create(
                order=order,
                shop=shop,
                subtotal=subtotal,
                status=SubOrder.Status.PENDING,
            )

            for item in items:
                listing = item.listing
                SubOrderItem.objects.create(
                    suborder=suborder,
                    listing=listing,
                    quantity=item.quantity,
                    unit_price=listing.price,
                )
                # Decrement stock
                listing.stock_qty -= item.quantity
                listing.save()

        # Clear cart
        cart.items.all().delete()

        # Generate in-app notifications
        try:
            Notification.objects.create(
                user=request.user,
                type=Notification.Type.ORDER_PLACED,
                title="Order Placed Successfully",
                message=f"Your order #{order.order_number} for ${order.total_amount} has been placed.",
                payload={"order_id": order.id, "order_number": order.order_number},
            )
            for shop, items in items_by_shop.items():
                if shop.owner:
                    Notification.objects.create(
                        user=shop.owner,
                        type=Notification.Type.ORDER_PLACED,
                        title=f"New Order #{order.order_number}",
                        message=f"New order received for shop '{shop.name}'.",
                        payload={"order_number": order.order_number, "order_id": order.id},
                    )
        except Exception:
            pass

        return Response(
            {
                "message": "Order placed successfully.",
                "order": OrderDetailSerializer(order).data,
            },
            status=status.HTTP_201_CREATED,
        )


# ─── Order Views ──────────────────────────────────────────────────
class CustomerOrdersView(generics.ListAPIView):
    """Customer views their order history."""

    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).prefetch_related("suborders__items__listing__product")


class OrderDetailView(generics.RetrieveAPIView):
    """Get single order detail by order_number."""

    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "order_number"

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)


# ─── Seller SubOrder Views ────────────────────────────────────────
class SellerSubOrdersView(generics.ListAPIView):
    """Seller views incoming SubOrders for their shop."""

    serializer_class = SubOrderSerializer
    permission_classes = [IsSeller]

    def get_queryset(self):
        if hasattr(self.request.user, "shop"):
            return SubOrder.objects.filter(shop=self.request.user.shop).prefetch_related("items__listing__product")
        return SubOrder.objects.none()


class SubOrderAcceptDenyView(APIView):
    """Seller accepts or denies an incoming SubOrder."""

    permission_classes = [IsSeller]

    def post(self, request, pk):
        try:
            suborder = SubOrder.objects.get(pk=pk, shop=request.user.shop)
        except SubOrder.DoesNotExist:
            return Response({"error": "SubOrder not found."}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get("action")  # 'accept' or 'deny'
        if action == "accept":
            suborder.status = SubOrder.Status.ACCEPTED
            suborder.save()
            try:
                Notification.objects.create(
                    user=suborder.order.customer,
                    type=Notification.Type.ORDER_ACCEPTED,
                    title="SubOrder Accepted",
                    message=f"Shop '{suborder.shop.name}' accepted items in Order #{suborder.order.order_number}.",
                    payload={"order_number": suborder.order.order_number, "suborder_id": suborder.id},
                )
            except Exception:
                pass
            return Response({"message": f"SubOrder #{pk} accepted."})
        elif action == "deny":
            suborder.status = SubOrder.Status.DENIED
            suborder.save()
            # Restore stock
            for item in suborder.items.all():
                item.listing.stock_qty += item.quantity
                item.listing.save()
            try:
                Notification.objects.create(
                    user=suborder.order.customer,
                    type=Notification.Type.ORDER_DENIED,
                    title="SubOrder Denied",
                    message=f"Shop '{suborder.shop.name}' could not fulfill items in Order #{suborder.order.order_number}. Stock has been updated.",
                    payload={"order_number": suborder.order.order_number, "suborder_id": suborder.id},
                )
            except Exception:
                pass
            return Response({"message": f"SubOrder #{pk} denied and stock restored."})
        else:
            return Response({"error": "Invalid action. Use 'accept' or 'deny'."}, status=status.HTTP_400_BAD_REQUEST)


# ─── Return Request Views ─────────────────────────────────────────
class ReturnRequestListCreateView(generics.ListCreateAPIView):
    """Customer views or submits a Return Request (RMA)."""

    serializer_class = ReturnRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReturnRequest.objects.filter(customer=self.request.user).select_related(
            "suborder_item__listing__product", "suborder_item__suborder__shop", "suborder_item__suborder__order"
        )

    def perform_create(self, serializer):
        return_req = serializer.save(customer=self.request.user)
        # Notify Seller
        try:
            shop_owner = return_req.suborder_item.suborder.shop.owner
            if shop_owner:
                Notification.objects.create(
                    user=shop_owner,
                    type=Notification.Type.RETURN_UPDATE,
                    title="New Return Request Received",
                    message=f"Customer requested a return for '{return_req.suborder_item.listing.product.title}' (Order #{return_req.suborder_item.suborder.order.order_number}).",
                    payload={"return_id": return_req.id, "suborder_id": return_req.suborder_item.suborder.id},
                )
        except Exception:
            pass


class SellerReturnRequestListView(generics.ListAPIView):
    """Seller views all Return Requests (RMA) for their shop."""

    serializer_class = ReturnRequestSerializer
    permission_classes = [IsSeller]

    def get_queryset(self):
        if hasattr(self.request.user, "shop"):
            return ReturnRequest.objects.filter(
                suborder_item__suborder__shop=self.request.user.shop
            ).select_related(
                "customer", "suborder_item__listing__product", "suborder_item__suborder__order"
            )
        return ReturnRequest.objects.none()


class AdminReturnRequestListView(generics.ListAPIView):
    """Admin / Super Admin views every shop's return requests across platform."""

    serializer_class = ReturnRequestSerializer
    permission_classes = [IsAdminOrSuperAdmin]

    def get_queryset(self):
        return ReturnRequest.objects.all().select_related(
            "customer", "suborder_item__listing__product", "suborder_item__suborder__shop", "suborder_item__suborder__order"
        )


class ReturnRequestActionView(APIView):
    """
    Seller or Admin updates return status (e.g. approved, rejected, refunded).
    Automatically records resolution and sends an in-app notification to the customer.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            return_req = ReturnRequest.objects.select_related(
                "customer", "suborder_item__suborder__shop", "suborder_item__suborder__order"
            ).get(pk=pk)
        except ReturnRequest.DoesNotExist:
            return Response({"error": "Return request not found."}, status=status.HTTP_404_NOT_FOUND)

        is_admin = request.user.role in ("ADMIN", "SUPER_ADMIN")
        is_seller_owner = (
            request.user.role == "SELLER"
            and hasattr(request.user, "shop")
            and return_req.suborder_item.suborder.shop == request.user.shop
        )

        if not (is_admin or is_seller_owner):
            return Response({"error": "You do not have permission to moderate this return."}, status=status.HTTP_403_FORBIDDEN)

        new_status = request.data.get("status")
        notes = request.data.get("admin_notes", "")

        valid_statuses = [s[0] for s in ReturnRequest.Status.choices]
        if new_status not in valid_statuses:
            return Response({"error": f"Invalid status. Choose from: {valid_statuses}"}, status=status.HTTP_400_BAD_REQUEST)

        return_req.status = new_status
        if notes:
            return_req.admin_notes = notes
        if new_status in [ReturnRequest.Status.REFUNDED, ReturnRequest.Status.REJECTED]:
            from django.utils import timezone
            return_req.resolved_at = timezone.now()

        return_req.save()

        # Send real-time in-app notification to customer
        try:
            display_status = new_status.replace('_', ' ').title()
            Notification.objects.create(
                user=return_req.customer,
                type=Notification.Type.RETURN_UPDATE,
                title=f"Return #{return_req.id} {display_status}",
                message=f"Your return request for '{return_req.suborder_item.listing.product.title}' has been updated to {display_status}.",
                payload={"return_id": return_req.id, "status": new_status},
            )
        except Exception:
            pass

        return Response({
            "message": f"Return #{return_req.id} status updated to {new_status}.",
            "return": ReturnRequestSerializer(return_req).data,
        })

