from decimal import Decimal

import pytest
from rest_framework import status

from orders.models import Order, OrderItem

pytestmark = pytest.mark.django_db

def test_success_order_create_api(
    api_client,
    user_obj,
    first_warehouse,
    first_category_first_product,
    second_category_first_product,
):
    api_client.force_authenticate(user_obj)
    order_data = {
        "warehouse": first_warehouse.id,
        "order_items": [
            {
                "product": first_category_first_product.id,
                "quantity": 4
            },
            {
                "product": second_category_first_product.id,
                "quantity": 7
            }
        ]
    }

    response = api_client.post(
        "/api/v1/orders/",
        data=order_data,
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    order_obj = Order.objects.get(id=response_data["id"])
    assert Order.objects.count() == 1
    assert OrderItem.objects.filter(order=order_obj).count() == 2
    assert order_obj.customer == user_obj
    assert order_obj.status == Order.Status.DRAFT
    assert order_obj.warehouse == first_warehouse


    order_items_objs = OrderItem.objects.filter(order=order_obj)
    product_items_ids = set(item.product_id for item in order_items_objs)

    assert first_category_first_product.id in product_items_ids
    assert second_category_first_product.id in product_items_ids

    for item in order_items_objs:
        if item.product == first_category_first_product:
            assert item.unit_price == first_category_first_product.price
            assert item.quantity == 4
        elif item.product == second_category_first_product:
            assert item.unit_price == second_category_first_product.price
            assert item.quantity == 7


def test_order_create_empty_items(
    api_client,
    user_obj,
    first_warehouse,
):
    api_client.force_authenticate(user_obj)
    order_data = {
        "warehouse": first_warehouse.id,
        "order_items": []
    }

    response = api_client.post(
        "/api/v1/orders/",
        data=order_data,
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "order_items" in response.json()
    assert not Order.objects.exists()


def test_order_create_duplicate_products(
    api_client,
    user_obj,
    first_warehouse,
    first_category_first_product,
):
    api_client.force_authenticate(user_obj)
    order_data = {
        "warehouse": first_warehouse.id,
        "order_items": [
            {
                "product": first_category_first_product.id,
                "quantity": 4
            },
            {
                "product": first_category_first_product.id,
                "quantity": 7
            }
        ]
    }

    response = api_client.post(
        "/api/v1/orders/",
        data=order_data,
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "order_items" in response.json()
    assert not Order.objects.exists()


@pytest.mark.parametrize(
    "quantity",
    [
        0,
        -3,
    ]
)
def test_order_create_invalid_quantity(
    api_client,
    user_obj,
    first_warehouse,
    first_category_first_product,
    quantity
):
    api_client.force_authenticate(user_obj)
    order_data = {
        "warehouse": first_warehouse.id,
        "order_items": [
            {
                "product": first_category_first_product.id,
                "quantity": quantity
            }
        ]
    }

    response = api_client.post(
        "/api/v1/orders/",
        data=order_data,
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "order_items" in response.json()
    assert "quantity" in response.json()["order_items"]["0"]
    assert not Order.objects.exists()
    assert not OrderItem.objects.exists()


def test_order_create_invalid_product(
    api_client,
    user_obj,
    first_warehouse,
):
    api_client.force_authenticate(user_obj)
    order_data = {
        "warehouse": first_warehouse.id,
        "order_items": [
            {
                "product": 99,
                "quantity": 4
            }
        ]
    }

    response = api_client.post(
        "/api/v1/orders/",
        data=order_data,
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "order_items" in response.json()
    assert "product" in response.json()["order_items"]["0"]
    assert not Order.objects.exists()
    assert not OrderItem.objects.exists()


def test_order_create_invalid_warehouse(
    api_client,
    user_obj,
    first_category_first_product,
):
    api_client.force_authenticate(user_obj)
    order_data = {
        "warehouse": 99,
        "order_items": [
            {
                "product": first_category_first_product.id,
                "quantity": 4
            }
        ]
    }

    response = api_client.post(
        "/api/v1/orders/",
        data=order_data,
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "warehouse" in response.json()
    assert not Order.objects.exists()
    assert not OrderItem.objects.exists()


def test_order_create_cannot_override_customer(
    api_client,
    user_obj,
    second_user_obj,
    first_warehouse,
    first_category_first_product,
):
    api_client.force_authenticate(user_obj)
    order_data = {
        "customer": second_user_obj.id,
        "warehouse": first_warehouse.id,
        "order_items": [
            {
                "product": first_category_first_product.id,
                "quantity": 4
            }
        ]
    }

    response = api_client.post(
        "/api/v1/orders/",
        data=order_data,
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED

    order_obj = Order.objects.get(id=response.json()["id"])
    assert order_obj.customer == user_obj


def test_order_create_cannot_override_status(
    api_client,
    user_obj,
    first_warehouse,
    first_category_first_product,
):
    api_client.force_authenticate(user_obj)
    order_data = {
        "status": Order.Status.CONFIRMED,
        "warehouse": first_warehouse.id,
        "order_items": [
            {
                "product": first_category_first_product.id,
                "quantity": 4
            }
        ]
    }

    response = api_client.post(
        "/api/v1/orders/",
        data=order_data,
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED

    order_obj = Order.objects.get(id=response.json()["id"])
    assert order_obj.status == Order.Status.DRAFT


def test_order_create_cannot_override_unit_price(
    api_client,
    user_obj,
    first_warehouse,
    first_category_first_product,
):
    api_client.force_authenticate(user_obj)
    order_data = {
        "warehouse": first_warehouse.id,
        "order_items": [
            {
                "product": first_category_first_product.id,
                "quantity": 4,
                "unit_price": Decimal("1"),
            }
        ]
    }

    response = api_client.post(
        "/api/v1/orders/",
        data=order_data,
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED

    order_item_obj = OrderItem.objects.get(order_id=response.json()["id"])
    assert order_item_obj.unit_price == first_category_first_product.price
