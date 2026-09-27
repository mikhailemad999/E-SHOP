"""
Catalog views — Categories, Products (Buy-Box), Listings, Shop Storefront, Search, and Moderation.
"""

try:
    from django.contrib.postgres.search import SearchRank, SearchQuery, SearchVector
except ImportError:
    SearchRank = SearchQuery = SearchVector = None
from django.db.models import Count, Min, Q
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from apps.accounts.permissions import IsAdmin, IsSeller, IsSellerOwner
from .models import Category, Listing, Product, SellerFollow, Shop
from .serializers import (
    CategorySerializer,
    ListingSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ShopSerializer,
)


# ─── Category Views ───────────────────────────────────────────────
class CategoryListView(generics.ListAPIView):
    """List root categories with nested children tree."""

    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Category.objects.filter(parent=None, is_active=True).prefetch_related("children")


class CategoryDetailView(generics.RetrieveAPIView):
    """Category detail with info and subcategories."""

    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"


# ─── Product Views ────────────────────────────────────────────────
class ProductDetailView(generics.RetrieveAPIView):
    """
    Buy-Box Product detail endpoint.
    Returns canonical info + buy_box (best seller offer) + other_sellers.
    """

    queryset = Product.objects.filter(is_active=True).prefetch_related("listings__images", "listings__shop")
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"


class ProductCreateView(generics.CreateAPIView):
    """Sellers or Admins create canonical Product entries."""

    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    permission_classes = [IsSeller | IsAdmin]


# ─── Listing Views ────────────────────────────────────────────────
class ListingCreateView(generics.CreateAPIView):
    """Seller creates a new offer/listing on a Product."""

    serializer_class = ListingSerializer
    permission_classes = [IsSeller]

    def perform_create(self, serializer):
        serializer.save(shop=self.request.user.shop, status=Listing.Status.PENDING_REVIEW)


class SellerListingsView(generics.ListAPIView):
    """Seller views all their own listings across all statuses."""

    serializer_class = ListingSerializer
    permission_classes = [IsSeller]

    def get_queryset(self):
        if hasattr(self.request.user, "shop"):
            return Listing.objects.filter(shop=self.request.user.shop).select_related("product").prefetch_related("images")
        return Listing.objects.none()


class ListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Seller updates or archives their own listing."""

    serializer_class = ListingSerializer
    permission_classes = [IsSellerOwner]
    queryset = Listing.objects.all()


# ─── Admin Moderation Views ───────────────────────────────────────
class ModerationQueueView(generics.ListAPIView):
    """Admin queue for pending_review listings."""

    serializer_class = ListingSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return Listing.objects.filter(status=Listing.Status.PENDING_REVIEW).select_related("product", "shop")


class ModerateListingView(APIView):
    """Admin approves or rejects a seller listing."""

    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            listing = Listing.objects.get(pk=pk)
        except Listing.DoesNotExist:
            return Response({"error": "Listing not found."}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get("action")  # 'approve' or 'reject'
        reason = request.data.get("reason", "")

        if action == "approve":
            listing.status = Listing.Status.LIVE
            listing.save()
            return Response({"message": f"Listing #{pk} approved and live."})
        elif action == "reject":
            listing.status = Listing.Status.REJECTED
            listing.save()
            return Response({"message": f"Listing #{pk} rejected.", "reason": reason})
        else:
            return Response({"error": "Invalid action. Use 'approve' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)


# ─── Search & Catalog Grid View ───────────────────────────────────
class CatalogSearchView(generics.ListAPIView):
    """
    Search and faceted product search view.
    Faceted by category, brand, price range, and full-text search vector.
    """

    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["category__slug", "brand"]
    ordering_fields = ["created_at", "lowest_price"]

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).annotate(
            lowest_price=Min("listings__price", filter=Q(listings__status="live", listings__stock_qty__gt=0)),
            total_listings=Count("listings", filter=Q(listings__status="live")),
        ).filter(total_listings__gt=0)

        # Full-text query
        q = self.request.query_params.get("q")
        if q:
            from django.db import connection
            if connection.vendor == "postgresql":
                vector = SearchVector("title", weight="A") + SearchVector("description", weight="B") + SearchVector("brand", weight="A")
                query = SearchQuery(q)
                qs = qs.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.01).order_by("-rank")
            else:
                qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(brand__icontains=q))

        # Min/Max price filter
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        if min_price:
            qs = qs.filter(lowest_price__gte=min_price)
        if max_price:
            qs = qs.filter(lowest_price__lte=max_price)

        return qs.select_related("category").prefetch_related("listings__images").order_by("-created_at")


# ─── Shop Views ───────────────────────────────────────────────────
class ShopDetailView(generics.RetrieveAPIView):
    """Public shop storefront detail."""

    queryset = Shop.objects.filter(is_active=True)
    serializer_class = ShopSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"


class SellerFollowToggleView(APIView):
    """Customer follows or unfollows a shop."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        if request.user.role != "CUSTOMER":
            return Response({"error": "Only customers can follow shops."}, status=status.HTTP_403_FORBIDDEN)

        try:
            shop = Shop.objects.get(slug=slug, is_active=True)
        except Shop.DoesNotExist:
            return Response({"error": "Shop not found."}, status=status.HTTP_404_NOT_FOUND)

        follow, created = SellerFollow.objects.get_or_create(customer=request.user, shop=shop)
        if not created:
            follow.delete()
            return Response({"message": f"Unfollowed {shop.name}.", "is_following": False})
        return Response({"message": f"Now following {shop.name}.", "is_following": True}, status=status.HTTP_201_CREATED)


class SellerAddProductListingView(APIView):
    """
    Seller endpoint to add a new product offer to their shop.
    Creates Product (if needed), Listing, and ProductImage directly in MySQL database.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from decimal import Decimal
        from django.utils.text import slugify

        title = request.data.get("title")
        category_id = request.data.get("category_id")
        price = request.data.get("price")
        compare_at_price = request.data.get("compare_at_price")
        stock_qty = request.data.get("stock_qty", 20)
        brand = request.data.get("brand", "Generic")
        image_url = request.data.get("image_url", "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800")
        sku = request.data.get("sku")

        if not title or not price:
            return Response({"error": "Title and Price are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create shop for user
        shop, _ = Shop.objects.get_or_create(
            owner=request.user,
            defaults={"name": f"{request.user.username}'s Store", "slug": slugify(f"{request.user.username}-store")}
        )

        category = Category.objects.filter(id=category_id).first() if category_id else Category.objects.first()

        # Get or create Product
        slug = slugify(title)
        product, _ = Product.objects.get_or_create(
            slug=slug,
            defaults={
                "title": title,
                "category": category,
                "brand": brand,
                "description": f"Premium {title}. Guaranteed high quality and fast shipping.",
            }
        )

        dec_price = Decimal(str(price))
        dec_compare = Decimal(str(compare_at_price)) if compare_at_price else dec_price * Decimal("1.25")

        # Create Listing
        listing = Listing.objects.create(
            product=product,
            shop=shop,
            price=dec_price,
            compare_at_price=dec_compare,
            stock_qty=int(stock_qty),
            status=Listing.Status.LIVE,
            sku=sku or f"SKU-{product.id}-{shop.id}",
        )

        if image_url:
            ProductImage.objects.create(
                listing=listing,
                image=image_url,
                alt_text=title,
                sort_order=0,
            )

        return Response({
            "message": "Product listing created successfully!",
            "listing_id": listing.id,
            "product_title": product.title,
            "price": str(listing.price),
        }, status=status.HTTP_201_CREATED)
