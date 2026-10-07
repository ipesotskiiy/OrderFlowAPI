import pytest
from rest_framework import status

from stocks.models import Stock

pytestmark = pytest.mark.django_db

def test_success_creation_stock_with_api(
    api_client,
    first_warehouse,
    first_category_first_product,
    staff_user_obj,
):
    stock_data = {
        "warehouse": first_warehouse.id,
        "product": first_category_first_product.id,
        "quantity": 10,
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.post(
        "/api/v1/stocks/",
        data=stock_data,
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    stock_obj = Stock.objects.get(id=response.json()["id"])

    assert stock_obj.warehouse.id == stock_data["warehouse"]
    assert stock_obj.product.id == stock_data["product"]
    assert stock_obj.quantity == stock_data["quantity"]


def test_reserved_quantity_ignored_on_stock_creation(
    api_client,
    first_warehouse,
    first_category_first_product,
    staff_user_obj,
):
    stock_data = {
        "warehouse": first_warehouse.id,
        "product": first_category_first_product.id,
        "quantity": 10,
        "reserved_quantity": 2
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.post(
        "/api/v1/stocks/",
        data=stock_data,
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    stock_obj = Stock.objects.get(id=response.json()["id"])

    assert stock_obj.reserved_quantity == 0


def test_reserved_quantity_ignored_on_stock_update(
    api_client,
    staff_user_obj,
    first_stock_with_first_warehouse_and_first_product
):
    stock_data = {
        "reserved_quantity": 5
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.patch(
        f"/api/v1/stocks/{first_stock_with_first_warehouse_and_first_product.id}/",
        data=stock_data,
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    stock_obj = Stock.objects.get(id=response.json()["id"])

    assert (stock_obj.reserved_quantity ==
            first_stock_with_first_warehouse_and_first_product.reserved_quantity)

def test_error_change_warehouse_in_stock(
    api_client,
    staff_user_obj,
    second_warehouse,
    first_stock_with_first_warehouse_and_first_product
):
    stock_data = {
        "warehouse": second_warehouse.id
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.patch(
        f"/api/v1/stocks/{first_stock_with_first_warehouse_and_first_product.id}/",
        data=stock_data,
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    stock_obj = Stock.objects.get(
        id=first_stock_with_first_warehouse_and_first_product.id
    )

    assert (stock_obj.warehouse ==
            first_stock_with_first_warehouse_and_first_product.warehouse)


def test_error_change_product_in_stock(
    api_client,
    staff_user_obj,
    first_category_second_product,
    first_stock_with_first_warehouse_and_first_product
):
    stock_data = {
        "product": first_category_second_product.id
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.patch(
        f"/api/v1/stocks/{first_stock_with_first_warehouse_and_first_product.id}/",
        data=stock_data,
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    stock_obj = Stock.objects.get(
        id=first_stock_with_first_warehouse_and_first_product.id
    )

    assert (stock_obj.product ==
            first_stock_with_first_warehouse_and_first_product.product)


def test_success_change_quantity(
    api_client,
    staff_user_obj,
    first_stock_with_first_warehouse_and_first_product
):
    stock_data = {
        "quantity": 100
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.patch(
        f"/api/v1/stocks/{first_stock_with_first_warehouse_and_first_product.id}/",
        data=stock_data,
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    stock_obj = Stock.objects.get(
        id=response.json()["id"]
    )
    assert stock_obj.quantity == stock_data["quantity"]


def test_error_quantity_lower_than_reserved_quantity(
    api_client,
    staff_user_obj,
    first_stock_with_first_warehouse_and_first_product
):
    stock_data = {
        "quantity": 1
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.patch(
        f"/api/v1/stocks/{first_stock_with_first_warehouse_and_first_product.id}/",
        data=stock_data,
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    stock_obj = Stock.objects.get(
        id=first_stock_with_first_warehouse_and_first_product.id
    )
    assert (stock_obj.quantity ==
            first_stock_with_first_warehouse_and_first_product.quantity)


def test_error_duplicate_warehouse_and_product_with_api(
    api_client,
    staff_user_obj,
    first_warehouse,
    first_category_first_product,
    first_stock_with_first_warehouse_and_first_product
):
    stock_data = {
        "warehouse": first_warehouse.id,
        "product": first_category_first_product.id,
        "quantity": 10,
        "reserved_quantity": 2
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.post(
        "/api/v1/stocks/",
        data=stock_data,
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Stock.objects.count() == 1


@pytest.mark.parametrize(
    "required_field",
    [
        "warehouse",
        "product",
        "quantity"
    ]
)
def test_error_creation_stock_without_required_field(
    api_client,
    staff_user_obj,
    first_warehouse,
    first_category_first_product,
    required_field
):
    stock_data = {
        "warehouse": first_warehouse.id,
        "product": first_category_first_product.id,
        "quantity": 10,
    }
    stock_data.pop(required_field)
    api_client.force_authenticate(staff_user_obj)

    response = api_client.post(
        "/api/v1/stocks/",
        data=stock_data,
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not Stock.objects.all().exists()


def test_success_update_stock_with_same_warehouse_and_product(
    api_client,
    staff_user_obj,
    first_warehouse,
    first_category_first_product,
    first_stock_with_first_warehouse_and_first_product,
):
    stock_data = {
        "warehouse": first_warehouse.id,
        "product": first_category_first_product.id,
    }

    api_client.force_authenticate(staff_user_obj)
    response = api_client.patch(
        f"/api/v1/stocks/{first_stock_with_first_warehouse_and_first_product.id}/",
        data=stock_data,
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    stock_obj = Stock.objects.get(id=response.json()["id"])

    assert stock_obj.warehouse_id == first_warehouse.id
    assert stock_obj.product_id == first_category_first_product.id


def test_error_quantity_lower_than_zero(
    api_client,
    staff_user_obj,
    first_warehouse,
    first_category_first_product,
):
    stock_data = {
        "warehouse": first_warehouse.id,
        "product": first_category_first_product.id,
        "quantity": -1,
    }
    api_client.force_authenticate(staff_user_obj)

    response = api_client.post(
        "/api/v1/stocks/",
        data=stock_data,
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not Stock.objects.all().exists()
