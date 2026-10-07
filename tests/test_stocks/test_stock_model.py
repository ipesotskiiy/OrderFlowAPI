from datetime import datetime

import pytest
from django.db.models.deletion import ProtectedError
from django.db.utils import IntegrityError

from stocks.models import Stock

pytestmark = pytest.mark.django_db


def test_success_stock_creation(first_warehouse, first_category_first_product):
    stock_data = {
        "warehouse": first_warehouse,
        "product": first_category_first_product,
        "quantity": 10,
        "reserved_quantity": 2,
    }

    stock_obj = Stock.objects.create(**stock_data)

    assert stock_obj.warehouse == stock_data["warehouse"]
    assert stock_obj.product == stock_data["product"]
    assert stock_obj.quantity == stock_data["quantity"]
    assert stock_obj.reserved_quantity == stock_data["reserved_quantity"]


def test_default_reserved_quantity_in_stock_is_zero(
    first_warehouse,
    first_category_first_product,
):
    stock_data = {
        "warehouse": first_warehouse,
        "product": first_category_first_product,
        "quantity": 10,
    }

    stock_obj = Stock.objects.create(**stock_data)
    assert stock_obj.reserved_quantity == 0

def test_correct_calculate_available_quantity_in_stock(
    first_stock_with_first_warehouse_and_first_product
):
    assert (first_stock_with_first_warehouse_and_first_product.available_quantity ==
            first_stock_with_first_warehouse_and_first_product.quantity -
            first_stock_with_first_warehouse_and_first_product.reserved_quantity)


def test_error_duplicate_warehouse_product_in_stock(
    first_stock_with_first_warehouse_and_first_product,
    first_warehouse,
    first_category_first_product,
):
    stock_data = {
        "warehouse": first_warehouse,
        "product": first_category_first_product,
        "quantity": 10,
        "reserved_quantity": 2,
    }
    with pytest.raises(IntegrityError) as ex:
        Stock.objects.create(**stock_data)

    assert "unique_stock_warehouse_product" in str(ex.value)


def test_error_create_stock_with_reserved_quantity_greater_than_quantity(
    first_warehouse,
    first_category_first_product,
):
    stock_data = {
        "warehouse": first_warehouse,
        "product": first_category_first_product,
        "quantity": 10,
        "reserved_quantity": 12,
    }
    with pytest.raises(IntegrityError) as ex:
        Stock.objects.create(**stock_data)

    assert "reserved_quantity_lte_quantity" in str(ex.value)


def test_stock_created_at_updated_at(
    first_stock_with_first_warehouse_and_first_product
):
    assert first_stock_with_first_warehouse_and_first_product.created_at is not None
    assert isinstance(
        first_stock_with_first_warehouse_and_first_product.created_at,
        datetime,
    )
    assert first_stock_with_first_warehouse_and_first_product.updated_at is not None
    assert isinstance(
        first_stock_with_first_warehouse_and_first_product.updated_at,
        datetime,
    )


def test_stock_change_updated_at(
    first_stock_with_first_warehouse_and_first_product
):
    old_updated_at = first_stock_with_first_warehouse_and_first_product.updated_at
    first_stock_with_first_warehouse_and_first_product.quantity = 4
    first_stock_with_first_warehouse_and_first_product.save()

    assert (old_updated_at <
            first_stock_with_first_warehouse_and_first_product.updated_at)


def test_error_delete_product_with_stock(
    first_category_first_product,
    first_stock_with_first_warehouse_and_first_product
):
    with pytest.raises(ProtectedError) as ex:
        first_category_first_product.delete()

    assert "Stock.product" in str(ex.value)


def test_error_delete_warehouse_with_stock(
    first_warehouse,
    first_stock_with_first_warehouse_and_first_product
):
    with pytest.raises(ProtectedError) as ex:
        first_warehouse.delete()

    assert "Stock.warehouse" in str(ex.value)
