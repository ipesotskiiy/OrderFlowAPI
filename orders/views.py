from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from orders.exceptions import (
    AdvanceNotPaidException,
    AdvanceReturnException,
    InvalidOrderStatusCancelException,
    LateCancelOrderException,
    NoAdvancePaidDateException,
)
from orders.models import Order
from orders.serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderUpdateSerializer,
)
from orders.services import cancel_confirmed_order
from payments.exceptions import (
    ConfirmationTimeExpiredException,
    DoubleAdvancePaidException,
    InvalidOrderStatusForPaymentException,
)
from payments.models import Payment
from payments.services import confirm_receipt_advance_payment
from reservations.exceptions import (
    EmptyDatetimeConfirmAdvance,
    EmptyOrderException,
    InsufficientStockException,
    InvalidOrderStatusReserveException,
    ReservedQuantityLowerOrderItemQuantityException,
    StockNotFoundException,
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
        if self.action == "cancel_order":
            return Order.objects.filter(
                customer=self.request.user
            ).prefetch_related(
                "order_items"
            )
        else:
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
            InvalidOrderStatusReserveException,
            EmptyOrderException,
        ) as error:
            return Response(
                error.message,
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        methods=["post"],
        detail=True,
        url_path="confirm_advance",
        permission_classes=[IsAdminUser],
    )
    def confirm_advance(self, request, pk):
        try:
            order_obj = self.get_object()
            confirm_receipt_advance_payment(order_obj.id)
            return Response(
                "Payment advance successfully confirmed",
                status=status.HTTP_200_OK,
            )
        except (
            InvalidOrderStatusForPaymentException,
            DoubleAdvancePaidException,
            Payment.DoesNotExist,
            ConfirmationTimeExpiredException,
            EmptyDatetimeConfirmAdvance,
        ) as error:
            return Response(
                str(error),
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        methods=["post"],
        detail=True,
        url_path="cancel",
    )
    def cancel_order(self, request, pk):
        try:
            order_obj = self.get_object()
            cancel_confirmed_order(order_obj.id)
            return Response(
                "Order successfully cancelled",
                status=status.HTTP_200_OK,
            )
        except (
            InvalidOrderStatusCancelException,
            AdvanceNotPaidException,
            NoAdvancePaidDateException,
            LateCancelOrderException,
            StockNotFoundException,
            ReservedQuantityLowerOrderItemQuantityException,
            AdvanceReturnException,
            EmptyOrderException,
        ) as error:
            return Response(
                str(error),
                status=status.HTTP_400_BAD_REQUEST,
            )
