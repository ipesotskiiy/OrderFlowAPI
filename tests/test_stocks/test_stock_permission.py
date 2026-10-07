import pytest
from rest_framework import status

from stocks.models import Stock

pytestmark = pytest.mark.django_db

def test_anonymous_cant_get_list_stock(
    api_client,
    first_stock_with_first_warehouse_and_first_product,
    second_stock_with_first_warehouse_and_second_product,
):
    response = api_client.get(
        "/api/v1/stocks/",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Authentication credentials were not provided."


def test_anonymous_cant_get_retrieve_stock(
    api_client,
    first_stock_with_first_warehouse_and_first_product,
):
    response = api_client.get(
        f"/api/v1/stocks/{first_stock_with_first_warehouse_and_first_product.id}/",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Authentication credentials were not provided."


def test_anonymous_cant_create_stock(
    api_client,
    first_warehouse,
    first_category_first_product,
):
    stock_data = {
        "warehouse": first_warehouse.id,
        "product": first_category_first_product.id,
        "quantity": 10,
    }
    response = api_client.post(
        "/api/v1/stocks/",
        data=stock_data,
        format="json",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Authentication credentials were not provided."
    assert not Stock.objects.all().exists()


def test_anonymous_cant_update_stock(
    api_client,
    first_stock_with_first_warehouse_and_first_product
):
    stock_data = {
        "quantity": 100
    }
    response = api_client.patch(
        f"/api/v1/stocks/{first_stock_with_first_warehouse_and_first_product.id}/",
        data=stock_data,
        format="json",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Authentication credentials were not provided."

    stock_obj = Stock.objects.get(
        id=first_stock_with_first_warehouse_and_first_product.id
    )
    assert stock_obj == first_stock_with_first_warehouse_and_first_product
    assert (stock_obj.quantity ==
            first_stock_with_first_warehouse_and_first_product.quantity)

def test_anonymous_cant_delete_stock(
    api_client,
    first_stock_with_first_warehouse_and_first_product
):
    response = api_client.delete(
        f"/api/v1/stocks/{first_stock_with_first_warehouse_and_first_product.id}/",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Authentication credentials were not provided."
    assert Stock.objects.count() == 1


def test_non_manager_cant_get_list_stock(
    api_client,
    user_obj,
    first_stock_with_first_warehouse_and_first_product,
    second_stock_with_first_warehouse_and_second_product,
):
    api_client.force_authenticate(user_obj)
    response = api_client.get("/api/v1/stocks/")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert (response.json()["detail"] ==
            "You do not have permission to perform this action.")


def test_non_manager_cant_get_retrieve_stock(
    api_client,
    user_obj,
    first_stock_with_first_warehouse_and_first_product,
):
    api_client.force_authenticate(user_obj)
    response = api_client.get(
        f"/api/v1/stocks/{first_stock_with_first_warehouse_and_first_product.id}/",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert (response.json()["detail"] ==
            "You do not have permission to perform this action.")


def test_non_manager_cant_create_stock(
    api_client,
    user_obj,
    first_warehouse,
    first_category_first_product,
):
    stock_data = {
        "warehouse": first_warehouse.id,
        "product": first_category_first_product.id,
        "quantity": 10,
    }
    api_client.force_authenticate(user_obj)
    response = api_client.post(
        "/api/v1/stocks/",
        data=stock_data,
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert (response.json()["detail"] ==
            "You do not have permission to perform this action.")
    assert not Stock.objects.all().exists()


def test_non_manager_cant_update_stock(
    api_client,
    user_obj,
    first_stock_with_first_warehouse_and_first_product
):
    stock_data = {
        "quantity": 100
    }
    api_client.force_authenticate(user_obj)
    response = api_client.patch(
        f"/api/v1/stocks/{first_stock_with_first_warehouse_and_first_product.id}/",
        data=stock_data,
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert (response.json()["detail"] ==
            "You do not have permission to perform this action.")

    stock_obj = Stock.objects.get(
        id=first_stock_with_first_warehouse_and_first_product.id
    )
    assert stock_obj == first_stock_with_first_warehouse_and_first_product
    assert (stock_obj.quantity ==
            first_stock_with_first_warehouse_and_first_product.quantity)


def test_non_manager_cant_delete_stock(
    api_client,
    user_obj,
    first_stock_with_first_warehouse_and_first_product
):
    api_client.force_authenticate(user_obj)
    response = api_client.delete(
        f"/api/v1/stocks/{first_stock_with_first_warehouse_and_first_product.id}/",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert (response.json()["detail"] ==
            "You do not have permission to perform this action.")
    assert Stock.objects.count() == 1


def test_manager_can_get_list_stock(
    api_client,
    user_obj,
    first_stock_with_first_warehouse_and_first_product,
    second_stock_with_first_warehouse_and_second_product,
    first_warehouse_manager_assignment,
):
    api_client.force_authenticate(user_obj)
    response = api_client.get("/api/v1/stocks/")

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()

    ids = {stock["id"] for stock in response_data}
    assert first_stock_with_first_warehouse_and_first_product.id in ids
    assert second_stock_with_first_warehouse_and_second_product.id in ids


def test_manager_can_get_retrieve_stock(
    api_client,
    user_obj,
    first_stock_with_first_warehouse_and_first_product,
    first_warehouse_manager_assignment,
):
    api_client.force_authenticate(user_obj)
    response = api_client.get(
        f"/api/v1/stocks/{first_stock_with_first_warehouse_and_first_product.id}/",
    )
    assert response.status_code == status.HTTP_200_OK

    stock_obj = Stock.objects.get(id=response.json()["id"])
    assert stock_obj == first_stock_with_first_warehouse_and_first_product


def test_manager_cant_create_stock(
    api_client,
    user_obj,
    first_warehouse,
    first_category_first_product,
    first_warehouse_manager_assignment,
):
    stock_data = {
        "warehouse": first_warehouse.id,
        "product": first_category_first_product.id,
        "quantity": 10,
    }
    api_client.force_authenticate(user_obj)
    response = api_client.post(
        "/api/v1/stocks/",
        data=stock_data,
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert (response.json()["detail"] ==
            "You do not have permission to perform this action.")
    assert not Stock.objects.all().exists()


def test_manager_can_update_stock(
    api_client,
    user_obj,
    first_stock_with_first_warehouse_and_first_product,
    first_warehouse_manager_assignment,
):
    stock_data = {
        "quantity": 100
    }
    api_client.force_authenticate(user_obj)
    response = api_client.patch(
        f"/api/v1/stocks/{first_stock_with_first_warehouse_and_first_product.id}/",
        data=stock_data,
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK

    stock_obj = Stock.objects.get(
        id=first_stock_with_first_warehouse_and_first_product.id
    )
    assert stock_obj.quantity == stock_data["quantity"]


def test_manager_cant_delete_stock(
    api_client,
    user_obj,
    first_stock_with_first_warehouse_and_first_product,
    first_warehouse_manager_assignment,
):
    api_client.force_authenticate(user_obj)
    response = api_client.delete(
        f"/api/v1/stocks/{first_stock_with_first_warehouse_and_first_product.id}/",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert (response.json()["detail"] ==
            "You do not have permission to perform this action.")
    assert Stock.objects.count() == 1


def test_staff_can_get_list_stock(
    api_client,
    staff_user_obj,
    first_stock_with_first_warehouse_and_first_product,
    second_stock_with_first_warehouse_and_second_product,
):
    api_client.force_authenticate(staff_user_obj)
    response = api_client.get("/api/v1/stocks/")

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()

    ids = {stock["id"] for stock in response_data}
    assert first_stock_with_first_warehouse_and_first_product.id in ids
    assert second_stock_with_first_warehouse_and_second_product.id in ids


def test_staff_can_get_retrieve_stock(
    api_client,
    staff_user_obj,
    first_stock_with_first_warehouse_and_first_product,
):
    api_client.force_authenticate(staff_user_obj)
    response = api_client.get(
        f"/api/v1/stocks/{first_stock_with_first_warehouse_and_first_product.id}/",
    )
    assert response.status_code == status.HTTP_200_OK

    stock_obj = Stock.objects.get(id=response.json()["id"])
    assert stock_obj == first_stock_with_first_warehouse_and_first_product


def test_staff_can_create_stock(
    api_client,
    staff_user_obj,
    first_warehouse,
    first_category_first_product,
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
    assert Stock.objects.count() == 1
    assert stock_obj.warehouse_id == stock_data["warehouse"]
    assert stock_obj.product_id == stock_data["product"]
    assert stock_obj.quantity == stock_data["quantity"]


def test_staff_can_update_stock(
    api_client,
    staff_user_obj,
    first_stock_with_first_warehouse_and_first_product,
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
        id=first_stock_with_first_warehouse_and_first_product.id
    )
    assert stock_obj.quantity == stock_data["quantity"]


def test_staff_can_delete_stock(
    api_client,
    staff_user_obj,
    first_stock_with_first_warehouse_and_first_product,
):
    api_client.force_authenticate(staff_user_obj)
    response = api_client.delete(
        f"/api/v1/stocks/{first_stock_with_first_warehouse_and_first_product.id}/",
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Stock.objects.exists()


def test_staff_cant_update_stock_with_put(
    api_client,
    staff_user_obj,
    first_warehouse,
    first_category_first_product,
    first_stock_with_first_warehouse_and_first_product,
):
    stock_data = {
        "warehouse": first_warehouse.id,
        "product": first_category_first_product.id,
        "quantity": 100,
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.put(
        f"/api/v1/stocks/{first_stock_with_first_warehouse_and_first_product.id}/",
        data=stock_data,
        format="json",
    )
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    stock_obj = Stock.objects.get(
        id=first_stock_with_first_warehouse_and_first_product.id,
    )
    assert stock_obj == first_stock_with_first_warehouse_and_first_product
    assert (stock_obj.quantity ==
            first_stock_with_first_warehouse_and_first_product.quantity)
