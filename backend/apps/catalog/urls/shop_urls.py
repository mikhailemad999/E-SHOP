from django.urls import path
from apps.catalog.views import SellerFollowToggleView, ShopDetailView

urlpatterns = [
    path("<slug:slug>/", ShopDetailView.as_view(), name="shop-detail"),
    path("<slug:slug>/follow/", SellerFollowToggleView.as_view(), name="shop-follow"),
]
