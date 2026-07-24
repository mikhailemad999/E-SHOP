"""
Catalog models — Buy-Box pattern with canonical Product + per-seller Listing.

Key architecture (from spec §5.3):
- Product = canonical catalog entry (title, category, shared attributes)
- Listing = one seller's offer (price, stock, condition, images, variants)
- Multiple sellers can attach Listings to the same Product
- Product detail page shows a "buy-box" (best listing) + all other sellers
"""

from django.conf import settings
from django.db import models

try:
    if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql":
        from django.contrib.postgres.search import SearchVectorField
    else:
        SearchVectorField = models.TextField
except Exception:
    SearchVectorField = models.TextField


class Category(models.Model):
    """
    Self-referential category tree (unlimited depth).
    E.g., Electronics → Phones → Smartphones
    """

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "categories"
        verbose_name_plural = "Categories"
        ordering = ["sort_order", "name"]

    def __str__(self):
        if self.parent:
            return f"{self.parent} → {self.name}"
        return self.name

    @property
    def full_path(self):
        """Return the full category path, e.g. 'Electronics / Phones / Smartphones'."""
        parts = [self.name]
        current = self.parent
        while current:
            parts.insert(0, current.name)
            current = current.parent
        return " / ".join(parts)


class Shop(models.Model):
    """
    Seller's storefront. A seller creates one shop.
    """

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shop",
        limit_choices_to={"role": "SELLER"},
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    logo = models.ImageField(upload_to="shops/logos/", blank=True, null=True)
    banner = models.ImageField(upload_to="shops/banners/", blank=True, null=True)
    description = models.TextField(blank=True)
    categories = models.ManyToManyField(Category, blank=True, related_name="shops")
    is_active = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_sales = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "shops"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class SellerFollow(models.Model):
    """Customer follows a shop — powers the 'shops I follow' feed."""

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following_shops",
        limit_choices_to={"role": "CUSTOMER"},
    )
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="followers",
    )
    followed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "seller_follows"
        unique_together = ["customer", "shop"]

    def __str__(self):
        return f"{self.customer.email} → {self.shop.name}"


class Product(models.Model):
    """
    Canonical catalog entry — shared across sellers.
    Contains the product's identity (title, category, base attributes).
    Individual sellers attach Listings with their price/stock/images.
    """

    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, unique=True)
    description = models.TextField()
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="products",
    )
    brand = models.CharField(max_length=200, blank=True)
    base_attributes = models.JSONField(
        default=dict,
        blank=True,
        help_text="Shared attributes like weight, dimensions, material, etc.",
    )
    # Full-text search vector (auto-populated via trigger or save)
    search_vector = SearchVectorField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["brand"]),
        ]

    def __str__(self):
        return self.title

    @property
    def avg_price(self):
        """Average price across all live listings."""
        listings = self.listings.filter(status="live")
        if listings.exists():
            return listings.aggregate(avg=models.Avg("price"))["avg"]
        return None

    @property
    def lowest_price(self):
        """Lowest price across all live listings (buy-box candidate)."""
        if hasattr(self, "_lowest_price"):
            return self._lowest_price
        listing = self.listings.filter(status="live").order_by("price").first()
        return listing.price if listing else None

    @lowest_price.setter
    def lowest_price(self, value):
        self._lowest_price = value

    @property
    def total_stock(self):
        """Total stock across all live listings."""
        return (
            self.listings.filter(status="live").aggregate(
                total=models.Sum("stock_qty")
            )["total"]
            or 0
        )


class Listing(models.Model):
    """
    One seller's offer on a Product — price, stock, condition, images.
    Multiple sellers can have Listings against the same Product.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_REVIEW = "pending_review", "Pending Review"
        LIVE = "live", "Live"
        REJECTED = "rejected", "Rejected"
        OUT_OF_STOCK = "out_of_stock", "Out of Stock"
        ARCHIVED = "archived", "Archived"

    class Condition(models.TextChoices):
        NEW = "new", "New"
        REFURBISHED = "refurbished", "Refurbished"
        USED_GOOD = "used_good", "Used — Good"
        USED_FAIR = "used_fair", "Used — Fair"

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="listings",
    )
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="listings",
    )
    price = models.DecimalField(max_digits=12, decimal_places=2)
    compare_at_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="Original price for showing discounts",
    )
    stock_qty = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, blank=True)
    condition = models.CharField(
        max_length=20,
        choices=Condition.choices,
        default=Condition.NEW,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING_REVIEW,
        db_index=True,
    )
    variant_attributes = models.JSONField(
        default=dict,
        blank=True,
        help_text="Seller-specific attributes: size, color, etc.",
    )
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    review_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "listings"
        ordering = ["price"]
        indexes = [
            models.Index(fields=["product", "shop"]),
            models.Index(fields=["status", "stock_qty"]),
            models.Index(fields=["shop", "status"]),
            models.Index(fields=["price"]),
        ]

    def __str__(self):
        return f"{self.product.title} by {self.shop.name} — ${self.price}"

    @property
    def is_in_stock(self):
        return self.stock_qty > 0

    @property
    def discount_percentage(self):
        if self.compare_at_price and self.compare_at_price > self.price:
            return round(
                (1 - self.price / self.compare_at_price) * 100
            )
        return 0

    def save(self, *args, **kwargs):
        # Auto-update status based on stock
        if self.stock_qty == 0 and self.status == self.Status.LIVE:
            self.status = self.Status.OUT_OF_STOCK
        elif self.stock_qty > 0 and self.status == self.Status.OUT_OF_STOCK:
            self.status = self.Status.LIVE
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    """Multiple images per listing, with sort ordering."""

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "product_images"
        ordering = ["sort_order"]

    def __str__(self):
        return f"Image for {self.listing} (#{self.sort_order})"
