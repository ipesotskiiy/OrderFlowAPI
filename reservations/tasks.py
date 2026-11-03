from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone

from orders.models import Order
from reservations.exceptions import (
    EmptyDatetimeConfirmAdvance,
    EmptyOrderException,
    InvalidOrderStatusExpireException,
    InvalidTimeExpireOrderException,
    ReservedQuantityLowerOrderItemQuantityException,
    StockNotFoundException,
)
from reservations.services import change_order_to_expired

task_logger = get_task_logger(__name__)

@shared_task
def get_order_log(order_id: int) -> None:
    task_logger.info("Processing order %s", order_id)


@shared_task
def expire_order(order_id: int) -> None:
    try:
        change_order_to_expired(order_id)
        task_logger.info(
            "Finished processing order expiration %s",
            order_id,
        )
    except (
            InvalidOrderStatusExpireException,
            EmptyDatetimeConfirmAdvance,
            InvalidTimeExpireOrderException,
            EmptyOrderException,
            StockNotFoundException,
            ReservedQuantityLowerOrderItemQuantityException,
    ) as error:
        task_logger.error(
            "Exception in expire order %s process. Error: %s",
            order_id,
            error,
        )
        raise


@shared_task
def check_order_to_expire() -> None:
    task_logger.info(
        "Start process expire orders"
    )
    orders_ids_to_expire =Order.objects.filter(
        status=Order.Status.RESERVED,
        datetime_confirm_advance__lte=timezone.now(),
    ).values_list("id", flat=True)
    task_logger.info(
        "Count orders to expire %s",
        len(orders_ids_to_expire)
    )
    published_order_tasks_count = 0
    for order_id in orders_ids_to_expire:
        task_logger.info("Processing order %s", order_id)
        expire_order.delay(order_id)
        task_logger.info("Processing order %s completed", order_id)
        published_order_tasks_count += 1

    task_logger.info(
        "Published %s expiration tasks",
        published_order_tasks_count,
    )
    task_logger.info(
        "Completed process expire orders"
    )

