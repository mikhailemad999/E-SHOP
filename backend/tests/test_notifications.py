"""
Tests for Notifications module — In-app alerts, unread counts, mark-as-read.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.notifications.models import Notification

User = get_user_model()


class NotificationsApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="notif_user",
            email="notif@test.com",
            password="Password123!",
            role=User.Role.CUSTOMER,
        )
        self.n1 = Notification.objects.create(
            user=self.user,
            type=Notification.Type.ORDER_PLACED,
            title="Order Placed",
            message="Your order #ORD-12345678 is placed.",
            is_read=False,
        )
        self.n2 = Notification.objects.create(
            user=self.user,
            type=Notification.Type.SHIPMENT_UPDATE,
            title="Shipment Dispatched",
            message="Your package is out for delivery.",
            is_read=False,
        )

    def test_list_notifications_and_unread_count(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/notifications/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 2)

        count_resp = self.client.get("/api/notifications/unread-count/")
        self.assertEqual(count_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(count_resp.data["unread_count"], 2)

    def test_mark_single_notification_read(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(f"/api/notifications/{self.n1.id}/read/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_read"])

        self.n1.refresh_from_db()
        self.assertTrue(self.n1.is_read)
        self.assertIsNotNone(self.n1.read_at)

    def test_mark_all_notifications_read(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/notifications/read-all/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        count_resp = self.client.get("/api/notifications/unread-count/")
        self.assertEqual(count_resp.data["unread_count"], 0)
