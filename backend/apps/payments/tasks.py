"""
Celery background tasks for payouts and payment processing.
"""

from celery import shared_task
from django.utils import timezone
from apps.orders.models import SubOrder
from .models import SellerPayout


@shared_task
def process_delivered_suborder_payouts():
    """
    Nightly Celery Beat task:
    Finds all delivered SubOrders that haven't been paid out yet,
    calculates platform commission (10%), and creates SellerPayout records.
    """
    delivered_suborders = SubOrder.objects.filter(
        status=SubOrder.Status.DELIVERED
    ).exclude(payouts__isnull=False)

    created_count = 0
    for suborder in delivered_suborders:
        platform_fee = suborder.subtotal * Decimal("0.10")  # 10% platform fee
        payout_amount = suborder.subtotal - platform_fee

        SellerPayout.objects.create(
            shop=suborder.shop,
            suborder=suborder,
            amount=payout_amount,
            platform_fee=platform_fee,
            status=SellerPayout.Status.COMPLETED,
            paid_at=timezone.now(),
        )
        created_count += 1

    return f"Processed {created_count} seller payouts."
