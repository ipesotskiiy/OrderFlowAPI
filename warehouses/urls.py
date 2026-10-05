from django.urls import include, path
from rest_framework.routers import DefaultRouter

from warehouses.views import WarehouseManagerAssignmentViewSet, WarehouseViewSet

router = DefaultRouter()
router.register("warehouses/assignments", WarehouseManagerAssignmentViewSet)
router.register("warehouses", WarehouseViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

