from django.conf import settings
from django.db import models
from django.db.models import CheckConstraint, Q, UniqueConstraint

from catalog.models import Product
from warehouses.models import Warehouse


# Create your models here.
class Order(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft"
        RESERVED = "reserved"
        CONFIRMED = "confirmed"
        CANCELLED = "cancelled"
        EXPIRED = "expired"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="customer_orders",
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="warehouse_orders",
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    created_at = models.DateTimeField(verbose_name="Order created", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Order updated", auto_now=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self) -> str:
        return f"{self.customer.email} | {self.warehouse.name} | {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="order_items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="product_order_items",
    )
    quantity = models.PositiveIntegerField(verbose_name="Quantity product in order")
    unit_price = models.DecimalField(
        verbose_name="Unit price in order",
        max_digits=12,
        decimal_places=2,
    )
    created_at = models.DateTimeField(
        verbose_name="Order item created",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        verbose_name="Order item updated",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Order item"
        verbose_name_plural = "Order items"

        constraints = [
            CheckConstraint(
                condition=Q(quantity__gt=0),
                name="quantity_gt_0",
                violation_error_message="Quantity must be greater than 0",
            ),
            UniqueConstraint(
                fields=["order", "product"],
                name="unique_order_item_order_and_product",
                violation_error_message=(
                    "This product is already assigned to this order."
                )
            )
        ]

    def __str__(self) -> str:
        return f"{self.product.name}-{self.quantity}-{self.unit_price}"
