from django.urls import path
from apps.catalog.views import CatalogSearchView

urlpatterns = [
    path("", CatalogSearchView.as_view(), name="catalog-search"),
]
