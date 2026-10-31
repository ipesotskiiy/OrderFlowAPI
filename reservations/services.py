from django.db import transaction
from django.db.models import F

from orders.models import Order, OrderItem
from payments.services import create_payment
from reservations.exceptions import (
    EmptyOrderException,
    InsufficientStockException,
    InvalidOrderStatusException,
    StockNotFoundException,
)
from reservations.models import ReservationFailure
from stocks.models import Stock


def reserve_order(order_id: int) -> None:
    try:
        with transaction.atomic():
            order_obj, order_obj_items = get_order_and_order_item_obj(order_id)
            stocks_by_product_id = get_product_stocks(order_obj, order_obj_items)
            check_stock_and_available_quantity(order_obj_items, stocks_by_product_id)
            change_stocks_reserved_quantity(order_obj_items, stocks_by_product_id)
            order_obj.status = Order.Status.RESERVED
            order_obj.save()
            create_payment(order_id)
    except (InsufficientStockException, StockNotFoundException) as error:
        if isinstance(error, InsufficientStockException):
            reason = ReservationFailure.ReasonFailure.INSUFFICIENT_STOCK
        elif isinstance(error, StockNotFoundException):
            reason = ReservationFailure.ReasonFailure.STOCK_NOT_FOUND

        ReservationFailure.objects.create(
            order=order_obj,
            reason=reason
        )
        raise


def get_order_and_order_item_obj(
        order_id: int,
) -> tuple[Order, list[OrderItem]]:
    try:
        order_obj = Order.objects.select_for_update().get(id=order_id)
    except Order.DoesNotExist:
        raise Order.DoesNotExist("Order not found")

    if order_obj.status != Order.Status.DRAFT:
        raise InvalidOrderStatusException()

    order_obj_items = list(OrderItem.objects.filter(order_id=order_id))
    if not order_obj_items:
        raise EmptyOrderException()
    return order_obj, order_obj_items


def get_product_stocks(
    order_obj: Order,
    order_obj_items: list[OrderItem],
) -> dict[int, Stock]:
    product_ids = [item.product_id for item in order_obj_items]
    stocks_for_order = list(
        Stock.objects
        .filter(
            warehouse_id=order_obj.warehouse_id,
            product_id__in=product_ids,
        )
        .order_by("id")
        .select_for_update()
    )

    stocks_by_product_id = {
        stock.product_id: stock
        for stock in stocks_for_order
    }
    return stocks_by_product_id

def check_stock_and_available_quantity(
    order_obj_items: list[OrderItem],
    stocks_by_product_id: dict[int, Stock],
) -> None:
    for order_item in order_obj_items:
        stock = stocks_by_product_id.get(order_item.product_id)
        if stock is None:
            raise StockNotFoundException(order_item.id)

        if stock.available_quantity < order_item.quantity:
            raise InsufficientStockException(stock, order_item)

def change_stocks_reserved_quantity(
    order_obj_items: list[OrderItem],
    stocks_by_product_id: dict[int, Stock],
) -> None:
    for order_item in order_obj_items:
        stock = stocks_by_product_id.get(order_item.product_id)
        stock.reserved_quantity = F("reserved_quantity") + order_item.quantity
        stock.save()
