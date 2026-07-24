"""
E-Shop Marketplace — Root URL Configuration.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse, JsonResponse
from django.urls import include, path


def api_root_view(request):
    """API Root endpoint returning available services and documentation links."""
    return JsonResponse(
        {
            "name": "E-Shop Multi-Vendor Marketplace API",
            "status": "online",
            "database": "MySQL 5.7 (E_shop)",
            "documentation": "http://localhost:5173",
            "admin": "http://localhost:8000/admin/",
            "endpoints": {
                "auth": "/api/auth/",
                "users": "/api/users/",
                "shops": "/api/shops/",
                "categories": "/api/categories/",
                "products": "/api/products/",
                "listings": "/api/listings/",
                "search": "/api/search/",
                "cart": "/api/cart/",
                "checkout": "/api/checkout/",
                "orders": "/api/orders/",
                "suborders": "/api/suborders/",
                "returns": "/api/returns/",
                "payments": "/api/payments/",
                "delivery": "/api/delivery/",
                "reviews": "/api/listings/",
                "favorites": "/api/favorites/",
                "notifications": "/api/notifications/",
                "stats": "/api/stats/",
            },
        }
    )


def favicon_view(request):
    """Empty favicon handler returning 204 No Content to avoid 404 browser errors."""
    return HttpResponse(status=204)


urlpatterns = [
    # Root & API Welcome handlers
    path("", api_root_view, name="root_welcome"),
    path("api/", api_root_view, name="api_root"),
    path("favicon.ico", favicon_view, name="favicon"),
    # Django admin
    path("admin/", admin.site.urls),
    # API endpoints
    path("api/auth/", include("apps.accounts.urls.auth_urls")),
    path("api/users/", include("apps.accounts.urls.user_urls")),
    path("api/shops/", include("apps.catalog.urls.shop_urls")),
    path("api/categories/", include("apps.catalog.urls.category_urls")),
    path("api/products/", include("apps.catalog.urls.product_urls")),
    path("api/listings/", include("apps.catalog.urls.listing_urls")),
    path("api/search/", include("apps.catalog.urls.search_urls")),
    path("api/cart/", include("apps.orders.urls.cart_urls")),
    path("api/checkout/", include("apps.orders.urls.checkout_urls")),
    path("api/orders/", include("apps.orders.urls.order_urls")),
    path("api/suborders/", include("apps.orders.urls.suborder_urls")),
    path("api/returns/", include("apps.orders.urls.return_urls")),
    path("api/payments/", include("apps.payments.urls")),
    path("api/delivery/", include("apps.shipping.urls")),
    path("api/listings/", include("apps.reviews.urls.review_urls")),
    path("api/favorites/", include("apps.reviews.urls.favorite_urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    path("api/stats/", include("apps.analytics.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Debug toolbar
    try:
        import debug_toolbar
        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass
