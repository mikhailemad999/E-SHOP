from django.contrib import admin

from .models import Address, DeliveryAgentProfile, DeliveryManagerProfile, SellerProfile, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "username", "role", "is_active", "created_at"]
    list_filter = ["role", "is_active", "is_email_verified"]
    search_fields = ["email", "username", "first_name", "last_name"]
    ordering = ["-created_at"]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["user", "label", "city", "is_default"]
    list_filter = ["is_default"]


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "business_name", "is_verified"]


@admin.register(DeliveryAgentProfile)
class DeliveryAgentProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "delivery_manager", "is_available", "is_on_shift"]


@admin.register(DeliveryManagerProfile)
class DeliveryManagerProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "zone", "max_agents"]
