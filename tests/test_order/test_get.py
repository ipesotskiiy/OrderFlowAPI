from decimal import Decimal

import pytest
from rest_framework import status

from orders.models import Order, OrderItem

pytestmark = pytest.mark.django_db

def test_order_list_only_own_orders(
    api_client,
    user_obj,
    draft_order,
    second_user_order,
):
    api_client.force_authenticate(user_obj)
    response = api_client.get("/api/v1/orders/")
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert len(response_data) == 1
    assert Order.objects.get(id=response_data[0]["id"]) == draft_order


def test_order_list_staff_all_orders(
    api_client,
    staff_user_obj,
    draft_order,
    second_user_order,
):
    api_client.force_authenticate(staff_user_obj)
    response = api_client.get("/api/v1/orders/")
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert len(response_data) == 2
    returned_order_identifiers = {order["id"] for order in response_data}
    assert draft_order.id in returned_order_identifiers
    assert second_user_order.id in returned_order_identifiers


def test_order_list_empty(
    api_client,
    second_user_obj,
    draft_order,
):
    api_client.force_authenticate(second_user_obj)
    response = api_client.get("/api/v1/orders/")
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert response_data == []


def test_order_list_nested_order_items(
    api_client,
    user_obj,
    order_with_items,
    first_category_first_product,
    second_category_first_product,
):
    api_client.force_authenticate(user_obj)
    response = api_client.get("/api/v1/orders/")
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert len(response_data) == 1
    order_obj = Order.objects.get(id=response_data[0]["id"])
    assert order_obj == order_with_items

    response_order_items_data = response_data[0]["order_items"]
    assert len(response_order_items_data) == 2

    response_order_items_product_ids = set(
        int(order_item["product"]) for order_item in response_order_items_data
    )

    assert {
               first_category_first_product.id, second_category_first_product.id
           } == response_order_items_product_ids

    for response_order_item in response_order_items_data:
        item_obj = OrderItem.objects.get(
            product=response_order_item["product"], order=order_obj.id
        )
        if response_order_item["product"] == first_category_first_product.id:
            assert response_order_item["id"] == item_obj.id
            assert response_order_item["quantity"] == 8
            assert (Decimal(response_order_item["unit_price"]) ==
                    first_category_first_product.price)
        elif response_order_item["product"] == second_category_first_product.id:
            assert response_order_item["id"] == item_obj.id
            assert response_order_item["quantity"] == 2
            assert (Decimal(response_order_item["unit_price"]) ==
                    second_category_first_product.price)


def test_order_retrieve_own_order(
    api_client,
    user_obj,
    draft_order,
    first_category_first_product,
):
    api_client.force_authenticate(user_obj)
    response = api_client.get(f"/api/v1/orders/{draft_order.id}/")
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert response_data["id"] == draft_order.id
    assert response_data["customer"] == draft_order.customer.id
    assert response_data["warehouse"] == draft_order.warehouse.id
    assert response_data["status"] == draft_order.status
    assert len(response_data["order_items"]) == 1
    assert response_data["order_items"][0]["id"] == draft_order.order_items.first().id
    assert response_data["order_items"][0]["product"] == first_category_first_product.id


def test_order_retrieve_other_user_order(
    api_client,
    user_obj,
    second_user_order,
):
    api_client.force_authenticate(user_obj)
    response = api_client.get(f"/api/v1/orders/{second_user_order.id}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_order_retrieve_staff_other_user_order(
    api_client,
    staff_user_obj,
    second_user_order,
    first_category_first_product,
):
    api_client.force_authenticate(staff_user_obj)
    response = api_client.get(f"/api/v1/orders/{second_user_order.id}/")
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert response_data["id"] == second_user_order.id
    assert response_data["customer"] == second_user_order.customer.id
    assert response_data["warehouse"] == second_user_order.warehouse.id
    assert response_data["status"] == second_user_order.status
    assert len(response_data["order_items"]) == 1
    assert (response_data["order_items"][0]["id"] ==
            second_user_order.order_items.first().id)
    assert response_data["order_items"][0]["product"] == first_category_first_product.id


def test_order_retrieve_nonexistent_order(
    api_client,
    user_obj,
):
    api_client.force_authenticate(user_obj)
    assert not Order.objects.filter(pk=99).exists()
    response = api_client.get("/api/v1/orders/99/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
