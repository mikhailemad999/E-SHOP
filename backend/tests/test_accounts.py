"""
Tests for Accounts and Authentication module.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class AccountsApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.buyer = User.objects.create_user(
            username="testbuyer",
            email="buyer@test.com",
            password="StrongPassword123!",
            role=User.Role.CUSTOMER,
            first_name="Test",
            last_name="Buyer",
        )
        self.seller = User.objects.create_user(
            username="testseller",
            email="seller@test.com",
            password="StrongPassword123!",
            role=User.Role.SELLER,
            first_name="Test",
            last_name="Seller",
        )

    def test_customer_login_success(self):
        """Verify JWT login returns access and refresh tokens."""
        response = self.client.post(
            "/api/auth/login/",
            {"username": "testbuyer", "password": "StrongPassword123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["role"], "CUSTOMER")

    def test_customer_registration(self):
        """Verify new buyer can self-register."""
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "newbuyer99",
                "email": "newbuyer99@test.com",
                "password": "BuyerPassword123!",
                "role": "CUSTOMER",
                "first_name": "New",
                "last_name": "User",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newbuyer99").exists())

    def test_authenticated_user_profile(self):
        """Verify authenticated user can retrieve and update profile."""
        self.client.force_authenticate(user=self.buyer)
        response = self.client.get("/api/users/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "buyer@test.com")

        update_resp = self.client.patch(
            "/api/users/me/",
            {"phone": "+201009998888"},
            format="json",
        )
        self.assertEqual(update_resp.status_code, status.HTTP_200_OK)
        self.buyer.refresh_from_db()
        self.assertEqual(self.buyer.phone, "+201009998888")
