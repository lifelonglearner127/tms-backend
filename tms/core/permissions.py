from rest_framework import permissions
from . import constants as c


class IsStaffUser(permissions.BasePermission):
    """
    Permission to only allow admin and staff user_types
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS or
            request.user.user_type in [c.USER_TYPE_STAFF, c.USER_TYPE_ADMIN]
        )


class IsDriverOrEscortUser(permissions.BasePermission):
    """
    Permission to only allow admin and staff user_types
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in [
            c.USER_TYPE_DRIVER, c.USER_TYPE_ESCORT
        ]

    def has_object_permission(self, request, view, obj):
        return request.user in obj.associated_drivers.all() or request.user in obj.associated_escorts.all()


class IsCustomerUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in [
            c.USER_TYPE_CUSTOMER
        ]


class OrderPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.user_type in [c.USER_TYPE_STAFF, c.USER_TYPE_ADMIN]:
            return True

        if request.user.user_type == c.USER_TYPE_CUSTOMER:
            if obj.customer == request.user.customer_profile:
                return True

        return False


class TMSStaffPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == c.USER_TYPE_ADMIN or\
            request.user.user_type == c.USER_TYPE_STAFF and request.user.permission.has_permission(
                page=view.page_name, action=view.action
            )
