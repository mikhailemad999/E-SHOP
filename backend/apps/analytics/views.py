"""
Analytics views — Platform summary statistics for Admin dashboard.
"""

from django.db.models import Sum
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.catalog.models import Listing
from apps.orders.models import Order


class PlatformStatsView(APIView):
    """
    GET /api/stats/
    Returns live platform analytics metrics:
    - total_users
    - total_listings
    - pending_moderation
    - total_orders
    - gross_sales
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        total_users = User.objects.count()
        total_listings = Listing.objects.filter(status=Listing.Status.LIVE).count()
        pending_moderation = Listing.objects.filter(status=Listing.Status.PENDING).count()
        total_orders = Order.objects.count()

        gross_sales_agg = Order.objects.aggregate(total=Sum("total_amount"))["total"] or 0

        return Response(
            {
                "total_users": total_users,
                "total_listings": total_listings,
                "pending_moderation": pending_moderation,
                "total_orders": total_orders,
                "gross_sales": float(gross_sales_agg),
            },
            status=status.HTTP_200_OK,
        )
