from rest_framework import permissions


class IsAdminOrIsAuthenticatedReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS and request.user.is_authenticated:
            return True
        return bool(request.user and request.user.is_staff)
