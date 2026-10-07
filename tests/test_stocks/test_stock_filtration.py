import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db

@pytest.mark.parametrize(
    "warehouse_num",
    [
        "1",
        "2",
        "3",
        "4"
    ]
)
def test_stock_filter_warehouse(
    api_client,
    staff_user_obj,
    first_warehouse,
    second_warehouse,
    third_warehouse,
    fourth_warehouse,
    first_stock_with_first_warehouse_and_first_product,
    second_stock_with_first_warehouse_and_second_product,
    third_stock_with_third_warehouse_and_third_product,
    fourth_stock_with_second_warehouse_and_second_product,
    warehouse_num,
):
    if warehouse_num == "1":
        warehouse_id = first_warehouse.id
    elif warehouse_num == "2":
        warehouse_id = second_warehouse.id
    elif warehouse_num == "3":
        warehouse_id = third_warehouse.id
    elif warehouse_num == "4":
        warehouse_id = fourth_warehouse.id

    api_client.force_authenticate(staff_user_obj)
    response = api_client.get(f"/api/v1/stocks/?warehouse={warehouse_id}")

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    if warehouse_num == "1":
        ids = {stock["id"] for stock in response_data}
        assert first_stock_with_first_warehouse_and_first_product.id in ids
        assert second_stock_with_first_warehouse_and_second_product.id in ids
        assert third_stock_with_third_warehouse_and_third_product.id not in ids
        assert fourth_stock_with_second_warehouse_and_second_product.id not in ids
    elif warehouse_num == "2":
        ids = {stock["id"] for stock in response_data}
        assert first_stock_with_first_warehouse_and_first_product.id not in ids
        assert second_stock_with_first_warehouse_and_second_product.id not in ids
        assert third_stock_with_third_warehouse_and_third_product.id not in ids
        assert fourth_stock_with_second_warehouse_and_second_product.id in ids
    elif warehouse_num == "3":
        ids = {stock["id"] for stock in response_data}
        assert first_stock_with_first_warehouse_and_first_product.id not in ids
        assert second_stock_with_first_warehouse_and_second_product.id not in ids
        assert third_stock_with_third_warehouse_and_third_product.id in ids
        assert fourth_stock_with_second_warehouse_and_second_product.id not in ids
    elif warehouse_num == "4":
        assert response_data == []


@pytest.mark.parametrize(
    "product_num",
    [
        "1",
        "2",
        "3",
        "4"
    ]
)
def test_stock_filter_product(
    api_client,
    staff_user_obj,
    first_category_first_product,
    first_category_second_product,
    second_category_first_product,
    first_category_third_product,
    first_stock_with_first_warehouse_and_first_product,
    second_stock_with_first_warehouse_and_second_product,
    third_stock_with_third_warehouse_and_third_product,
    fourth_stock_with_second_warehouse_and_second_product,
    product_num,
):
    if product_num == "1":
        product_id = first_category_first_product.id
    elif product_num == "2":
        product_id = first_category_second_product.id
    elif product_num == "3":
        product_id = second_category_first_product.id
    elif product_num == "4":
        product_id = first_category_third_product.id

    api_client.force_authenticate(staff_user_obj)
    response = api_client.get(f"/api/v1/stocks/?product={product_id}")

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    if product_num == "1":
        ids = {stock["id"] for stock in response_data}
        assert first_stock_with_first_warehouse_and_first_product.id in ids
        assert second_stock_with_first_warehouse_and_second_product.id not in ids
        assert third_stock_with_third_warehouse_and_third_product.id not in ids
        assert fourth_stock_with_second_warehouse_and_second_product.id not in ids
    elif product_num == "2":
        ids = {stock["id"] for stock in response_data}
        assert first_stock_with_first_warehouse_and_first_product.id not in ids
        assert second_stock_with_first_warehouse_and_second_product.id in ids
        assert third_stock_with_third_warehouse_and_third_product.id not in ids
        assert fourth_stock_with_second_warehouse_and_second_product.id in ids
    elif product_num == "3":
        ids = {stock["id"] for stock in response_data}
        assert first_stock_with_first_warehouse_and_first_product.id not in ids
        assert second_stock_with_first_warehouse_and_second_product.id not in ids
        assert third_stock_with_third_warehouse_and_third_product.id in ids
        assert fourth_stock_with_second_warehouse_and_second_product.id not in ids
    elif product_num == "4":
        assert response_data == []


@pytest.mark.parametrize(
    "quantity",
    [
        10,
        20,
        40,
        999,
    ]
)
def test_stock_filter_quantity(
    api_client,
    staff_user_obj,
    first_stock_with_first_warehouse_and_first_product,
    second_stock_with_first_warehouse_and_second_product,
    third_stock_with_third_warehouse_and_third_product,
    fourth_stock_with_second_warehouse_and_second_product,
    quantity,
):

    api_client.force_authenticate(staff_user_obj)
    response = api_client.get(f"/api/v1/stocks/?quantity={quantity}")

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    if quantity == 10:
        ids = {stock["id"] for stock in response_data}
        assert first_stock_with_first_warehouse_and_first_product.id in ids
        assert second_stock_with_first_warehouse_and_second_product.id not in ids
        assert third_stock_with_third_warehouse_and_third_product.id not in ids
        assert fourth_stock_with_second_warehouse_and_second_product.id not in ids
    elif quantity == 20:
        ids = {stock["id"] for stock in response_data}
        assert first_stock_with_first_warehouse_and_first_product.id not in ids
        assert second_stock_with_first_warehouse_and_second_product.id in ids
        assert third_stock_with_third_warehouse_and_third_product.id not in ids
        assert fourth_stock_with_second_warehouse_and_second_product.id not in ids
    elif quantity == 40:
        ids = {stock["id"] for stock in response_data}
        assert first_stock_with_first_warehouse_and_first_product.id not in ids
        assert second_stock_with_first_warehouse_and_second_product.id not in ids
        assert third_stock_with_third_warehouse_and_third_product.id not in ids
        assert fourth_stock_with_second_warehouse_and_second_product.id in ids
    elif quantity == 999:
        assert response_data == []


@pytest.mark.parametrize(
    "reserved_quantity",
    [
        2,
        5,
        20,
        999,
    ]
)
def test_stock_filter_reserved_quantity(
    api_client,
    staff_user_obj,
    first_stock_with_first_warehouse_and_first_product,
    second_stock_with_first_warehouse_and_second_product,
    third_stock_with_third_warehouse_and_third_product,
    fourth_stock_with_second_warehouse_and_second_product,
    reserved_quantity,
):

    api_client.force_authenticate(staff_user_obj)
    response = api_client.get(f"/api/v1/stocks/?reserved_quantity={reserved_quantity}")

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    if reserved_quantity == 2:
        ids = {stock["id"] for stock in response_data}
        assert first_stock_with_first_warehouse_and_first_product.id in ids
        assert second_stock_with_first_warehouse_and_second_product.id not in ids
        assert third_stock_with_third_warehouse_and_third_product.id not in ids
        assert fourth_stock_with_second_warehouse_and_second_product.id not in ids
    elif reserved_quantity == 5:
        ids = {stock["id"] for stock in response_data}
        assert first_stock_with_first_warehouse_and_first_product.id not in ids
        assert second_stock_with_first_warehouse_and_second_product.id in ids
        assert third_stock_with_third_warehouse_and_third_product.id not in ids
        assert fourth_stock_with_second_warehouse_and_second_product.id not in ids
    elif reserved_quantity == 20:
        ids = {stock["id"] for stock in response_data}
        assert first_stock_with_first_warehouse_and_first_product.id not in ids
        assert second_stock_with_first_warehouse_and_second_product.id not in ids
        assert third_stock_with_third_warehouse_and_third_product.id not in ids
        assert fourth_stock_with_second_warehouse_and_second_product.id in ids
    elif reserved_quantity == 999:
        assert response_data == []


@pytest.mark.parametrize(
    "quantity_min, quantity_max",
    [
        (10, ""),
        (20, ""),
        ("", 20),
        ("", 40),
        (20, 30),
        (41, ""),
    ]
)
def test_stock_filter_quantity_min_quantity_max(
    api_client,
    staff_user_obj,
    first_stock_with_first_warehouse_and_first_product,
    second_stock_with_first_warehouse_and_second_product,
    third_stock_with_third_warehouse_and_third_product,
    fourth_stock_with_second_warehouse_and_second_product,
    quantity_min,
    quantity_max,
):

    api_client.force_authenticate(staff_user_obj)
    response = api_client.get(
        f"/api/v1/stocks/?quantity_min={quantity_min}&quantity_max={quantity_max}"
    )

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    if quantity_min == 10 and quantity_max == "":
        ids = {stock["id"] for stock in response_data}
        assert first_stock_with_first_warehouse_and_first_product.id in ids
        assert second_stock_with_first_warehouse_and_second_product.id in ids
        assert third_stock_with_third_warehouse_and_third_product.id in ids
        assert fourth_stock_with_second_warehouse_and_second_product.id in ids
    elif quantity_min == 20 and quantity_max == "":
        ids = {stock["id"] for stock in response_data}
        assert first_stock_with_first_warehouse_and_first_product.id not in ids
        assert second_stock_with_first_warehouse_and_second_product.id in ids
        assert third_stock_with_third_warehouse_and_third_product.id in ids
        assert fourth_stock_with_second_warehouse_and_second_product.id in ids
    elif quantity_min == "" and quantity_max == 20:
        ids = {stock["id"] for stock in response_data}
        assert first_stock_with_first_warehouse_and_first_product.id in ids
        assert second_stock_with_first_warehouse_and_second_product.id in ids
        assert third_stock_with_third_warehouse_and_third_product.id not in ids
        assert fourth_stock_with_second_warehouse_and_second_product.id not in ids
    elif quantity_min == "" and quantity_max == 40:
        ids = {stock["id"] for stock in response_data}
        assert first_stock_with_first_warehouse_and_first_product.id in ids
        assert second_stock_with_first_warehouse_and_second_product.id in ids
        assert third_stock_with_third_warehouse_and_third_product.id in ids
        assert fourth_stock_with_second_warehouse_and_second_product.id in ids
    elif quantity_min == 20 and quantity_max == 30:
        ids = {stock["id"] for stock in response_data}
        assert first_stock_with_first_warehouse_and_first_product.id not in ids
        assert second_stock_with_first_warehouse_and_second_product.id in ids
        assert third_stock_with_third_warehouse_and_third_product.id in ids
        assert fourth_stock_with_second_warehouse_and_second_product.id not in ids
    elif quantity_min == 41:
        assert response_data == []


@pytest.mark.parametrize(
    "reserved_quantity_min, reserved_quantity_max",
    [
        (2, ""),
        (5, ""),
        ("", 10),
        ("", 20),
        (5, 10),
        (21, ""),
    ]
)
def test_stock_filter_reserved_quantity_min_reserved_quantity_max(
    api_client,
    staff_user_obj,
    first_stock_with_first_warehouse_and_first_product,
    second_stock_with_first_warehouse_and_second_product,
    third_stock_with_third_warehouse_and_third_product,
    fourth_stock_with_second_warehouse_and_second_product,
    reserved_quantity_min,
    reserved_quantity_max,
):

    api_client.force_authenticate(staff_user_obj)
    response = api_client.get(
        f"/api/v1/stocks/?reserved_quantity_min={reserved_quantity_min}&reserved_quantity_max={reserved_quantity_max}"
    )

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    if reserved_quantity_min == 2 and reserved_quantity_max == "":
        ids = {stock["id"] for stock in response_data}
        assert first_stock_with_first_warehouse_and_first_product.id in ids
        assert second_stock_with_first_warehouse_and_second_product.id in ids
        assert third_stock_with_third_warehouse_and_third_product.id in ids
        assert fourth_stock_with_second_warehouse_and_second_product.id in ids
    elif reserved_quantity_min == 5 and reserved_quantity_max == "":
        ids = {stock["id"] for stock in response_data}
        assert first_stock_with_first_warehouse_and_first_product.id not in ids
        assert second_stock_with_first_warehouse_and_second_product.id in ids
        assert third_stock_with_third_warehouse_and_third_product.id in ids
        assert fourth_stock_with_second_warehouse_and_second_product.id in ids
    elif reserved_quantity_min == "" and reserved_quantity_max == 10:
        ids = {stock["id"] for stock in response_data}
        assert first_stock_with_first_warehouse_and_first_product.id in ids
        assert second_stock_with_first_warehouse_and_second_product.id in ids
        assert third_stock_with_third_warehouse_and_third_product.id  in ids
        assert fourth_stock_with_second_warehouse_and_second_product.id not in ids
    elif reserved_quantity_min == "" and reserved_quantity_max == 20:
        ids = {stock["id"] for stock in response_data}
        assert first_stock_with_first_warehouse_and_first_product.id in ids
        assert second_stock_with_first_warehouse_and_second_product.id in ids
        assert third_stock_with_third_warehouse_and_third_product.id in ids
        assert fourth_stock_with_second_warehouse_and_second_product.id in ids
    elif reserved_quantity_min == 5 and reserved_quantity_max == 10:
        ids = {stock["id"] for stock in response_data}
        assert first_stock_with_first_warehouse_and_first_product.id not in ids
        assert second_stock_with_first_warehouse_and_second_product.id in ids
        assert third_stock_with_third_warehouse_and_third_product.id in ids
        assert fourth_stock_with_second_warehouse_and_second_product.id not in ids
    elif reserved_quantity_min == 21:
        assert response_data == []


def test_stock_filter_combination(
    api_client,
    staff_user_obj,
    first_warehouse,
    second_warehouse,
    third_warehouse,
    fourth_warehouse,
    first_category_third_product,
    first_category_second_product,
    second_category_first_product,
    first_category_first_product,
    first_stock_with_first_warehouse_and_first_product,
    second_stock_with_first_warehouse_and_second_product,
    third_stock_with_third_warehouse_and_third_product,
    fourth_stock_with_second_warehouse_and_second_product,
):

    api_client.force_authenticate(staff_user_obj)
    response = api_client.get(
        f"/api/v1/stocks/?warehouse={first_warehouse.id}&product={first_category_second_product.id}&quantity_min=20&reserved_quantity_max=5"
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    ids = {stock["id"] for stock in response_data}
    assert first_stock_with_first_warehouse_and_first_product.id not in ids
    assert second_stock_with_first_warehouse_and_second_product.id in ids
    assert third_stock_with_third_warehouse_and_third_product.id not in ids
    assert fourth_stock_with_second_warehouse_and_second_product.id not in ids


def test_manager_cant_bypass_stock_isolation_with_filter(
    api_client,
    user_obj,
    second_user_obj,
    first_warehouse,
    second_warehouse,
    third_warehouse,
    fourth_warehouse,
    first_category_third_product,
    first_category_second_product,
    second_category_first_product,
    first_category_first_product,
    first_stock_with_first_warehouse_and_first_product,
    second_stock_with_first_warehouse_and_second_product,
    third_stock_with_third_warehouse_and_third_product,
    fourth_stock_with_second_warehouse_and_second_product,
    first_warehouse_manager_assignment,
    third_warehouse_manager_assignment_another_user
):

    api_client.force_authenticate(user_obj)
    response = api_client.get(
        f"/api/v1/stocks/?warehouse={third_warehouse.id}"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []
