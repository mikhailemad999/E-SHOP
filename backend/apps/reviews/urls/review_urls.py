from django.urls import path
from apps.reviews.views import ListingReviewListCreateView

urlpatterns = [
    path("<int:listing_id>/reviews/", ListingReviewListCreateView.as_view(), name="listing-reviews"),
]
