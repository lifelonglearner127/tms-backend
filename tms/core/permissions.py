from rest_framework import permissions
from . import constants as c


class IsStaffUser(permissions.BasePermission):
    """
    Permission to only allow admin and staff roles
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS or
            request.user.role in [c.USER_ROLE_STAFF, c.USER_ROLE_ADMIN]
        )


class IsDriverOrEscortUser(permissions.BasePermission):
    """
    Permission to only allow admin and staff roles
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            c.USER_ROLE_DRIVER, c.USER_ROLE_ESCORT
        ]

    def has_object_permission(self, request, view, obj):
        return obj.driver == request.user
