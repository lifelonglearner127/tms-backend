from rest_framework import permissions


class IsMyNotification(permissions.BasePermission):
    """
    Permission to only allow admin and staff roles
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user
