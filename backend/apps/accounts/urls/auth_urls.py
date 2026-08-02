"""Auth URLs — login, register, refresh, logout."""

from django.urls import path

from apps.accounts.views import (
    CustomerRegistrationView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    SellerRegistrationView,
    UniversalRegistrationView,
)

urlpatterns = [
    path("register/", UniversalRegistrationView.as_view(), name="register-universal"),
    path("register/customer/", CustomerRegistrationView.as_view(), name="register-customer"),
    path("register/seller/", SellerRegistrationView.as_view(), name="register-seller"),
    path("login/", CustomTokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
