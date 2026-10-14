import pytest
from rest_framework import status

from orders.models import Order, OrderItem

pytestmark = pytest.mark.django_db

def test_order_anonymous_access_denied_list(
    api_client,
    order_with_items,
    draft_order,
):
    response = api_client.get("/api/v1/orders/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_order_anonymous_access_denied_retrieve(
    api_client,
    draft_order,
):
    response = api_client.get(f"/api/v1/orders/{draft_order.id}/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_order_anonymous_access_denied_create(
    api_client,
    first_warehouse,
    first_category_first_product,
    second_category_first_product,
):
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
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not Order.objects.exists()
    assert not OrderItem.objects.exists()


def test_order_anonymous_access_denied_patch(
        api_client,
        draft_order,
        first_warehouse,
        second_warehouse,
):
    order_data = {
        "warehouse": second_warehouse.id,
    }
    old_order_items_data = set(
        OrderItem.objects.filter(
            order=draft_order.id
        ).values_list(
            "id",
            "product_id",
            "quantity",
            "unit_price",
        )
    )

    response = api_client.patch(
        f"/api/v1/orders/{draft_order.id}/",
        data=order_data,
        format="json",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    order_obj = Order.objects.get(id=draft_order.id)
    assert order_obj.warehouse == first_warehouse
    assert order_obj.customer == draft_order.customer
    assert order_obj.status == draft_order.status

    new_order_items_data = set(
        OrderItem.objects.filter(
            order=draft_order.id
        ).values_list(
            "id",
            "product_id",
            "quantity",
            "unit_price",
        )
    )
    assert old_order_items_data == new_order_items_data


def test_order_patch_other_user_order(
        api_client,
        second_user_obj,
        draft_order,
        first_warehouse,
        second_warehouse,
):
    order_data = {
        "warehouse": second_warehouse.id,
    }
    old_order_items_data = set(
        OrderItem.objects.filter(
            order=draft_order.id
        ).values_list(
            "id",
            "product_id",
            "quantity",
            "unit_price",
        )
    )

    api_client.force_authenticate(second_user_obj)
    response = api_client.patch(
        f"/api/v1/orders/{draft_order.id}/",
        data=order_data,
        format="json",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    order_obj = Order.objects.get(id=draft_order.id)
    assert order_obj.warehouse == first_warehouse
    assert order_obj.customer == draft_order.customer
    assert order_obj.status == draft_order.status

    new_order_items_data = set(
        OrderItem.objects.filter(
            order=draft_order.id
        ).values_list(
            "id",
            "product_id",
            "quantity",
            "unit_price",
        )
    )
    assert old_order_items_data == new_order_items_data


def test_order_patch_staff_other_user_order(
        api_client,
        staff_user_obj,
        draft_order,
        first_warehouse,
        second_warehouse,
):
    order_data = {
        "warehouse": second_warehouse.id,
    }
    old_order_items_data = set(
        OrderItem.objects.filter(
            order=draft_order.id
        ).values_list(
            "id",
            "product_id",
            "quantity",
            "unit_price",
        )
    )

    api_client.force_authenticate(staff_user_obj)
    response = api_client.patch(
        f"/api/v1/orders/{draft_order.id}/",
        data=order_data,
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK

    order_obj = Order.objects.get(id=draft_order.id)
    assert order_obj.warehouse == second_warehouse
    assert order_obj.customer == draft_order.customer
    assert order_obj.status == draft_order.status

    new_order_items_data = set(
        OrderItem.objects.filter(
            order=draft_order.id
        ).values_list(
            "id",
            "product_id",
            "quantity",
            "unit_price",
        )
    )
    assert old_order_items_data == new_order_items_data


def test_order_forbidden_http_method_put(
        api_client,
        staff_user_obj,
        draft_order,
        first_warehouse,
        second_warehouse,
):
    order_data = {
        "warehouse": second_warehouse.id,
    }
    old_order_items_data = set(
        OrderItem.objects.filter(
            order=draft_order.id
        ).values_list(
            "id",
            "product_id",
            "quantity",
            "unit_price",
        )
    )

    api_client.force_authenticate(staff_user_obj)
    response = api_client.put(
        f"/api/v1/orders/{draft_order.id}/",
        data=order_data,
        format="json",
    )
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    order_obj = Order.objects.get(id=draft_order.id)
    assert order_obj.warehouse == first_warehouse
    assert order_obj.customer == draft_order.customer
    assert order_obj.status == draft_order.status

    new_order_items_data = set(
        OrderItem.objects.filter(
            order=draft_order.id
        ).values_list(
            "id",
            "product_id",
            "quantity",
            "unit_price",
        )
    )
    assert old_order_items_data == new_order_items_data


def test_order_forbidden_http_method_delete(
        api_client,
        staff_user_obj,
        draft_order,
        first_warehouse,
        second_warehouse,
):
    old_order_items_data = set(
        OrderItem.objects.filter(
            order=draft_order.id
        ).values_list(
            "id",
            "product_id",
            "quantity",
            "unit_price",
        )
    )

    api_client.force_authenticate(staff_user_obj)
    response = api_client.delete(
        f"/api/v1/orders/{draft_order.id}/",
    )
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    order_obj = Order.objects.get(id=draft_order.id)
    assert order_obj.warehouse == first_warehouse
    assert order_obj.customer == draft_order.customer
    assert order_obj.status == draft_order.status

    new_order_items_data = set(
        OrderItem.objects.filter(
            order=draft_order.id
        ).values_list(
            "id",
            "product_id",
            "quantity",
            "unit_price",
        )
    )
    assert old_order_items_data == new_order_items_data


def test_order_warehouse_manager_isolation(
        api_client,
        user_obj,
        second_user_order,
        second_warehouse_manager_assignment,
):
    api_client.force_authenticate(user_obj)
    response = api_client.get(
        "/api/v1/orders/",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

    response = api_client.get(
        f"/api/v1/orders/{second_user_order.id}/",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
