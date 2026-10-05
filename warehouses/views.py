from rest_framework import viewsets
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.permissions import IsAdminUser

from warehouses.models import Warehouse, WarehouseManagerAssignment
from warehouses.permissions import IsAdminOrWarehouseManagerReadOnly
from warehouses.serializers import (
    WarehouseManagerAssignmentSerializer,
    WarehouseSerializer,
)


# Create your views here.
class WarehouseViewSet(viewsets.ModelViewSet):
    serializer_class = WarehouseSerializer
    queryset = Warehouse.objects.all()
    permission_classes = (IsAdminOrWarehouseManagerReadOnly,)
    http_method_names = [
        "get",
        "post",
        "patch",
        "delete",
        "head",
        "options",
    ]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Warehouse.objects.all()
        return Warehouse.objects.filter(
            manager_assignments__user=self.request.user
        )


class WarehouseManagerAssignmentViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = WarehouseManagerAssignmentSerializer
    queryset = WarehouseManagerAssignment.objects.all()
    permission_classes = (IsAdminUser,)
