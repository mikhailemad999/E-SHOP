from django.urls import path
from apps.catalog.views import ProductCreateView, ProductDetailView

urlpatterns = [
    path("create/", ProductCreateView.as_view(), name="product-create"),
    path("<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
]
