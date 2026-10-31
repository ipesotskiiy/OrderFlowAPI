from django.db import models
from django.db.models.constraints import CheckConstraint
from django.db.models.query_utils import Q

from orders.models import Order


# Create your models here.
class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    advance_amount = models.DecimalField(
        verbose_name="Order advance amount",
        max_digits=12,
        decimal_places=2,
    )
    advance_paid = models.BooleanField(
        verbose_name="Order is advance amount paid?",
        default=False,
    )
    advance_paid_at = models.DateTimeField(
        verbose_name="Date paid advance amount",
        null=True,
        blank=True,
    )
    remaining_amount = models.DecimalField(
        verbose_name="Order remaining amount",
        max_digits=14,
        decimal_places=2,
    )
    remaining_paid = models.BooleanField(
        verbose_name="Order is remaining amount paid?",
        default=False,
    )
    remaining_paid_at = models.DateTimeField(
        verbose_name="Date paid remaining amount",
        null=True,
        blank=True,
    )
    advance_refunded = models.BooleanField(
        verbose_name="Advance is return?",
        default=False,
    )
    advance_refunded_at = models.DateTimeField(
        verbose_name="Date return advance",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        constraints = [
            CheckConstraint(
                condition=Q(advance_amount__gt=0),
                name="positive_advance_amount",
            ),
            CheckConstraint(
                condition=Q(remaining_amount__gt=0),
                name="positive_remaining_amount",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.order.id} | {self.advance_amount} | {self.remaining_amount}"
