from rest_framework import permissions
from .constants import USER_ROLE_STAFF, USER_ROLE_ADMIN


class IsAccountStaffOrReadOnly(permissions.BasePermission):
    """
    Permission to only allow admin and staff roles
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS or
            request.user.role in [USER_ROLE_STAFF, USER_ROLE_ADMIN]
        )
