"""
Celery background task for async bulk product import from CSV/XLSX.
"""

import csv
import io
from celery import shared_task
from django.utils.text import slugify
from .models import Category, Listing, Product, Shop


@shared_task
def bulk_import_products_task(shop_id, file_content_str, file_type="csv"):
    """
    Async Celery task to import product listings from CSV data.
    Expected CSV columns:
    title, category_name, brand, description, price, stock_qty, condition, sku
    """
    try:
        shop = Shop.objects.get(id=shop_id)
    except Shop.DoesNotExist:
        return {"status": "error", "message": "Shop not found"}

    imported_count = 0
    errors = []

    f = io.StringIO(file_content_str)
    reader = csv.DictReader(f)

    for row in reader:
        try:
            title = row.get("title", "").strip()
            category_name = row.get("category_name", "General").strip()
            brand = row.get("brand", "").strip()
            description = row.get("description", "").strip()
            price = float(row.get("price", 0))
            stock_qty = int(row.get("stock_qty", 0))
            condition = row.get("condition", "new").strip().lower()
            sku = row.get("sku", "").strip()

            if not title or price <= 0:
                continue

            # Category
            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={"slug": slugify(category_name)}
            )

            # Canonical Product
            product_slug = slugify(title)
            product, _ = Product.objects.get_or_create(
                slug=product_slug,
                defaults={
                    "title": title,
                    "category": category,
                    "brand": brand,
                    "description": description,
                }
            )

            # Seller Listing
            Listing.objects.create(
                product=product,
                shop=shop,
                price=price,
                stock_qty=stock_qty,
                condition=condition,
                sku=sku,
                status=Listing.Status.LIVE,
            )

            imported_count += 1
        except Exception as e:
            errors.append(f"Row {title}: {str(e)}")

    return {
        "status": "completed",
        "imported_count": imported_count,
        "errors": errors,
    }
