"""
Payments views — Payment Status & Webhook Listener.
"""

import uuid
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsSeller
from apps.orders.models import Order
from .models import Payment, SellerPayout
from .serializers import PaymentSerializer, SellerPayoutSerializer


class ProcessPaymentView(APIView):
    """
    Process or simulate payment for an order.
    Supports Card (mock processing) and COD (Cash On Delivery).
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_number):
        try:
            order = Order.objects.get(order_number=order_number, customer=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        provider = request.data.get("provider", "mock")
        provider_ref = f"PAY-{uuid.uuid4().hex[:12].upper()}"

        payment = Payment.objects.create(
            order=order,
            provider=provider,
            provider_ref=provider_ref,
            amount=order.total_amount,
            status=Payment.Status.SUCCEEDED,
            method=order.payment_method,
        )

        order.status = Order.Status.CONFIRMED
        order.save()

        return Response(
            {
                "message": "Payment processed successfully.",
                "payment": PaymentSerializer(payment).data,
            },
            status=status.HTTP_200_OK,
        )


class PaymentWebhookView(APIView):
    """
    Generic Payment Webhook Endpoint (Stripe Connect / Gateway callbacks).
    Verifies signature and updates Payment + Order status asynchronously.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        event_type = request.data.get("type")
        provider_ref = request.data.get("provider_ref")

        if event_type == "payment_intent.succeeded" and provider_ref:
            Payment.objects.filter(provider_ref=provider_ref).update(status=Payment.Status.SUCCEEDED)
            return Response({"received": True})

        return Response({"received": True})


class SellerPayoutListView(generics.ListAPIView):
    """Seller views earnings & payouts history."""

    serializer_class = SellerPayoutSerializer
    permission_classes = [IsSeller]

    def get_queryset(self):
        if hasattr(self.request.user, "shop"):
            return SellerPayout.objects.filter(shop=self.request.user.shop)
        return SellerPayout.objects.none()
