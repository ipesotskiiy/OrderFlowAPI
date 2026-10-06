from django.db import models
from django.db.models import Q, F
from django.db.models.constraints import UniqueConstraint, CheckConstraint

from catalog.models import Product
from warehouses.models import Warehouse


# Create your models here.
class Stock(models.Model):
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="stock_items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="stock_items"
    )
    quantity = models.PositiveIntegerField(
        verbose_name="Stock quantity product in warehouse"
    )
    reserved_quantity = models.PositiveIntegerField(
        verbose_name="Reserved quantity product in warehouse",
        default=0
    )
    created_at = models.DateTimeField(verbose_name="Stock created", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Stock updated", auto_now=True)

    @property
    def available_quantity(self) -> int:
        return self.quantity - self.reserved_quantity

    class Meta:
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"
        constraints = [
            UniqueConstraint(
                fields=["warehouse", "product"],
                name="unique_stock_warehouse_product",
                violation_error_message=(
                    "This product is already assigned to this warehouse."
                ),
            ),
            CheckConstraint(
                condition=Q(reserved_quantity__lte=F("quantity")),
                name="reserved_quantity_lte_quantity",
                violation_error_message=(
                    "Reserved quantity can't be more than quantity"
                ),
            ),
        ]

    def __str__(self) -> str:
        return f"{self.warehouse.name} | {self.product.name} | {self.quantity}"
