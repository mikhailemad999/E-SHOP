from django.urls import path
from apps.orders.views import ReturnRequestListCreateView

urlpatterns = [
    path("", ReturnRequestListCreateView.as_view(), name="return-list-create"),
]
