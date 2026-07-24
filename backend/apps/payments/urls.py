from django.urls import path
from apps.payments.views import PaymentWebhookView, ProcessPaymentView, SellerPayoutListView

urlpatterns = [
    path("process/<str:order_number>/", ProcessPaymentView.as_view(), name="payment-process"),
    path("webhook/", PaymentWebhookView.as_view(), name="payment-webhook"),
    path("payouts/", SellerPayoutListView.as_view(), name="seller-payouts"),
]
