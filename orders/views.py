from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from orders.models import Order
from orders.serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderUpdateSerializer,
)
from reservations.exceptions import (
    InsufficientStockException,
    StockNotFoundException,
    InvalidOrderStatusException,
    EmptyOrderException,
)
from reservations.services import reserve_order


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

    @action(methods=["post"], detail=True, url_path="reserve")
    def reserve(self, request, pk):
        try:
            order_obj = self.get_object()
            reserve_order(order_obj.id)
            return Response(
                "Order successfully reserved",
                status=status.HTTP_200_OK,
        )
        except (
            InsufficientStockException,
            StockNotFoundException,
            InvalidOrderStatusException,
            EmptyOrderException,
        ) as error:
            return Response(
                error.message,
                status=status.HTTP_400_BAD_REQUEST,
            )
