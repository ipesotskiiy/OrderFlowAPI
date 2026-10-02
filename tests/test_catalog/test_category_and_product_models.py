from datetime import datetime
from decimal import Decimal

import pytest
from django.db import IntegrityError
from django.db.models import ProtectedError

from catalog.models import Category, Product

pytestmark = pytest.mark.django_db


def test_success_category_create():
    category_data = {
        "name": "Напитки",
        "minimum_age": 12,
    }

    category = Category.objects.create(**category_data)

    assert category is not None
    assert isinstance(category, Category)
    assert category.name == category_data["name"]
    assert category.minimum_age == category_data["minimum_age"]


def test_category_error_minimum_age_lower_zero():
    category_data = {
        "name": "Напитки",
        "minimum_age": -1,
    }
    with pytest.raises(IntegrityError) as ex:
        Category.objects.create(**category_data)

    assert "catalog_category_minimum_age_check" in str(ex.value)


def test_error_equal_name(first_category):
    category_data = {
        "name": "напитки",
        "minimum_age": 12,
    }

    with pytest.raises(IntegrityError) as ex:
        Category.objects.create(**category_data)

    assert "unique_lower_name_category" in str(ex.value)


def test_drop_category_with_product(first_category):
    product_data = {
        "name": "Кока Кола",
        "manufacturer_name": "Кока Кола инк",
        "category": first_category,
        "minimum_age": 7,
        "sku": "H2O-1",
        "price": Decimal("100"),
        "weight_kg": Decimal("0.5"),
        "height_cm": Decimal("30"),
        "color": "black",
    }
    Product.objects.create(**product_data)

    with pytest.raises(ProtectedError) as ex:
        first_category.delete()
    assert "Product.category" in str(ex.value)


def test_category_check_created_at_updated_at(first_category):
    assert first_category.created_at is not None
    assert isinstance(first_category.created_at, datetime)
    assert first_category.updated_at is not None
    assert isinstance(first_category.updated_at, datetime)


def test_category_change_updated_at(first_category):
    old_category_updated_at = first_category.updated_at
    first_category.name = "Вода"
    first_category.save()

    assert old_category_updated_at < first_category.updated_at

def test_category_default_minimum_age():
    category_data = {"name": "Напитки"}

    category = Category.objects.create(**category_data)
    assert category.minimum_age == 0


def test_success_product_create(first_category):
    product_data = {
        "name": "Кока Кола",
        "manufacturer_name": "Кока Кола инк",
        "category": first_category,
        "minimum_age": 7,
        "sku": "H2O-1",
        "price": Decimal("100"),
        "weight_kg": Decimal("0.5"),
        "height_cm": Decimal("30"),
        "color": "black",
    }
    product = Product.objects.create(**product_data)
    assert product is not None
    assert isinstance(product, Product)
    assert product.name == product_data["name"]
    assert product.manufacturer_name == product_data["manufacturer_name"]
    assert product.category == product_data["category"]
    assert product.minimum_age == product_data["minimum_age"]
    assert product.sku == product_data["sku"]
    assert product.price == product_data["price"]
    assert product.weight_kg == product_data["weight_kg"]
    assert product.height_cm == product_data["height_cm"]
    assert product.color == product_data["color"]


def test_product_error_minimum_age_lower_zero(first_category):
    product_data = {
        "name": "Кока Кола",
        "manufacturer_name": "Кока Кола инк",
        "category": first_category,
        "minimum_age": -1,
        "sku": "H2O-1",
        "price": Decimal("100"),
        "weight_kg": Decimal("0.5"),
        "height_cm": Decimal("30"),
        "color": "black",
    }
    with pytest.raises(IntegrityError) as ex:
        Product.objects.create(**product_data)
    assert "catalog_product_minimum_age_check" in str(ex.value)


def test_create_error_duplicate_sku(first_category, first_category_first_product):
    product_data = {
        "name": "Кока Кола",
        "manufacturer_name": "Кока Кола инк",
        "category": first_category,
        "minimum_age": 12,
        "sku": "H2O-1",
        "price": Decimal("100"),
        "weight_kg": Decimal("0.5"),
        "height_cm": Decimal("30"),
        "color": "black",
    }
    with pytest.raises(IntegrityError) as ex:
        Product.objects.create(**product_data)
    assert "catalog_product_sku_key" in str(ex.value)


@pytest.mark.parametrize(
    "price, weight_kg, height_cm",
    [
        ("0", "0.5", "30"),
        ("-1", "0.5", "30"),
        ("100", "0", "30"),
        ("100", "-1", "30"),
        ("100", "0.5", "0"),
        ("100", "0.5", "-1")
    ]
)
def test_error_constraint_fields_equal_and_lower_zero(
        first_category,
        price,
        weight_kg,
        height_cm
):
    product_data = {
        "name": "Кока Кола",
        "manufacturer_name": "Кока Кола инк",
        "category": first_category,
        "minimum_age": 7,
        "sku": "H2O-1",
        "price": Decimal(price),
        "weight_kg": Decimal(weight_kg),
        "height_cm": Decimal(height_cm),
        "color": "black",
    }
    with pytest.raises(IntegrityError) as ex:
        Product.objects.create(**product_data)
    if price == "0" or price == "-1":
        assert "product_price_positive" in str(ex.value)
    elif weight_kg == "0" or weight_kg == "-1":
        assert "weight_kg_positive" in str(ex.value)
    elif height_cm == "0" or height_cm == "-1":
        assert "height_cm_positive" in str(ex.value)


def test_product_check_created_at_updated_at(first_category):
    product_data = {
        "name": "Кока Кола",
        "manufacturer_name": "Кока Кола инк",
        "category": first_category,
        "minimum_age": 12,
        "sku": "H2O-1",
        "price": Decimal("100"),
        "weight_kg": Decimal("0.5"),
        "height_cm": Decimal("30"),
        "color": "black",
    }
    product = Product.objects.create(**product_data)
    assert product.created_at is not None
    assert isinstance(product.created_at, datetime)
    assert product.updated_at is not None
    assert isinstance(product.updated_at, datetime)


def test_product_change_updated_at(first_category_first_product):
    old_product_updated_at = first_category_first_product.updated_at
    first_category_first_product.name = "Пепси"
    first_category_first_product.save()

    assert old_product_updated_at < first_category_first_product.updated_at
