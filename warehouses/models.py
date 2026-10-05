from django.conf import settings
from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.db.models.functions import Lower


# Create your models here.
class Warehouse(models.Model):
    name = models.CharField(verbose_name="Warehouse name", max_length=100)
    code = models.CharField(verbose_name="Warehouse code", max_length=50)
    address = models.CharField(verbose_name="Warehouse address", max_length=255)
    is_active = models.BooleanField(verbose_name="Warehouse active", default=True)
    created_at = models.DateTimeField(
        verbose_name="Warehouse create",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(verbose_name="Warehouse update", auto_now=True)

    class Meta:
        verbose_name = "Warehouse"
        verbose_name_plural = "Warehouses"
        constraints = [
            UniqueConstraint(
                Lower("code"),
                name="unique_lower_warehouse_code",
                violation_error_message=(
                    "A warehouse with this code already exists."
                ),
            ),
        ]

    def __str__(self) -> str:
        return self.code


class WarehouseManagerAssignment(models.Model):
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="manager_assignments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="warehouse_assignments",
    )
    created_at = models.DateTimeField(
        verbose_name="Warehouse manager assignment created",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Warehouse manager assignment"
        verbose_name_plural = "Warehouse manager assignments"
        constraints = [
            UniqueConstraint(
                fields=["warehouse", "user"],
                name="unique_user_warehouse_relation",
                violation_error_message=(
                    "This user is already assigned to this warehouse."
                ),
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} -> {self.warehouse}"
