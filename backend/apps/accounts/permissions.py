"""
Permission classes — role-based AND object-level checks.

Each class checks the user's `role` field. Object-level permissions
(e.g., a seller can only edit their own listings) are handled in
views or via IsOwner-style mixins.
"""

from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    """Only Super Admins can access."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "SUPER_ADMIN"
        )


class IsAdmin(BasePermission):
    """Admins and Super Admins can access."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ("ADMIN", "SUPER_ADMIN")
        )


class IsSeller(BasePermission):
    """Only Sellers can access."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "SELLER"
        )


class IsDeliveryManager(BasePermission):
    """Only Delivery Managers can access."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "DELIVERY_MANAGER"
        )


class IsDeliveryAgent(BasePermission):
    """Only Delivery Agents can access."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "DELIVERY_AGENT"
        )


class IsCustomer(BasePermission):
    """Only Customers can access."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "CUSTOMER"
        )


class IsAdminOrSuperAdmin(BasePermission):
    """Admin or Super Admin access."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ("ADMIN", "SUPER_ADMIN")
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level: the requesting user must be the owner of the object,
    or an Admin/Super Admin. Views must implement `get_owner_field()`
    or the object must have a `user` or `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.role in ("ADMIN", "SUPER_ADMIN"):
            return True
        # Check common owner patterns
        if hasattr(obj, "user"):
            return obj.user == request.user
        if hasattr(obj, "owner"):
            return obj.owner == request.user
        if hasattr(obj, "customer"):
            return obj.customer == request.user
        return False


class IsSellerOwner(BasePermission):
    """
    Object-level: the requesting seller must own the shop
    that the object belongs to.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.role in ("ADMIN", "SUPER_ADMIN"):
            return True
        if not request.user.role == "SELLER":
            return False
        # Check if obj has a shop with this seller as owner
        if hasattr(obj, "shop"):
            return obj.shop.owner == request.user
        if hasattr(obj, "listing") and hasattr(obj.listing, "shop"):
            return obj.listing.shop.owner == request.user
        return False
