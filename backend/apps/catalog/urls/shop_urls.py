from django.urls import path
from apps.catalog.views import CustomerFollowedShopsView, SellerFollowToggleView, ShopDetailView

urlpatterns = [
    path("following/mine/", CustomerFollowedShopsView.as_view(), name="followed-shops-mine"),
    path("<slug:slug>/", ShopDetailView.as_view(), name="shop-detail"),
    path("<slug:slug>/follow/", SellerFollowToggleView.as_view(), name="shop-follow"),
]
