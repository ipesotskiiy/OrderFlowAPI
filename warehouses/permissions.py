from rest_framework import permissions

from warehouses.models import WarehouseManagerAssignment


class IsAdminOrWarehouseManagerReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if not request.user.is_staff:
            count_user_warehouse = WarehouseManagerAssignment.objects.filter(
                user=request.user
            ).exists()
            if count_user_warehouse and request.method in permissions.SAFE_METHODS:
                return True
            elif not count_user_warehouse:
                return False
        return bool(request.user.is_staff)
