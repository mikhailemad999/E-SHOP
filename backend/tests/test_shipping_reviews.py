"""
Tests for Shipping and Reviews/Wishlist modules.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.catalog.models import Category, Listing, Product, Shop
from apps.reviews.models import Favorite
from apps.shipping.models import DeliveryAssignment

User = get_user_model()


class ShippingAndReviewsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.agent = User.objects.create_user(
            username="delivery_agent_1",
            email="agent1@test.com",
            password="Password123!",
            role=User.Role.DELIVERY_AGENT,
        )
        self.customer = User.objects.create_user(
            username="shopper_1",
            email="shopper1@test.com",
            password="Password123!",
            role=User.Role.CUSTOMER,
        )
        self.seller = User.objects.create_user(
            username="shopowner_1",
            email="owner1@test.com",
            password="Password123!",
            role=User.Role.SELLER,
        )
        self.shop = Shop.objects.create(owner=self.seller, name="FastTech", slug="fasttech")
        self.category = Category.objects.create(name="Accessories", slug="accessories")
        self.prod = Product.objects.create(title="USB-C Hub", slug="usb-c-hub", category=self.category)
        self.listing = Listing.objects.create(
            product=self.prod, shop=self.shop, price=29.99, stock_qty=50, status=Listing.Status.LIVE
        )
        self.assignment = DeliveryAssignment.objects.create(
            agent=self.agent,
            tracking_number="TRK-UNITTEST001",
            status=DeliveryAssignment.Status.ASSIGNED,
        )

    def test_delivery_agent_queue_and_status_update(self):
        """Verify delivery agent can view queue and advance delivery status."""
        self.client.force_authenticate(user=self.agent)
        response = self.client.get("/api/delivery/agent/queue/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        update_resp = self.client.post(
            f"/api/delivery/assignments/{self.assignment.tracking_number}/status/",
            {"status": "in_transit"},
            format="json",
        )
        self.assertEqual(update_resp.status_code, status.HTTP_200_OK)
        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.status, DeliveryAssignment.Status.IN_TRANSIT)

    def test_customer_public_tracking_endpoint(self):
        """Verify tracking endpoint resolves without requiring login."""
        response = self.client.get(f"/api/delivery/tracking/{self.assignment.tracking_number}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["tracking_number"], self.assignment.tracking_number)

    def test_favorite_wishlist_toggle(self):
        """Verify customer can add and remove listing from favorites."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(f"/api/favorites/{self.listing.id}/toggle/")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["is_favorite"])
        self.assertTrue(Favorite.objects.filter(customer=self.customer, listing=self.listing).exists())

        # Check customer favorites list
        list_resp = self.client.get("/api/favorites/")
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)
        results = list_resp.data.get("results", list_resp.data)
        self.assertEqual(len(results), 1)

        # Toggle off
        toggle_off = self.client.post(f"/api/favorites/{self.listing.id}/toggle/")
        self.assertEqual(toggle_off.status_code, status.HTTP_200_OK)
        self.assertFalse(toggle_off.data["is_favorite"])
