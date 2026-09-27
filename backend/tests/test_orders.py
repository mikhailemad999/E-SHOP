"""
Tests for Orders module — Cart, Atomic Multi-Vendor Checkout, SubOrder split, Stock management.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.catalog.models import Category, Listing, Product, Shop
from apps.orders.models import Cart, CartItem, Order, SubOrder

User = get_user_model()


class OrdersApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.buyer = User.objects.create_user(
            username="ordertestbuyer",
            email="orderbuyer@test.com",
            password="Password123!",
            role=User.Role.CUSTOMER,
        )
        self.seller1 = User.objects.create_user(
            username="seller_one",
            email="seller1@test.com",
            password="Password123!",
            role=User.Role.SELLER,
        )
        self.seller2 = User.objects.create_user(
            username="seller_two",
            email="seller2@test.com",
            password="Password123!",
            role=User.Role.SELLER,
        )
        self.shop1 = Shop.objects.create(owner=self.seller1, name="Shop Alpha", slug="shop-alpha")
        self.shop2 = Shop.objects.create(owner=self.seller2, name="Shop Beta", slug="shop-beta")

        self.category = Category.objects.create(name="Gadgets", slug="gadgets")

        self.prod1 = Product.objects.create(title="Gadget A", slug="gadget-a", category=self.category)
        self.listing1 = Listing.objects.create(
            product=self.prod1, shop=self.shop1, price=50.00, stock_qty=10, status=Listing.Status.LIVE
        )

        self.prod2 = Product.objects.create(title="Gadget B", slug="gadget-b", category=self.category)
        self.listing2 = Listing.objects.create(
            product=self.prod2, shop=self.shop2, price=75.00, stock_qty=5, status=Listing.Status.LIVE
        )

    def test_multi_vendor_atomic_checkout(self):
        """
        Verify single checkout containing 2 different sellers:
        1. Creates 1 parent Order
        2. Creates 2 SubOrders (one per seller)
        3. Correctly decrements stock for each Listing
        4. Empties the Cart
        """
        self.client.force_authenticate(user=self.buyer)

        cart = Cart.objects.create(customer=self.buyer)
        CartItem.objects.create(cart=cart, listing=self.listing1, quantity=2)
        CartItem.objects.create(cart=cart, listing=self.listing2, quantity=1)

        payload = {
            "payment_method": "cod",
            "shipping_address": {
                "full_name": "Test Recipient",
                "phone": "+201011223344",
                "address_line1": "123 Nile Road",
                "city": "Cairo",
                "state": "Cairo",
                "postal_code": "11511",
                "country": "EG",
            },
            "notes": "Please leave at front desk.",
        }

        response = self.client.post("/api/checkout/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        order_data = response.data["order"]
        self.assertEqual(float(order_data["total_amount"]), 175.00)  # (50*2) + (75*1)

        # Verify parent Order in DB
        parent_order = Order.objects.get(order_number=order_data["order_number"])
        self.assertEqual(parent_order.customer, self.buyer)

        # Verify 2 SubOrders created
        suborders = SubOrder.objects.filter(order=parent_order)
        self.assertEqual(suborders.count(), 2)

        # Verify Stock Decrement
        self.listing1.refresh_from_db()
        self.assertEqual(self.listing1.stock_qty, 8)  # 10 - 2

        self.listing2.refresh_from_db()
        self.assertEqual(self.listing2.stock_qty, 4)  # 5 - 1

        # Verify Cart is now empty
        self.assertEqual(cart.items.count(), 0)

    def test_customer_orders_list(self):
        """Verify customer can view their order history."""
        self.client.force_authenticate(user=self.buyer)
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
