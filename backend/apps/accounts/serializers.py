"""
Accounts serializers — registration, login, profile management.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Address, DeliveryAgentProfile, DeliveryManagerProfile, SellerProfile

User = get_user_model()


# ─── JWT Custom Token ───────────────────────────────────────────
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Include role in the JWT token payload so the frontend knows which dashboard to show."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["email"] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["role"] = self.user.role
        data["email"] = self.user.email
        data["user_id"] = self.user.id
        return data


# ─── Registration ────────────────────────────────────────────────
class CustomerRegistrationSerializer(serializers.ModelSerializer):
    """Self-service registration for customers."""

    password = serializers.CharField(
        write_only=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email", "username", "first_name", "last_name",
            "phone", "password", "password_confirm",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            phone=validated_data.get("phone", ""),
            password=validated_data["password"],
            role=User.Role.CUSTOMER,
        )
        return user


class SellerRegistrationSerializer(serializers.ModelSerializer):
    """Self-service registration for sellers — creates user + seller profile."""

    password = serializers.CharField(
        write_only=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True)
    business_name = serializers.CharField(max_length=255, required=False, default="")

    class Meta:
        model = User
        fields = [
            "email", "username", "first_name", "last_name",
            "phone", "password", "password_confirm", "business_name",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        business_name = validated_data.pop("business_name", "")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            phone=validated_data.get("phone", ""),
            password=validated_data["password"],
            role=User.Role.SELLER,
        )
        SellerProfile.objects.create(user=user, business_name=business_name)
        return user


class AdminCreationSerializer(serializers.ModelSerializer):
    """Super Admin creates an Admin account."""

    password = serializers.CharField(
        write_only=True, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ["email", "username", "first_name", "last_name", "phone", "password"]

    def create(self, validated_data):
        return User.objects.create_user(
            **validated_data,
            role=User.Role.ADMIN,
        )


class DeliveryManagerCreationSerializer(serializers.ModelSerializer):
    """Super Admin creates a Delivery Manager account."""

    password = serializers.CharField(
        write_only=True, validators=[validate_password]
    )
    zone = serializers.CharField(max_length=100, required=False, default="")

    class Meta:
        model = User
        fields = ["email", "username", "first_name", "last_name", "phone", "password", "zone"]

    def create(self, validated_data):
        zone = validated_data.pop("zone", "")
        user = User.objects.create_user(
            **validated_data,
            role=User.Role.DELIVERY_MANAGER,
        )
        DeliveryManagerProfile.objects.create(user=user, zone=zone)
        return user


class DeliveryAgentCreationSerializer(serializers.ModelSerializer):
    """Delivery Manager creates a Delivery Agent account."""

    password = serializers.CharField(
        write_only=True, validators=[validate_password]
    )
    vehicle_type = serializers.CharField(max_length=50, required=False, default="")

    class Meta:
        model = User
        fields = [
            "email", "username", "first_name", "last_name",
            "phone", "password", "vehicle_type",
        ]

    def create(self, validated_data):
        vehicle_type = validated_data.pop("vehicle_type", "")
        manager = self.context["request"].user
        user = User.objects.create_user(
            **validated_data,
            role=User.Role.DELIVERY_AGENT,
        )
        DeliveryAgentProfile.objects.create(
            user=user, delivery_manager=manager, vehicle_type=vehicle_type
        )
        return user


# ─── Profile / User Detail ──────────────────────────────────────
class UserProfileSerializer(serializers.ModelSerializer):
    """Read/update current user's profile."""

    class Meta:
        model = User
        fields = [
            "id", "email", "username", "first_name", "last_name",
            "phone", "avatar", "role", "is_email_verified",
            "is_phone_verified", "created_at",
        ]
        read_only_fields = ["id", "email", "role", "created_at"]


class AddressSerializer(serializers.ModelSerializer):
    """Customer address CRUD."""

    class Meta:
        model = Address
        fields = [
            "id", "label", "full_name", "phone", "address_line1",
            "address_line2", "city", "state", "postal_code",
            "country", "is_default", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
