"""
Tests for Storefront, Seller Follows, and RMA Return/Refund Workflow.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.catalog.models import Category, Listing, Product, Shop
from apps.notifications.models import Notification
from apps.orders.models import Order, ReturnRequest, SubOrder, SubOrderItem

User = get_user_model()


class StorefrontAndReturnsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Users
        self.seller = User.objects.create_user(
            username="seller_boutique",
            email="seller_boutique@eshop.dev",
            password="Password123!",
            role=User.Role.SELLER,
        )
        self.customer = User.objects.create_user(
            username="buyer_vip",
            email="buyer_vip@eshop.dev",
            password="Password123!",
            role=User.Role.CUSTOMER,
        )
        self.admin = User.objects.create_user(
            username="admin_ops",
            email="admin_ops@eshop.dev",
            password="Password123!",
            role=User.Role.ADMIN,
        )

        # Shop & Catalog
        self.shop = Shop.objects.create(
            owner=self.seller,
            name="Parisian Boutique",
            slug="parisian-boutique",
            description="Luxury curated apparel and accessories.",
        )
        self.category = Category.objects.create(name="Luxury Fashion", slug="luxury-fashion")
        self.product = Product.objects.create(
            title="Cashmere Trench Coat",
            slug="cashmere-trench-coat",
            category=self.category,
            brand="Atelier Lux",
        )
        self.listing = Listing.objects.create(
            product=self.product,
            shop=self.shop,
            price=850.00,
            stock_qty=10,
            status=Listing.Status.LIVE,
        )

        # Delivered Order for Return testing
        self.order = Order.objects.create(
            customer=self.customer,
            order_number="ORD-TEST-RET01",
            payment_method=Order.PaymentMethod.CARD,
            total_amount=850.00,
            shipping_address={"city": "Cairo", "country": "EG"},
            status=Order.Status.DELIVERED,
        )
        self.suborder = SubOrder.objects.create(
            order=self.order,
            shop=self.shop,
            subtotal=850.00,
            status=SubOrder.Status.DELIVERED,
        )
        self.suborder_item = SubOrderItem.objects.create(
            suborder=self.suborder,
            listing=self.listing,
            quantity=1,
            unit_price=850.00,
        )

    def test_shop_detail_storefront(self):
        """Verify public shop detail returns seller profile and active listings."""
        response = self.client.get(f"/api/shops/{self.shop.slug}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Parisian Boutique")
        self.assertIn("listings", response.data)
        self.assertEqual(len(response.data["listings"]), 1)
        self.assertEqual(response.data["listings"][0]["product_title"], "Cashmere Trench Coat")

    def test_follow_and_unfollow_shop(self):
        """Verify customer can follow and unfollow a seller shop."""
        self.client.force_authenticate(user=self.customer)

        # 1. Follow shop
        res_follow = self.client.post(f"/api/shops/{self.shop.slug}/follow/")
        self.assertEqual(res_follow.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res_follow.data["is_following"])

        # 2. Verify in followed shops list
        res_list = self.client.get("/api/shops/following/mine/")
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_list.data["results"] if "results" in res_list.data else res_list.data), 1)

        # 3. Unfollow shop
        res_unfollow = self.client.post(f"/api/shops/{self.shop.slug}/follow/")
        self.assertEqual(res_unfollow.status_code, status.HTTP_200_OK)
        self.assertFalse(res_unfollow.data["is_following"])

    def test_return_request_lifecycle(self):
        """Verify RMA Return lifecycle: Customer request -> Seller views -> Seller approves -> Customer notified."""
        # 1. Customer creates return request
        self.client.force_authenticate(user=self.customer)
        res_create = self.client.post("/api/returns/", {
            "suborder_item": self.suborder_item.id,
            "reason": "Size too large, need smaller fit.",
        })
        self.assertEqual(res_create.status_code, status.HTTP_201_CREATED)
        return_id = res_create.data["id"]
        self.assertEqual(res_create.data["status"], "requested")
        self.assertEqual(res_create.data["shop_name"], "Parisian Boutique")

        # 2. Seller views their returns
        self.client.force_authenticate(user=self.seller)
        res_seller = self.client.get("/api/returns/seller/")
        self.assertEqual(res_seller.status_code, status.HTTP_200_OK)
        returns = res_seller.data["results"] if "results" in res_seller.data else res_seller.data
        self.assertEqual(len(returns), 1)
        self.assertEqual(returns[0]["id"], return_id)

        # 3. Seller approves the return
        res_action = self.client.post(f"/api/returns/{return_id}/action/", {
            "status": "approved",
            "admin_notes": "Return approved. Please ship item back using provided label.",
        })
        self.assertEqual(res_action.status_code, status.HTTP_200_OK)
        self.assertEqual(res_action.data["return"]["status"], "approved")

        # 4. Verify notification sent to customer
        notif = Notification.objects.filter(user=self.customer, type=Notification.Type.RETURN_UPDATE).first()
        self.assertIsNotNone(notif)
        self.assertIn("Approved", notif.title)
