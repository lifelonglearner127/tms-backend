from rest_framework import permissions
from ..core import constants as c


class IsMyJob(permissions.BasePermission):
    """
    Permission to only allow admin and staff roles
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in [
            c.USER_TYPE_DRIVER, c.USER_TYPE_ESCORT
        ]

    def has_object_permission(self, request, view, obj):
        return obj.job.driver == request.user
