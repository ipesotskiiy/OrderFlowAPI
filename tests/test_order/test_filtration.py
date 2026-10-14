from datetime import timedelta

import pytest
from django.utils.timezone import now
from rest_framework import status

from orders.models import Order

pytestmark = pytest.mark.django_db

@pytest.mark.parametrize(
    "filter_status",
    [
        Order.Status.DRAFT,
        Order.Status.RESERVED,
    ]
)
def test_order_filter_status(
    api_client,
    user_obj,
    draft_order,
    reserved_order,
    order_with_items,
    second_user_order,
    filter_status,
):
    api_client.force_authenticate(user_obj)
    response = api_client.get(
        f"/api/v1/orders/?status={filter_status}",
    )
    assert response.status_code == status.HTTP_200_OK

    response_order_ids = {order["id"] for order in response.json()}

    if filter_status == "draft":
        assert response_order_ids == {draft_order.id, order_with_items.id}
    elif filter_status == "reserved":
        assert response_order_ids == {reserved_order.id}

    assert second_user_order.id not in response_order_ids


@pytest.mark.parametrize(
    "warehouse_filter, status_filter",
    [
        ("first", None),
        ("second", None),
        ("first", Order.Status.RESERVED),
        ("second", Order.Status.DRAFT),
    ]
)
def test_order_filter_warehouse(
    api_client,
    user_obj,
    draft_order,
    reserved_order,
    order_with_items,
    second_user_order,
    first_warehouse,
    second_warehouse,
    warehouse_filter,
    status_filter,
):
    order_with_items.warehouse = second_warehouse
    order_with_items.save()

    warehouse_id = (
        first_warehouse.id
        if warehouse_filter == "first"
        else second_warehouse.id
    )

    api_client.force_authenticate(user_obj)

    if status_filter is None:
        response = api_client.get(
            f"/api/v1/orders/?warehouse={warehouse_id}",
        )
    else:
        response = api_client.get(
            f"/api/v1/orders/?status={status_filter}&warehouse={warehouse_id}",
        )
    assert response.status_code == status.HTTP_200_OK

    response_order_ids = {order["id"] for order in response.json()}
    if warehouse_filter == "first" and status_filter is None:
        assert {draft_order.id, reserved_order.id} == response_order_ids
    elif warehouse_filter == "second" and status_filter is None:
        assert {order_with_items.id} == response_order_ids
    elif warehouse_filter == "first" and status_filter == "reserved":
        assert {reserved_order.id} == response_order_ids
    elif warehouse_filter == "second" and status_filter == "draft":
        assert {order_with_items.id} == response_order_ids


@pytest.mark.parametrize(
    "ordering_parameter",
    [
        "created_at",
        "-created_at",
        None,
    ]
)
def test_order_ordering_created_at(
        api_client,
        user_obj,
        draft_order,
        reserved_order,
        order_with_items,
        ordering_parameter,
):
    draft_order.created_at = now() - timedelta(days=3)
    draft_order.save()
    reserved_order.created_at = now() - timedelta(days=2)
    reserved_order.save()
    order_with_items.created_at = now() - timedelta(days=1)
    order_with_items.save()
    api_client.force_authenticate(user_obj)
    if ordering_parameter is None:
        response = api_client.get("/api/v1/orders/")
    else:
        response = api_client.get(
            f"/api/v1/orders/?ordering={ordering_parameter}"
        )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    if ordering_parameter == "created_at":
        assert response_data[0]["id"] == draft_order.id
        assert response_data[1]["id"] == reserved_order.id
        assert response_data[2]["id"] == order_with_items.id
    elif ordering_parameter == "-created_at":
        assert response_data[2]["id"] == draft_order.id
        assert response_data[1]["id"] == reserved_order.id
        assert response_data[0]["id"] == order_with_items.id
    elif ordering_parameter is None:
        assert response_data[2]["id"] == draft_order.id
        assert response_data[1]["id"] == reserved_order.id
        assert response_data[0]["id"] == order_with_items.id
