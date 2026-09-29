from django.urls import path
from apps.orders.views import (
    AdminReturnRequestListView,
    ReturnRequestActionView,
    ReturnRequestListCreateView,
    SellerReturnRequestListView,
)

urlpatterns = [
    path("", ReturnRequestListCreateView.as_view(), name="return-list-create"),
    path("seller/", SellerReturnRequestListView.as_view(), name="return-seller-list"),
    path("admin/", AdminReturnRequestListView.as_view(), name="return-admin-list"),
    path("<int:pk>/action/", ReturnRequestActionView.as_view(), name="return-action"),
]

