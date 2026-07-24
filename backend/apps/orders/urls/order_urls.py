from django.urls import path
from apps.orders.views import CustomerOrdersView, OrderDetailView

urlpatterns = [
    path("", CustomerOrdersView.as_view(), name="customer-orders"),
    path("<str:order_number>/", OrderDetailView.as_view(), name="order-detail"),
]
