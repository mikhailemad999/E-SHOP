"""
Reviews & Favorites views — Verified purchase review submit, listing reviews list, favorite toggle.
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import SubOrderItem
from .models import Favorite, Review
from .serializers import FavoriteSerializer, ReviewSerializer


class ListingReviewListCreateView(generics.ListCreateAPIView):
    """List reviews for a listing or submit a review if customer purchased it."""

    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        listing_id = self.kwargs.get("listing_id")
        return Review.objects.filter(listing_id=listing_id).select_related("customer")

    def perform_create(self, serializer):
        listing_id = self.kwargs.get("listing_id")
        # Check if customer has a delivered SubOrder with this listing
        is_verified = SubOrderItem.objects.filter(
            suborder__order__customer=self.request.user,
            listing_id=listing_id,
            suborder__status="delivered",
        ).exists()

        serializer.save(
            customer=self.request.user,
            listing_id=listing_id,
            is_verified_purchase=is_verified,
        )


class FavoriteToggleView(APIView):
    """Customer toggles a listing in their favorites / wishlist."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, listing_id):
        fav, created = Favorite.objects.get_or_create(customer=request.user, listing_id=listing_id)
        if not created:
            fav.delete()
            return Response({"message": "Removed from wishlist.", "is_favorite": False})
        return Response({"message": "Added to wishlist.", "is_favorite": True}, status=status.HTTP_201_CREATED)


class CustomerFavoriteListView(generics.ListAPIView):
    """Customer views their wishlist."""

    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(customer=self.request.user).select_related("listing__product", "listing__shop")
