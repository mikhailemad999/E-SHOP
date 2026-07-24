from django.urls import path
from apps.reviews.views import CustomerFavoriteListView, FavoriteToggleView

urlpatterns = [
    path("", CustomerFavoriteListView.as_view(), name="favorite-list"),
    path("<int:listing_id>/toggle/", FavoriteToggleView.as_view(), name="favorite-toggle"),
]
