from datetime import datetime
from decimal import Decimal

import pytest
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError

from orders.models import Order, OrderItem

pytestmark = pytest.mark.django_db

def test_success_order_create(user_obj, first_warehouse):
    order_data = {
        "customer": user_obj,
        "warehouse": first_warehouse,
        "status": Order.Status.DRAFT,
    }
    order_obj = Order.objects.create(**order_data)

    assert order_obj.customer == order_data["customer"]
    assert order_obj.warehouse == order_data["warehouse"]
    assert order_obj.status == order_data["status"]


def test_order_default_status_draft(user_obj, first_warehouse):
    order_data = {
        "customer": user_obj,
        "warehouse": first_warehouse,
    }
    order_obj = Order.objects.create(**order_data)
    assert order_obj.status == Order.Status.DRAFT


def test_order_created_at_updated_at(draft_order):
    assert draft_order.created_at is not None
    assert isinstance(
        draft_order.created_at,
        datetime,
    )
    assert draft_order.updated_at is not None
    assert isinstance(
        draft_order.updated_at,
        datetime,
    )

def test_order_change_updated_at(draft_order, second_warehouse):
    old_update_at = draft_order.updated_at
    draft_order.warehouse = second_warehouse
    draft_order.save()
    assert old_update_at < draft_order.updated_at


def test_user_cant_delete_with_orders(user_obj, draft_order):
    with pytest.raises(ProtectedError) as ex:
        user_obj.delete()

    assert "Order.customer" in str(ex.value)


def test_warehouse_cant_delete_with_orders(first_warehouse, draft_order):
    with pytest.raises(ProtectedError) as ex:
        first_warehouse.delete()

    assert "Order.warehouse" in str(ex.value)


def test_success_order_item_create(second_category_first_product, draft_order):
    order_items_data = [
        {
            "product": second_category_first_product,
            "quantity": 3,
            "unit_price": second_category_first_product.price
        }
    ]
    for item in order_items_data:
        item_obj = OrderItem.objects.create(order=draft_order, **item)

        assert item_obj.product == item["product"]
        assert item_obj.quantity == item["quantity"]
        assert item_obj.unit_price == item["unit_price"]

@pytest.mark.parametrize(
    "quantity",
    [
        -3,
        0,
    ]
)
def test_order_item_invalid_quantity(
    second_category_first_product,
    draft_order,
    quantity
):
    order_items_data = [
        {
            "product": second_category_first_product,
            "quantity": quantity,
            "unit_price": second_category_first_product.price
        }
    ]
    with pytest.raises(IntegrityError) as ex:
        for item in order_items_data:
            OrderItem.objects.create(order=draft_order, **item)

    assert ex.typename == "IntegrityError"

def test_order_item_duplicate_product(first_category_first_product, draft_order):
    order_items_data = [
        {
            "product": first_category_first_product,
            "quantity": 3,
            "unit_price": first_category_first_product.price
        }
    ]
    with pytest.raises(IntegrityError) as ex:
        for item in order_items_data:
            OrderItem.objects.create(order=draft_order, **item)

    assert "unique_order_item_order_and_product" in str(ex.value)


def test_same_product_in_different_orders(
    draft_order,
    order_with_items,
    first_category_first_product
):
    draft_order_products = [
        item.product for item in draft_order.order_items.all()
    ]
    order_with_items_products = [
        item.product for item in order_with_items.order_items.all()
    ]
    assert first_category_first_product in draft_order_products
    assert first_category_first_product in order_with_items_products

def test_order_item_price_snapshot(
    second_category_first_product,
    draft_order
):
    order_items_data = [
        {
            "product": second_category_first_product,
            "quantity": 3,
            "unit_price": second_category_first_product.price
        }
    ]

    item_obj = OrderItem.objects.create(order=draft_order, **order_items_data[0])
    old_unit_price = item_obj.unit_price
    second_category_first_product.price = Decimal("999999")
    second_category_first_product.save()
    obj_after_price_change = OrderItem.objects.get(id=item_obj.id)
    assert old_unit_price == obj_after_price_change.unit_price


def test_order_item_created_at_updated_at(
    second_category_first_product,
    draft_order
):
    order_items_data = [
        {
            "product": second_category_first_product,
            "quantity": 3,
            "unit_price": second_category_first_product.price
        }
    ]

    item_obj = OrderItem.objects.create(order=draft_order, **order_items_data[0])
    assert item_obj.created_at is not None
    assert isinstance(
        item_obj.created_at,
        datetime,
    )
    assert item_obj.updated_at is not None
    assert isinstance(
        item_obj.updated_at,
        datetime,
    )


def test_order_item_change_updated_at(
    second_category_first_product,
    draft_order
):
    order_items_data = [
        {
            "product": second_category_first_product,
            "quantity": 3,
            "unit_price": second_category_first_product.price
        }
    ]

    item_obj = OrderItem.objects.create(order=draft_order, **order_items_data[0])
    old_updated_at = item_obj.updated_at
    item_obj.quantity = 10
    item_obj.save()
    assert old_updated_at < item_obj.updated_at

def test_order_delete_cascades_items(draft_order):
    id_for_search = draft_order.id
    draft_order.delete()
    assert not OrderItem.objects.filter(order=id_for_search).exists()


def test_product_cant_delete_with_order_items(
    draft_order,
    first_category_first_product
):
    with pytest.raises(ProtectedError) as ex:
        first_category_first_product.delete()
    assert "OrderItem.product" in str(ex.value)
