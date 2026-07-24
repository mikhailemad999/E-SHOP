from django.urls import path
from apps.catalog.views import (
    ListingCreateView,
    ListingDetailView,
    ModerateListingView,
    ModerationQueueView,
    SellerAddProductListingView,
    SellerListingsView,
)

urlpatterns = [
    path("add-product/", SellerAddProductListingView.as_view(), name="seller-add-product"),
    path("create/", ListingCreateView.as_view(), name="listing-create"),
    path("mine/", SellerListingsView.as_view(), name="seller-listings"),
    path("moderation-queue/", ModerationQueueView.as_view(), name="moderation-queue"),
    path("<int:pk>/", ListingDetailView.as_view(), name="listing-detail"),
    path("<int:pk>/moderate/", ModerateListingView.as_view(), name="listing-moderate"),
]
