"""
Accounts views — registration, profile, and admin-created accounts.
"""

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import Address
from .permissions import IsCustomer, IsDeliveryManager, IsSuperAdmin
from .serializers import (
    AddressSerializer,
    AdminCreationSerializer,
    CustomerRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    DeliveryAgentCreationSerializer,
    DeliveryManagerCreationSerializer,
    SellerRegistrationSerializer,
    UserProfileSerializer,
)

User = get_user_model()


# ─── Authentication ──────────────────────────────────────────────
class CustomTokenObtainPairView(TokenObtainPairView):
    """Login — returns access + refresh tokens with role info."""
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    """Refresh — exchange refresh token for a new access token."""
    pass


class LogoutView(generics.GenericAPIView):
    """Logout — blacklist the refresh token."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Successfully logged out."},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"error": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


# ─── Self-Service Registration ───────────────────────────────────
class CustomerRegistrationView(generics.CreateAPIView):
    """Register a new customer account."""

    serializer_class = CustomerRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Generate tokens for immediate login
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "Account created successfully.",
                "user": UserProfileSerializer(user).data,
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class SellerRegistrationView(generics.CreateAPIView):
    """Register a new seller account + seller profile."""

    serializer_class = SellerRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "Seller account created successfully.",
                "user": UserProfileSerializer(user).data,
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_201_CREATED,
        )


# ─── Admin-Created Accounts ─────────────────────────────────────
class CreateAdminView(generics.CreateAPIView):
    """Super Admin creates an Admin account."""

    serializer_class = AdminCreationSerializer
    permission_classes = [IsSuperAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "Admin account created.",
                "user": UserProfileSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class CreateDeliveryManagerView(generics.CreateAPIView):
    """Super Admin creates a Delivery Manager account."""

    serializer_class = DeliveryManagerCreationSerializer
    permission_classes = [IsSuperAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "Delivery Manager account created.",
                "user": UserProfileSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class CreateDeliveryAgentView(generics.CreateAPIView):
    """Delivery Manager creates a Delivery Agent account."""

    serializer_class = DeliveryAgentCreationSerializer
    permission_classes = [IsDeliveryManager]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "Delivery Agent account created.",
                "user": UserProfileSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


# ─── Profile ────────────────────────────────────────────────────
class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get/update current user's profile."""

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# ─── Addresses ───────────────────────────────────────────────────
class AddressListCreateView(generics.ListCreateAPIView):
    """List and create customer addresses."""

    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a customer address."""

    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
