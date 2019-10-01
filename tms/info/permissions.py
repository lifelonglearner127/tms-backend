from rest_framework import permissions
from ..core import constants as c


class ProductViewSetPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.user_type in [c.USER_TYPE_ADMIN, c.USER_TYPE_CUSTOMER]:
            return True

        if request.user.user_type == c.USER_TYPE_STAFF:
            if request.user.permission.has_permission(
                page='settings', action=view.action
            ):
                return True

            if request.user.permission.has_permission(page='orders', action='create'):
                return True

        return False
