from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework import status

from catalog.models import Category, Product

pytestmark = pytest.mark.django_db

@pytest.mark.parametrize(
    "expected_sku",
    [
        "H2O-1",
        "H2O-2",
        "missing"
    ]
)
def test_product_filter_category(
    api_client,
    user_obj,
    first_category,
    second_category,
    first_category_first_product,
    second_category_first_product,
    expected_sku,
):
    api_client.force_authenticate(user_obj)

    category_data = {
        "name": "Еда",
        "minimum_age": 0,
    }

    third_category = Category.objects.create(**category_data)

    if expected_sku == "H2O-1":
        category_id = first_category.id
    elif expected_sku == "H2O-2":
        category_id = second_category.id
    else:
        category_id = third_category.id
    response = api_client.get(
        f"/api/v1/catalog/products/?category={category_id}"
    )
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    if expected_sku in ("H2O-1", "H2O-2"):
        assert len(response_data) == 1
        product_obj = Product.objects.get(id=response_data[0]["id"])
        if expected_sku == "H2O-1":
            assert product_obj == first_category_first_product
        elif expected_sku == "H2O-2":
            assert product_obj == second_category_first_product
    elif expected_sku == "missing":
        assert response_data == []


@pytest.mark.parametrize(
    "is_active",
    [
        True,
        False,
    ]
)
def test_product_filter_is_active(
    api_client,
    user_obj,
    first_category,
    first_category_first_product,
    first_category_second_product,
    is_active,
):
    api_client.force_authenticate(user_obj)

    response = api_client.get(
        f"/api/v1/catalog/products/?is_active={is_active}&category={first_category.id}"
    )
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert len(response_data) == 1
    product_obj = Product.objects.get(id=response_data[0]["id"])
    if is_active is True:
       assert product_obj == first_category_first_product
    elif is_active is False:
       assert product_obj == first_category_second_product


@pytest.mark.parametrize(
    "minimum_age",
    [
        "7",
        "9",
        "2"
    ]
)
def test_product_filter_minimum_age(
    api_client,
    user_obj,
    first_category,
    first_category_first_product,
    first_category_second_product,
    minimum_age,
):
    api_client.force_authenticate(user_obj)

    response = api_client.get(
        f"/api/v1/catalog/products/?minimum_age={minimum_age}"
    )
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    if minimum_age in ("7", "9"):
        assert len(response_data) == 1
        product_obj = Product.objects.get(id=response_data[0]["id"])
        if minimum_age == "7":
            assert product_obj == first_category_first_product
        elif minimum_age == "9":
            assert product_obj == first_category_second_product
    else:
        assert response_data == []


@pytest.mark.parametrize(
    "price",
    [
        Decimal("100"),
        Decimal("90"),
    ]
)
def test_product_filter_exact_price(
    api_client,
    user_obj,
    first_category,
    first_category_first_product,
    first_category_second_product,
    price,
):
    api_client.force_authenticate(user_obj)

    response = api_client.get(
        f"/api/v1/catalog/products/?price={price}"
    )
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert len(response_data) == 1
    product_obj = Product.objects.get(id=response_data[0]["id"])
    if price == Decimal("100"):
        assert product_obj == first_category_first_product
    elif price == Decimal("90"):
        assert product_obj == first_category_second_product


def test_product_price_border(
    api_client,
    user_obj,
    first_category,
    first_category_first_product,
    first_category_second_product,
    second_category_first_product,
):
    api_client.force_authenticate(user_obj)

    response = api_client.get(
        "/api/v1/catalog/products/?price_min=90&price_max=100"
    )
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    ids = {product["id"] for product in response_data}
    assert first_category_first_product.id in ids
    assert first_category_second_product.id in ids
    assert second_category_first_product.id not in ids


def test_combination_product_filters_category_and_price_max(
    api_client,
    user_obj,
    first_category,
    first_category_first_product,
    first_category_second_product,
):
    api_client.force_authenticate(user_obj)

    response = api_client.get(
        f"/api/v1/catalog/products/?category={first_category.id}&price_max=95"
    )
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    ids = {product["id"] for product in response_data}
    assert first_category_first_product.id not in ids
    assert first_category_second_product.id in ids


@pytest.mark.parametrize(
    "product_name",
    [
        "борж",
        "Кола",
        "Апельсин",
    ]
)
def test_product_search_name(
    api_client,
    user_obj,
    first_category_first_product,
    second_category_first_product,
    product_name,
):
    api_client.force_authenticate(user_obj)

    response = api_client.get(
        f"/api/v1/catalog/products/?search={product_name}"
    )
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    if product_name in ("борж", "Кола"):
        assert len(response_data) == 1
        product_obj = Product.objects.get(id=response_data[0]["id"])
        if product_name == "борж":
            assert product_obj == second_category_first_product
        elif product_name == "Кола":
            assert product_obj == first_category_first_product
    elif product_name == "Апельсин":
        assert response_data == []


@pytest.mark.parametrize(
    "sku",
    [
        "h2O-1",
        "O-2",
        "missing"
    ]
)
def test_product_search_sku(
    api_client,
    user_obj,
    first_category_first_product,
    second_category_first_product,
    sku,
):
    api_client.force_authenticate(user_obj)

    response = api_client.get(
        f"/api/v1/catalog/products/?search={sku}"
    )
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    if sku in ("h2O-1", "O-2"):
        assert len(response_data) == 1
        product_obj = Product.objects.get(id=response_data[0]["id"])
        if sku == "h2O-1":
            assert product_obj == first_category_first_product
        elif sku == "O-2":
            assert product_obj == second_category_first_product
    elif sku == "missing":
        assert response_data == []


@pytest.mark.parametrize(
    "ordering_expression",
    [
        "price",
        "-price",
        "created_at",
        "-created_at",
        "name",
        "-name",
    ]
)
def test_product_ordering(
    api_client,
    user_obj,
    first_category,
    second_category,
    ordering_expression,
):
    first_product_data = {
        "name": "Пепси",
        "manufacturer_name": "Кока Кола инк",
        "category": first_category,
        "minimum_age": 9,
        "sku": "H2O-3",
        "price": Decimal("90"),
        "weight_kg": Decimal("0.5"),
        "height_cm": Decimal("30"),
        "color": "black",
        "is_active": False,
    }
    first_product_first_cat = Product.objects.create(**first_product_data)
    second_product_data = {
        "name": "Боржоми",
        "manufacturer_name": "ООО Боржоми",
        "category": second_category,
        "minimum_age": 7,
        "sku": "H2O-2",
        "price": Decimal("50"),
        "weight_kg": Decimal("0.5"),
        "height_cm": Decimal("30"),
        "color": "black",
    }
    first_product_second_cat = Product.objects.create(**second_product_data)

    base_time = timezone.now()

    Product.objects.filter(
        id=first_product_first_cat.id
    ).update(
        created_at=base_time - timedelta(seconds=1)
    )

    Product.objects.filter(
        id=first_product_second_cat.id
    ).update(
        created_at=base_time
    )

    first_product_first_cat.refresh_from_db()
    first_product_second_cat.refresh_from_db()

    api_client.force_authenticate(user_obj)

    response = api_client.get(
        f"/api/v1/catalog/products/?ordering={ordering_expression}"
    )
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert len(response_data) == 2
    if ordering_expression == "price":
        assert first_product_second_cat.name == response_data[0]["name"]
        assert first_product_first_cat.name == response_data[1]["name"]
    elif ordering_expression == "-price":
        assert first_product_first_cat.name == response_data[0]["name"]
        assert first_product_second_cat.name == response_data[1]["name"]
    elif ordering_expression == "created_at":
        assert response_data[0]["id"] == first_product_first_cat.id
        assert response_data[1]["id"] == first_product_second_cat.id
    elif ordering_expression == "-created_at":
        assert response_data[0]["id"] == first_product_second_cat.id
        assert response_data[1]["id"] == first_product_first_cat.id
    elif ordering_expression == "name":
        assert first_product_second_cat.name == response_data[0]["name"]
        assert first_product_first_cat.name  == response_data[1]["name"]
    elif ordering_expression == "-name":
        assert first_product_first_cat.name  == response_data[0]["name"]
        assert first_product_second_cat.name == response_data[1]["name"]


def test_product_ordering_disallowed_field(
    api_client,
    user_obj,
    first_category_first_product,
    second_category_first_product,
):
    api_client.force_authenticate(user_obj)

    response = api_client.get(
        "/api/v1/catalog/products/"
    )
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    response_disallowed_field = api_client.get(
        "/api/v1/catalog/products/?ordering=sku"
    )
    assert response_disallowed_field.status_code == status.HTTP_200_OK

    response_disallowed_field_data = response_disallowed_field.json()

    assert response_data == response_disallowed_field_data
