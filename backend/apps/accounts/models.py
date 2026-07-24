"""
Accounts models — User with role-based access + per-role profile tables.

Architecture decision:
- Single User table with a `role` field for DRF permission classes.
- One-to-one profile tables per role for role-specific fields.
- This avoids multi-table inheritance complexity while keeping
  role-specific data cleanly separated.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model with role-based access control.
    Roles determine which dashboard a user sees and which
    API endpoints they can access.
    """

    class Role(models.TextChoices):
        CUSTOMER = "CUSTOMER", "Customer"
        SELLER = "SELLER", "Seller"
        DELIVERY_AGENT = "DELIVERY_AGENT", "Delivery Agent"
        DELIVERY_MANAGER = "DELIVERY_MANAGER", "Delivery Manager"
        ADMIN = "ADMIN", "Admin"
        SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
        db_index=True,
    )
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    @property
    def is_seller(self):
        return self.role == self.Role.SELLER

    @property
    def is_delivery_agent(self):
        return self.role == self.Role.DELIVERY_AGENT

    @property
    def is_delivery_manager(self):
        return self.role == self.Role.DELIVERY_MANAGER

    @property
    def is_admin_user(self):
        return self.role in (self.Role.ADMIN, self.Role.SUPER_ADMIN)

    @property
    def is_super_admin(self):
        return self.role == self.Role.SUPER_ADMIN


class Address(models.Model):
    """Customer shipping addresses. A customer can store multiple."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    label = models.CharField(max_length=50, default="Home")  # Home, Work, etc.
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="US")
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "addresses"
        verbose_name_plural = "Addresses"
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.label}: {self.address_line1}, {self.city}"

    def save(self, *args, **kwargs):
        # If this is set as default, unset other defaults for this user
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(
                is_default=False
            )
        super().save(*args, **kwargs)


class SellerProfile(models.Model):
    """Extended profile for sellers. Created when a seller registers."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="seller_profile",
    )
    business_name = models.CharField(max_length=255, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    bank_account = models.CharField(max_length=50, blank=True)
    payout_email = models.EmailField(blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "seller_profiles"

    def __str__(self):
        return f"Seller: {self.user.email}"


class DeliveryAgentProfile(models.Model):
    """Extended profile for delivery agents. Created by Delivery Manager."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="delivery_agent_profile",
    )
    delivery_manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="managed_agents",
        limit_choices_to={"role": User.Role.DELIVERY_MANAGER},
    )
    vehicle_type = models.CharField(max_length=50, blank=True)  # motorcycle, car, bicycle
    license_plate = models.CharField(max_length=20, blank=True)
    current_lat = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    current_lng = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    is_available = models.BooleanField(default=True)
    is_on_shift = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "delivery_agent_profiles"

    def __str__(self):
        return f"Agent: {self.user.email}"


class DeliveryManagerProfile(models.Model):
    """Extended profile for delivery managers. Created by Super Admin."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="delivery_manager_profile",
    )
    zone = models.CharField(max_length=100, blank=True)  # Geographic zone
    max_agents = models.PositiveIntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "delivery_manager_profiles"

    def __str__(self):
        return f"Manager: {self.user.email}"
