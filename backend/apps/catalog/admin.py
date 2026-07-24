from django.contrib import admin
from .models import Category, Listing, Product, ProductImage, SellerFollow, Shop

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent", "is_active", "sort_order"]
    list_filter = ["is_active"]
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "is_active", "rating", "total_sales"]
    list_filter = ["is_active"]
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "brand", "is_active"]
    list_filter = ["is_active", "category"]
    prepopulated_fields = {"slug": ("title",)}

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ["product", "shop", "price", "stock_qty", "status", "condition"]
    list_filter = ["status", "condition"]

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ["listing", "sort_order"]

@admin.register(SellerFollow)
class SellerFollowAdmin(admin.ModelAdmin):
    list_display = ["customer", "shop", "followed_at"]
