from celery import shared_task
from celery.utils.log import get_task_logger

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
        task_logger.info("Success expire order %s", order_id)
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
