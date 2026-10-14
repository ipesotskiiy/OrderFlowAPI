import pytest
from rest_framework import status

from catalog.models import Product
from orders.models import Order, OrderItem

pytestmark = pytest.mark.django_db

def test_order_patch_warehouse(
        api_client,
        user_obj,
        draft_order,
        second_warehouse,
):
    api_client.force_authenticate(user_obj)
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
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert response_data["id"] == draft_order.id
    order_obj = Order.objects.get(id=response_data["id"])
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


def test_order_patch_item_quantity(
        api_client,
        user_obj,
        draft_order,
        first_category_first_product
):
    api_client.force_authenticate(user_obj)
    order_data = {
        "order_items": [
            {
                "product": first_category_first_product.id,
                "quantity": 10,
            }
        ]
    }
    old_order_items_data = set(
        OrderItem.objects.filter(
            order=draft_order.id
        ).values_list(
            "id",
            "unit_price",
        )
    )

    response = api_client.patch(
        f"/api/v1/orders/{draft_order.id}/",
        data=order_data,
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    order_obj = Order.objects.get(id=draft_order.id)
    assert order_obj.order_items.first().quantity == 10

    new_order_items_data = set(
        OrderItem.objects.filter(
            order=draft_order.id
        ).values_list(
            "id",
            "unit_price",
        )
    )
    assert old_order_items_data == new_order_items_data


def test_order_patch_add_new_item(
        api_client,
        user_obj,
        draft_order,
        first_category_first_product,
        second_category_first_product
):
    api_client.force_authenticate(user_obj)
    order_data = {
        "order_items": [
            {
                "product": first_category_first_product.id,
                "quantity": 3,
            },
            {
                "product": second_category_first_product.id,
                "quantity": 5,
            }
        ]
    }
    old_order_items_data = set(
        OrderItem.objects.filter(
            order=draft_order.id
        ).values_list(
            "id",
            "quantity",
            "unit_price",
        )
    )

    response = api_client.patch(
        f"/api/v1/orders/{draft_order.id}/",
        data=order_data,
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert OrderItem.objects.filter(
        order=draft_order.id
    ).count() == 2

    old_item_data_after_patch = set(
        OrderItem.objects.filter(
            order=draft_order.id,
            product=first_category_first_product.id,
        ).values_list(
            "id",
            "quantity",
            "unit_price",
        )
    )
    assert old_item_data_after_patch == old_order_items_data

    new_item = OrderItem.objects.get(
        order=draft_order.id,
        product=second_category_first_product.id,
    )
    assert new_item.product == second_category_first_product
    assert new_item.quantity == 5
    assert new_item.unit_price == second_category_first_product.price


def test_order_patch_remove_item(
        api_client,
        user_obj,
        order_with_items,
        first_category_first_product,
        second_category_first_product
):
    api_client.force_authenticate(user_obj)
    order_data = {
        "order_items": [
            {
                "product": first_category_first_product.id,
                "quantity": 8,
            }
        ]
    }
    old_order_items_data = set(
        OrderItem.objects.filter(
            order=order_with_items.id
        ).values_list(
            "id",
            "quantity",
            "unit_price",
        )
    )

    response = api_client.patch(
        f"/api/v1/orders/{order_with_items.id}/",
        data=order_data,
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert OrderItem.objects.filter(
        order=order_with_items.id
    ).count() == 1


    assert not OrderItem.objects.filter(
        order=order_with_items,
        product=second_category_first_product.id
    ).exists()

    new_order_items_data = list(
        OrderItem.objects.filter(
            order=order_with_items.id
        ).values_list(
            "id",
            "quantity",
            "unit_price",
        )
    )
    assert new_order_items_data[0] in old_order_items_data


@pytest.mark.parametrize(
    "order_data",
    [
        "empty",
        "duplicate",
        "zero",
        "not exists"
    ]
)
def test_order_patch_invalid_items(
        api_client,
        user_obj,
        draft_order,
        first_category_first_product,
        order_data,
):
    if order_data == "empty":
        order_data = {
            "order_items": []
        }
    elif order_data == "duplicate":
        order_data = {
            "order_items": [
                {
                    "product": first_category_first_product.id,
                    "quantity": 3,
                },
                {
                    "product": first_category_first_product.id,
                    "quantity": 5,
                }
            ]
        }
    elif order_data == "zero":
        order_data = {
            "order_items": [
                {
                    "product": first_category_first_product.id,
                    "quantity": 0,
                },
            ]
        }
    elif order_data == "not exists":
        assert not Product.objects.filter(id=99).exists()
        order_data = {
            "order_items": [
                {
                    "product": 99,
                    "quantity": 3,
                }
            ]
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

    api_client.force_authenticate(user_obj)
    response = api_client.patch(
        f"/api/v1/orders/{draft_order.id}/",
        data=order_data,
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

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
    assert new_order_items_data == old_order_items_data


@pytest.mark.parametrize(
    "order_status",
    [
        Order.Status.RESERVED,
        Order.Status.CONFIRMED,
        Order.Status.CANCELLED,
        Order.Status.EXPIRED,
    ]
)
def test_order_patch_non_draft(
    api_client,
    user_obj,
    draft_order,
    second_warehouse,
    order_status,
):
    draft_order.status = order_status
    draft_order.save()

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
    old_order_fields = set(
        Order.objects.filter(
            id=draft_order.id
        ).values_list()
    )

    api_client.force_authenticate(user_obj)
    response = api_client.patch(
        f"/api/v1/orders/{draft_order.id}/",
        data=order_data,
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

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
    assert new_order_items_data == old_order_items_data

    assert set(
        Order.objects.filter(
            id=draft_order.id
        ).values_list()
    ) == old_order_fields


@pytest.mark.parametrize(
    "field",
    [
        "customer",
        "status",
        "unit_price",
    ]
)
def test_order_patch_protected_fields(
    api_client,
    user_obj,
    second_user_obj,
    draft_order,
    first_category_first_product,
    field,
):
    api_client.force_authenticate(user_obj)
    if field == "customer":
        order_data = {
            "customer": second_user_obj.id
        }
    if field == "status":
        order_data = {
            "status": Order.Status.RESERVED
        }
    if field == "unit_price":
        order_data = {
            "order_items": [
                {
                    "product": first_category_first_product.id,
                    "quantity": 3,
                    "unit_price": 0,
                },
            ]
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
    old_order_fields = set(
        Order.objects.filter(
            id=draft_order.id
        ).values_list(
            "id",
            "warehouse_id",
            "customer_id",
            "status"
        )
    )

    response = api_client.patch(
        f"/api/v1/orders/{draft_order.id}/",
        data=order_data,
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK

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
    new_order_fields = set(
        Order.objects.filter(
            id=draft_order.id
        ).values_list(
            "id",
            "warehouse_id",
            "customer_id",
            "status"
        )
    )

    assert old_order_items_data == new_order_items_data
    assert old_order_fields == new_order_fields


def test_order_patch_updated_at(
        api_client,
        user_obj,
        draft_order,
        second_warehouse,
):
    api_client.force_authenticate(user_obj)
    order_data = {
        "warehouse": second_warehouse.id,
    }

    old_updated_at = draft_order.updated_at

    response = api_client.patch(
        f"/api/v1/orders/{draft_order.id}/",
        data=order_data,
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK

    ord_obj = Order.objects.get(id=draft_order.id)
    assert old_updated_at < ord_obj.updated_at


