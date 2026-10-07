import pytest
from rest_framework import status

from stocks.models import Stock

pytestmark = pytest.mark.django_db

def test_manager_can_get_only_own_warehouse_stocks(
    api_client,
    user_obj,
    first_stock_with_first_warehouse_and_first_product,
    second_stock_with_first_warehouse_and_second_product,
    third_stock_with_third_warehouse_and_third_product,
    first_warehouse_manager_assignment,
    second_warehouse_manager_assignment,
):
    api_client.force_authenticate(user_obj)
    response = api_client.get("/api/v1/stocks/")

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()

    ids = {stock["id"] for stock in response_data}
    assert first_stock_with_first_warehouse_and_first_product.id in ids
    assert second_stock_with_first_warehouse_and_second_product.id in ids
    assert third_stock_with_third_warehouse_and_third_product.id not in ids


def test_manager_cant_retrieve_another_manager_warehouse_stock(
    api_client,
    user_obj,
    third_stock_with_third_warehouse_and_third_product,
    first_warehouse_manager_assignment,
    third_warehouse_manager_assignment_another_user,
):
    api_client.force_authenticate(user_obj)
    response = api_client.get(
        f"/api/v1/stocks/{third_stock_with_third_warehouse_and_third_product.id}/"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_manager_cant_update_another_manager_warehouse_stock(
    api_client,
    user_obj,
    third_stock_with_third_warehouse_and_third_product,
    first_warehouse_manager_assignment,
    third_warehouse_manager_assignment_another_user,
):
    stock_data = {
        "quantity": 100
    }
    api_client.force_authenticate(user_obj)
    response = api_client.patch(
        f"/api/v1/stocks/{third_stock_with_third_warehouse_and_third_product.id}/",
        data=stock_data,
        format="json",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    stock_obj = Stock.objects.get(
        id=third_stock_with_third_warehouse_and_third_product.id
    )
    assert (stock_obj.quantity ==
            third_stock_with_third_warehouse_and_third_product.quantity)


def test_manager_with_multiple_warehouses_gets_all_own_stocks(
    api_client,
    user_obj,
    first_stock_with_first_warehouse_and_first_product,
    second_stock_with_first_warehouse_and_second_product,
    third_stock_with_third_warehouse_and_third_product,
    fourth_stock_with_second_warehouse_and_second_product,
    first_warehouse_manager_assignment,
    second_warehouse_manager_assignment,
    third_warehouse_manager_assignment_another_user,
):
    api_client.force_authenticate(user_obj)
    response = api_client.get("/api/v1/stocks/")

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()

    ids = {stock["id"] for stock in response_data}
    assert first_stock_with_first_warehouse_and_first_product.id in ids
    assert second_stock_with_first_warehouse_and_second_product.id in ids
    assert fourth_stock_with_second_warehouse_and_second_product.id in ids
    assert third_stock_with_third_warehouse_and_third_product.id not in ids


def test_staff_can_get_all_warehouse_stocks(
    api_client,
    staff_user_obj,
    first_stock_with_first_warehouse_and_first_product,
    second_stock_with_first_warehouse_and_second_product,
    third_stock_with_third_warehouse_and_third_product,
    fourth_stock_with_second_warehouse_and_second_product,
):
    api_client.force_authenticate(staff_user_obj)
    response = api_client.get("/api/v1/stocks/")

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()

    ids = {stock["id"] for stock in response_data}
    assert first_stock_with_first_warehouse_and_first_product.id in ids
    assert second_stock_with_first_warehouse_and_second_product.id in ids
    assert fourth_stock_with_second_warehouse_and_second_product.id in ids
    assert third_stock_with_third_warehouse_and_third_product.id in ids
