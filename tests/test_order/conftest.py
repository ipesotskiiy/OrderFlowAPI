import pytest

from orders.models import Order, OrderItem


@pytest.fixture()
def draft_order(user_obj, first_warehouse, first_category_first_product):
    order_data = {
        "customer": user_obj,
        "warehouse": first_warehouse,
        "status": Order.Status.DRAFT,
    }
    ord_obj = Order.objects.create(**order_data)
    order_items_data = [
        {
            "product": first_category_first_product,
            "quantity": 3,
            "unit_price": first_category_first_product.price
        }
    ]
    for item in order_items_data:
        OrderItem.objects.create(order=ord_obj, **item)
    return ord_obj


@pytest.fixture()
def second_user_order(
    second_user_obj,
    second_warehouse,
    first_category_first_product
):
    order_data = {
        "customer": second_user_obj,
        "warehouse": second_warehouse,
        "status": Order.Status.DRAFT,
    }
    ord_obj = Order.objects.create(**order_data)

    order_items_data = [
        {
            "product": first_category_first_product,
            "quantity": 6,
            "unit_price": first_category_first_product.price
        }
    ]

    for item in order_items_data:
        OrderItem.objects.create(order=ord_obj, **item)

    return ord_obj


@pytest.fixture()
def order_with_items(
    user_obj,
    first_warehouse,
    first_category_first_product,
    second_category_first_product,
):
    order_data = {
        "customer": user_obj,
        "warehouse": first_warehouse,
        "status": Order.Status.DRAFT,
    }
    ord_obj = Order.objects.create(**order_data)

    order_items_data = [
        {
            "product": first_category_first_product,
            "quantity": 8,
            "unit_price": first_category_first_product.price
        },
        {
            "product": second_category_first_product,
            "quantity": 2,
            "unit_price": second_category_first_product.price
        }
    ]
    for item in order_items_data:
        OrderItem.objects.create(order=ord_obj, **item)

    return ord_obj


@pytest.fixture()
def reserved_order(user_obj, first_warehouse, first_category_first_product):
    order_data = {
        "customer": user_obj,
        "warehouse": first_warehouse,
        "status": Order.Status.RESERVED,
    }

    ord_obj = Order.objects.create(**order_data)

    order_items_data = [
        {
            "product": first_category_first_product,
            "quantity": 3,
            "unit_price": first_category_first_product.price
        }
    ]

    for item in order_items_data:
        OrderItem.objects.create(order=ord_obj, **item)

    return ord_obj
