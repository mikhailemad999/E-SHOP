"""
Catalog serializers — Category tree, Shop, canonical Product, and seller Listing (Buy-Box pattern).
"""

from rest_framework import serializers
from .models import Category, Listing, Product, ProductImage, SellerFollow, Shop


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer with optional nested children for category tree."""

    children = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Category
        fields = [
            "id", "name", "slug", "parent", "image",
            "description", "is_active", "sort_order",
            "full_path", "children", "created_at",
        ]

    def get_children(self, obj):
        if hasattr(obj, "children") and obj.children.exists():
            return CategorySerializer(obj.children.filter(is_active=True), many=True).data
        return []


class ShopSerializer(serializers.ModelSerializer):
    """Shop storefront serializer."""

    owner_email = serializers.EmailField(source="owner.email", read_only=True)
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = [
            "id", "owner", "owner_email", "name", "slug", "logo",
            "banner", "description", "categories", "is_active",
            "rating", "total_sales", "is_following", "created_at",
        ]
        read_only_fields = ["id", "owner", "rating", "total_sales", "created_at"]

    def get_is_following(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated and request.user.role == "CUSTOMER":
            return SellerFollow.objects.filter(customer=request.user, shop=obj).exists()
        return False


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "sort_order"]

    def get_image(self, obj):
        if not obj.image:
            return None
        img_str = str(obj.image)
        if img_str.startswith("http://") or img_str.startswith("https://"):
            return img_str
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


class ListingSerializer(serializers.ModelSerializer):
    """
    Seller offer serializer with images and shop metadata.
    """

    shop_name = serializers.CharField(source="shop.name", read_only=True)
    shop_logo = serializers.ImageField(source="shop.logo", read_only=True)
    shop_rating = serializers.DecimalField(source="shop.rating", max_digits=3, decimal_places=2, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = Listing
        fields = [
            "id", "product", "shop", "shop_name", "shop_logo", "shop_rating",
            "price", "compare_at_price", "discount_percentage",
            "stock_qty", "is_in_stock", "sku", "condition", "status",
            "variant_attributes", "rating", "review_count", "images",
            "uploaded_images", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "shop", "rating", "review_count", "created_at", "updated_at"]

    def create(self, validated_data):
        uploaded_images = validated_data.pop("uploaded_images", [])
        request = self.context.get("request")
        if request and hasattr(request.user, "shop"):
            validated_data["shop"] = request.user.shop
        listing = Listing.objects.create(**validated_data)

        for i, img in enumerate(uploaded_images):
            ProductImage.objects.create(listing=listing, image=img, sort_order=i)

        return listing


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Buy-Box Product detail:
    Includes canonical info + best (lowest price live) listing as buy_box + all other live listings.
    """

    category_name = serializers.CharField(source="category.name", read_only=True)
    category_path = serializers.CharField(source="category.full_path", read_only=True)
    buy_box = serializers.SerializerMethodField()
    other_sellers = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "title", "slug", "description", "category",
            "category_name", "category_path", "brand", "base_attributes",
            "is_active", "lowest_price", "avg_price", "total_stock",
            "buy_box", "other_sellers", "created_at",
        ]

    def get_buy_box(self, obj):
        best_listing = obj.listings.filter(status="live", stock_qty__gt=0).order_by("price").first()
        if best_listing:
            return ListingSerializer(best_listing, context=self.context).data
        return None

    def get_other_sellers(self, obj):
        listings = obj.listings.filter(status="live", stock_qty__gt=0).order_by("price")[1:]
        return ListingSerializer(listings, many=True, context=self.context).data


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight product list serializer for search and homepage grids."""

    category_name = serializers.CharField(source="category.name", read_only=True)
    lowest_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_listings = serializers.IntegerField(read_only=True)
    featured_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "title", "slug", "category", "category_name",
            "brand", "lowest_price", "total_listings", "featured_image",
        ]

    def get_featured_image(self, obj):
        first_listing = obj.listings.filter(status="live").first()
        if first_listing and first_listing.images.exists():
            image = first_listing.images.first()
            img_url = str(image.image)
            if img_url.startswith("http://") or img_url.startswith("https://"):
                return img_url
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(image.image.url)
            return image.image.url
        return None
