"""
Tests for Catalog module — Buy-Box pattern, Category hierarchy, Listing selection.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.catalog.models import Category, Listing, Product, Shop

User = get_user_model()


class CatalogApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.seller = User.objects.create_user(
            username="seller_audio",
            email="seller_audio@test.com",
            password="Password123!",
            role=User.Role.SELLER,
        )
        self.shop = Shop.objects.create(
            owner=self.seller,
            name="Audio Excellence",
            slug="audio-excellence",
        )
        self.category = Category.objects.create(
            name="Audio & Headphones",
            slug="audio-headphones",
        )
        self.product = Product.objects.create(
            title="Premium Studio Headphones X100",
            slug="premium-studio-headphones-x100",
            category=self.category,
            brand="SoundPro",
            description="Professional studio monitor headphones with active noise cancellation.",
        )
        self.listing = Listing.objects.create(
            product=self.product,
            shop=self.shop,
            price=199.99,
            compare_at_price=249.99,
            stock_qty=25,
            condition=Listing.Condition.NEW,
            status=Listing.Status.LIVE,
        )

    def test_product_detail_endpoint(self):
        """Verify product detail returns canonical info and buy_box."""
        response = self.client.get(f"/api/products/{self.product.slug}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Premium Studio Headphones X100")
        self.assertIsNotNone(response.data.get("buy_box"))
        self.assertEqual(float(response.data["buy_box"]["price"]), 199.99)

    def test_search_endpoint(self):
        """Verify search finds products by keyword."""
        response = self.client.get("/api/search/?q=Headphones")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        self.assertTrue(len(results) >= 1)

    def test_shop_follow_toggle(self):
        """Verify authenticated customer can follow and unfollow a shop."""
        customer = User.objects.create_user(
            username="follower_customer",
            email="follower@test.com",
            password="Password123!",
            role=User.Role.CUSTOMER,
        )
        self.client.force_authenticate(user=customer)
        response = self.client.post(f"/api/shops/{self.shop.slug}/follow/")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["is_following"])

        # Unfollow
        unfollow_resp = self.client.post(f"/api/shops/{self.shop.slug}/follow/")
        self.assertEqual(unfollow_resp.status_code, status.HTTP_200_OK)
        self.assertFalse(unfollow_resp.data["is_following"])
