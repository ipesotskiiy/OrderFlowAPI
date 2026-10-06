from rest_framework import permissions

from warehouses.models import WarehouseManagerAssignment


class IsAdminOrStockWarehouseManagerReadAndUpdate(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if not request.user.is_staff:
            has_warehouse_assignment = WarehouseManagerAssignment.objects.filter(
                user=request.user
            ).exists()
            if has_warehouse_assignment and request.method in (
                    "GET",
                    "HEAD",
                    "OPTIONS",
                    "PATCH"
            ):
                return True
            elif not has_warehouse_assignment:
                return False
        return bool(request.user.is_staff)
