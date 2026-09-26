from django.db import models
from django.db.models import CheckConstraint, Q, UniqueConstraint
from django.db.models.functions import Lower


class Category(models.Model):
    name = models.CharField(verbose_name="Category name", max_length=50)
    minimum_age = models.PositiveSmallIntegerField(
        verbose_name="Аge restriction",
        default=0,
    )
    created_at = models.DateTimeField(verbose_name="Category create", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Category update", auto_now=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        constraints = [
            UniqueConstraint(
                Lower("name"),
                name="unique_lower_name_category",
                violation_error_message="A category with this name already exists.",
            )
        ]


class Product(models.Model):
    name = models.CharField(verbose_name="Product name", max_length=50)
    manufacturer_name = models.CharField(
        verbose_name="Product manufacturer",
        max_length=50,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )
    minimum_age = models.PositiveSmallIntegerField(
        verbose_name="Аge restriction",
        default=0,
    )
    sku = models.CharField(verbose_name="Product article", max_length=100, unique=True)
    price = models.DecimalField(
        verbose_name="Product price",
        max_digits=10,
        decimal_places=2,
    )
    weight_kg = models.DecimalField(
        verbose_name="Product weight in kilograms",
        max_digits=8,
        decimal_places=2,
    )
    height_cm = models.DecimalField(
        verbose_name="Product height in centimeters",
        max_digits=8,
        decimal_places=2,
    )
    color = models.CharField(
        verbose_name="Product color",
        max_length=15,
        blank=True
    )
    is_active = models.BooleanField(
        verbose_name="Product is active",
        default=True,
    )
    created_at = models.DateTimeField(verbose_name="Product create", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Product update", auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

        constraints = [
            CheckConstraint(
                condition=Q(height_cm__gt=0),
                name="height_cm_positive",
                violation_error_message="The product height must be greater than zero."
            ),
            CheckConstraint(
                condition=Q(weight_kg__gt=0),
                name="weight_kg_positive",
                violation_error_message="The weight must be greater than zero."
            ),
            CheckConstraint(
                condition=Q(price__gt=0),
                name="product_price_positive",
                violation_error_message="The product price must be greater than zero."
            ),
        ]


    def __str__(self) -> str:
        return self.name
