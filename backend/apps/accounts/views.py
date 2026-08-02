"""
Accounts views — registration, profile, and admin-created accounts.
"""

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from rest_framework.views import APIView

from .models import Address, DeliveryAgentProfile, DeliveryManagerProfile, SellerProfile
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


class UniversalRegistrationView(APIView):
    """
    Universal Registration View — allows self-registering as Customer, Seller,
    Delivery Manager, Delivery Agent, Admin, or Super Admin.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        role_str = (data.get("role") or "customer").lower()
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        phone = data.get("phone", "")

        if not username or not email or not password:
            return Response(
                {"error": "Username, email, and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response({"username": ["Username already taken."]}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"email": ["Email already registered."]}, status=status.HTTP_400_BAD_REQUEST)

        role_map = {
            "customer": User.Role.CUSTOMER,
            "buyer": User.Role.CUSTOMER,
            "seller": User.Role.SELLER,
            "delivery_manager": User.Role.DELIVERY_MANAGER,
            "delivery_agent": User.Role.DELIVERY_AGENT,
            "admin": User.Role.ADMIN,
            "super_admin": User.Role.SUPER_ADMIN,
        }
        target_role = role_map.get(role_str, User.Role.CUSTOMER)

        is_staff = target_role in [User.Role.ADMIN, User.Role.SUPER_ADMIN]
        is_superuser = target_role == User.Role.SUPER_ADMIN

        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=target_role,
            is_staff=is_staff,
            is_superuser=is_superuser,
        )
        user.set_password(password)
        user.save()

        if target_role == User.Role.SELLER:
            from apps.catalog.models import Shop
            from django.utils.text import slugify
            b_name = data.get("business_name") or f"{user.username}'s Store"
            SellerProfile.objects.get_or_create(user=user, defaults={"business_name": b_name})
            Shop.objects.get_or_create(owner=user, defaults={"name": b_name, "slug": slugify(b_name), "description": f"Official store for {b_name}"})

        elif target_role == User.Role.DELIVERY_MANAGER:
            DeliveryManagerProfile.objects.get_or_create(user=user, defaults={"zone": data.get("zone", "Zone 1")})

        elif target_role == User.Role.DELIVERY_AGENT:
            DeliveryAgentProfile.objects.get_or_create(user=user, defaults={"vehicle_type": "motorcycle", "license_plate": "PLATE-DEV"})

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
