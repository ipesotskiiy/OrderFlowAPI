from celery import shared_task
from celery.utils.log import get_task_logger

task_logger = get_task_logger(__name__)

@shared_task
def get_order_log(order_id: int) -> None:
    task_logger.info("Processing order %s", order_id)
