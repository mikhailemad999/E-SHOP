"""User management URLs — profile, addresses, admin-created accounts."""

from django.urls import path

from apps.accounts.views import (
    AddressDetailView,
    AddressListCreateView,
    CreateAdminView,
    CreateDeliveryAgentView,
    CreateDeliveryManagerView,
    UserProfileView,
)

urlpatterns = [
    path("me/", UserProfileView.as_view(), name="user-profile"),
    path("me/addresses/", AddressListCreateView.as_view(), name="address-list"),
    path("me/addresses/<int:pk>/", AddressDetailView.as_view(), name="address-detail"),
    path("admins/", CreateAdminView.as_view(), name="create-admin"),
    path("delivery-managers/", CreateDeliveryManagerView.as_view(), name="create-delivery-manager"),
    path("delivery-agents/", CreateDeliveryAgentView.as_view(), name="create-delivery-agent"),
]
