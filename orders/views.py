from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet

from orders.models import Order
from orders.serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderUpdateSerializer,
)


# Create your views here.
class OrderViewSet(
    CreateModelMixin,
    ListModelMixin,
    UpdateModelMixin,
    RetrieveModelMixin,
    GenericViewSet
):
    serializer_class = OrderCreateSerializer
    queryset = Order.objects.all()
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ("status", "warehouse")
    ordering_fields = ("created_at",)
    ordering = ("-created_at",)
    http_method_names = [
        "get",
        "post",
        "patch",
        "head",
        "options",
    ]

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return OrderSerializer
        elif self.action == "partial_update":
            return OrderUpdateSerializer
        return OrderCreateSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.prefetch_related("order_items").all()
        return Order.objects.filter(
            customer=self.request.user
        ).prefetch_related(
            "order_items"
        )

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

