from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction
from django.utils import timezone

from orders.models import Order, OrderItem
from payments.exceptions import (
    DoubleAdvancePaidException,
    InvalidOrderStatusForPaymentException,
    OrderHasPaymentException,
    PaymentPartException,
)
from payments.models import Payment


def create_payment(order_id: int):
    order_obj = get_order_obj(order_id)
    check_order_obj_payment(order_obj)
    _, advance, remaining = calculate_payment(order_id)
    Payment.objects.create(
        order=order_obj,
        advance_amount=advance,
        remaining_amount=remaining,
    )


def calculate_payment(order_id: int):
    order_obj_items = get_order_item_obj(order_id)
    full_sum, advance, remaining = calculate_payments_parts(order_obj_items)
    return full_sum, advance, remaining


def get_order_obj(order_id: int) -> Order:
    try:
        order_obj = Order.objects.select_for_update().get(id=order_id)
    except Order.DoesNotExist:
        raise Order.DoesNotExist("Order not found")

    if order_obj.status != Order.Status.RESERVED:
        raise InvalidOrderStatusForPaymentException()
    return order_obj


def check_order_obj_payment(order_obj: Order) -> None:
    if Payment.objects.filter(order=order_obj).exists():
        raise OrderHasPaymentException(order_obj.id)


def get_order_item_obj(
    order_id: int,
) ->  list[OrderItem]:
    order_obj_items = list(OrderItem.objects.filter(order_id=order_id))
    return order_obj_items


def calculate_payments_parts(
    order_obj_items: list[OrderItem],
) -> tuple[Decimal, Decimal, Decimal]:
    full_sum = Decimal("0")
    for item in order_obj_items:
        full_sum += item.quantity * item.unit_price

    advance = full_sum * Decimal("0.2")
    advance = advance.quantize(Decimal("1.00"), ROUND_HALF_UP)
    remaining = full_sum - advance
    remaining = remaining.quantize(Decimal("1.00"), ROUND_HALF_UP)
    check_payments_parts(full_sum, advance, remaining)
    return full_sum, advance, remaining

def check_payments_parts(
    full_sum: Decimal,
    advance: Decimal,
    remaining: Decimal,
) -> None:
    for payment_part in (full_sum, advance, remaining):
        if payment_part <= 0:
            raise PaymentPartException(full_sum, advance, remaining)


def confirm_receipt_advance_payment(
    order_id: int,
)-> None:
    with transaction.atomic():
        order_obj = get_order_obj(order_id)
        payment_obj = get_order_payment_obj(order_obj)
        change_payment_advance(payment_obj)
        order_obj.status = Order.Status.CONFIRMED
        order_obj.save()


def get_order_payment_obj(order_obj: Order) -> Payment:
    try:
        payment_obj = Payment.objects.select_for_update().get(order=order_obj)
    except Payment.DoesNotExist:
        raise Payment.DoesNotExist("Payment not found")

    if payment_obj.advance_paid:
        raise DoubleAdvancePaidException()

    return payment_obj


def change_payment_advance(payment_obj: Payment) -> None:
    payment_obj.advance_paid = True
    payment_obj.advance_paid_at = timezone.now()
    payment_obj.save()

