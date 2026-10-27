from django.db import models

from orders.models import Order


# Create your models here.
class ReservationFailure(models.Model):
    class ReasonFailure(models.TextChoices):
        INSUFFICIENT_STOCK = "insufficient_stock"
        STOCK_NOT_FOUND = "stock_not_found"
        ORDER_INVALID_STATUS = "order_invalid_status"

    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
    )
    reason = models.CharField(
        verbose_name="Reasons to reservation fail",
        max_length=25,
        choices=ReasonFailure.choices
    )
    created_at = models.DateTimeField(
        verbose_name="Reservation failure create",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Reservation failure"
        verbose_name_plural = "Reservations failures"

    def __str__(self) -> str:
        return f"{self.id} | {self.reason}"
