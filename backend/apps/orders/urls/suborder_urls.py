from django.urls import path
from apps.orders.views import SellerSubOrdersView, SubOrderAcceptDenyView

urlpatterns = [
    path("seller/", SellerSubOrdersView.as_view(), name="seller-suborders"),
    path("<int:pk>/action/", SubOrderAcceptDenyView.as_view(), name="suborder-action"),
]
