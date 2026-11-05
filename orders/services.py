from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from orders.exceptions import (
    AdvanceNotPaidException,
    AdvanceReturnException,
    LateCancelOrderException,
    NoAdvancePaidDateException,
)
from orders.models import Order
from payments.models import Payment
from reservations.services import (
    change_stocks_expired_quantity,
    get_order_and_order_item_obj,
    get_product_stocks,
)


def cancel_confirmed_order(order_id: int):
    with transaction.atomic():
        order_obj, order_obj_items = get_order_and_order_item_obj(
            order_id,
            "cancel"
        )
        payment_obj = get_payment_obj(order_obj)
        _, stocks_by_product_id = get_product_stocks(order_obj, order_obj_items)

        change_stocks_expired_quantity(order_obj_items, stocks_by_product_id)
        order_obj.status = Order.Status.CANCELLED
        order_obj.save()

        payment_obj.advance_refunded = True
        payment_obj.advance_refunded_at = timezone.now()
        payment_obj.save()


def get_payment_obj(order_obj: Order) -> Payment:
    try:
        payment_obj = Payment.objects.select_for_update().get(order=order_obj)
    except Payment.DoesNotExist:
        raise Payment.DoesNotExist("Payment not found")

    if not payment_obj.advance_paid:
        raise AdvanceNotPaidException(order_obj.id)

    if not payment_obj.advance_paid_at:
        raise NoAdvancePaidDateException(order_obj.id)

    if payment_obj.advance_refunded:
        raise AdvanceReturnException(order_obj.id)

    if timezone.now() > payment_obj.advance_paid_at + timedelta(hours=24):
        raise LateCancelOrderException(order_obj.id)

    return payment_obj
