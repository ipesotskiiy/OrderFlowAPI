from django.contrib import admin

from catalog.models import Category, Product


# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "minimum_age",
        "created_at",
        "updated_at",
    )
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name", "minimum_age")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "manufacturer_name",
        "minimum_age",
        "sku",
        "price",
        "weight_kg",
        "height_cm",
        "color",
        "is_active",
        "created_at",
        "updated_at"
    )

    search_fields = (
        "name",
        "manufacturer_name",
        "sku"
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = (
        "name",
        "manufacturer_name",
        "sku",
        "is_active"
    )
