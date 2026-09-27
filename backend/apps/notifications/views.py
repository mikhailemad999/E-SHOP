"""
Notification Views — List notifications, retrieve unread counts, and mark as read.
"""
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    """List in-app notifications for authenticated user, with optional unread filter."""

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)
        unread_only = self.request.query_params.get("unread")
        if unread_only and unread_only.lower() in ("true", "1"):
            qs = qs.filter(is_read=False)
        return qs


class NotificationMarkReadView(APIView):
    """Mark a single notification as read."""

    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            notif = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found."}, status=status.HTTP_404_NOT_FOUND)

        if not notif.is_read:
            notif.is_read = True
            notif.read_at = timezone.now()
            notif.save(update_fields=["is_read", "read_at"])

        return Response(NotificationSerializer(notif).data)


class NotificationMarkAllReadView(APIView):
    """Mark all unread notifications as read for current user."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        updated_count = Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True, read_at=timezone.now())

        return Response(
            {"message": f"{updated_count} notification(s) marked as read.", "count": updated_count},
            status=status.HTTP_200_OK,
        )


class NotificationUnreadCountView(APIView):
    """Return number of unread notifications for current user."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({"unread_count": count})
