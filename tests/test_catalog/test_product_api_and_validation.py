from decimal import Decimal

import pytest
from rest_framework import status

from catalog.models import Product

pytestmark = pytest.mark.django_db

def test_success_product_create(api_client, first_category, staff_user_obj):
    product_data = {
        "name": "Кока Кола",
        "manufacturer_name": "Кока Кола инк",
        "category": first_category.id,
        "minimum_age": 7,
        "sku": "H2O-1",
        "price": Decimal("100"),
        "weight_kg": Decimal("0.5"),
        "height_cm": Decimal("30"),
        "color": "black",
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.post(
        "/api/v1/catalog/products/",
        data=product_data,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    product_obj = Product.objects.get(id=response_data["id"])
    assert product_obj.name == product_data["name"]
    assert product_obj.manufacturer_name == product_data["manufacturer_name"]
    assert product_obj.category.id == product_data["category"]
    assert product_obj.minimum_age == product_data["minimum_age"]
    assert product_obj.sku == product_data["sku"]
    assert product_obj.price == product_data["price"]
    assert product_obj.weight_kg == product_data["weight_kg"]
    assert product_obj.height_cm == product_data["height_cm"]
    assert product_obj.color == product_data["color"]


def test_error_product_creation_with_wrong_category(api_client, staff_user_obj):
    product_data = {
        "name": "Кока Кола",
        "manufacturer_name": "Кока Кола инк",
        "category": 1,
        "minimum_age": 7,
        "sku": "H2O-1",
        "price": Decimal("100"),
        "weight_kg": Decimal("0.5"),
        "height_cm": Decimal("30"),
        "color": "black",
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.post(
        "/api/v1/catalog/products/",
        data=product_data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(Product.objects.all()) == 0


def test_error_product_creation_with_duplicate_sku(
    api_client,
    first_category,
    staff_user_obj,
    first_category_first_product,
):
    product_data = {
        "name": "Кока Кола",
        "manufacturer_name": "Кока Кола инк",
        "category": first_category.id,
        "minimum_age": 7,
        "sku": first_category_first_product.sku,
        "price": Decimal("100"),
        "weight_kg": Decimal("0.5"),
        "height_cm": Decimal("30"),
        "color": "black",
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.post(
        "/api/v1/catalog/products/",
        data=product_data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(Product.objects.all()) == 1

@pytest.mark.parametrize(
    "price, weight_kg, height_cm",
    [
        ("0", "0.5", "30"),
        ("-1", "0.5", "30"),
        ("100", "0", "30"),
        ("100", "-1", "30"),
        ("100", "0.5", "0"),
        ("100", "0.5", "-1")
    ]
)
def test_error_product_creation_with_wrong_constraint(
    api_client,
    first_category,
    staff_user_obj,
    price,
    weight_kg,
    height_cm,
):
    product_data = {
        "name": "Кока Кола",
        "manufacturer_name": "Кока Кола инк",
        "category": first_category.id,
        "minimum_age": 7,
        "sku": "H2O-1",
        "price": Decimal(price),
        "weight_kg": Decimal(weight_kg),
        "height_cm": Decimal(height_cm),
        "color": "black",
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.post(
        "/api/v1/catalog/products/",
        data=product_data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(Product.objects.all()) == 0


def test_product_create_check_default_minimum_age_and_is_active(
        api_client,
        first_category,
        staff_user_obj,
):
    product_data = {
        "name": "Кока Кола",
        "manufacturer_name": "Кока Кола инк",
        "category": first_category.id,
        "sku": "H2O-1",
        "price": Decimal("100"),
        "weight_kg": Decimal("0.5"),
        "height_cm": Decimal("30"),
        "color": "black",
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.post(
        "/api/v1/catalog/products/",
        data=product_data,
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED

    response_data = response.json()
    product_obj = Product.objects.get(id=response_data["id"])
    assert product_obj.minimum_age == 0
    assert product_obj.is_active is True


def test_success_product_create_without_color(
        api_client,
        first_category,
        staff_user_obj
):
    product_data = {
        "name": "Кока Кола",
        "manufacturer_name": "Кока Кола инк",
        "category": first_category.id,
        "minimum_age": 7,
        "sku": "H2O-1",
        "price": Decimal("100"),
        "weight_kg": Decimal("0.5"),
        "height_cm": Decimal("30"),
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.post(
        "/api/v1/catalog/products/",
        data=product_data,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    product_obj = Product.objects.get(id=response_data["id"])
    assert product_obj.color == ""

def test_product_minimum_age_not_copy_category_minimum_age(
        api_client,
        first_category,
        staff_user_obj
):
    product_data = {
        "name": "Кока Кола",
        "manufacturer_name": "Кока Кола инк",
        "category": first_category.id,
        "minimum_age": 7,
        "sku": "H2O-1",
        "price": Decimal("100"),
        "weight_kg": Decimal("0.5"),
        "height_cm": Decimal("30"),
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.post(
        "/api/v1/catalog/products/",
        data=product_data,
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED

    response_data = response.json()
    product_obj = Product.objects.get(id=response_data["id"])
    assert product_obj.minimum_age != first_category.minimum_age
    assert product_obj.minimum_age == product_data["minimum_age"]


@pytest.mark.parametrize(
    "required_field_name",
    [
        "name",
        "manufacturer_name",
        "category",
        "sku",
        "price",
        "weight_kg",
        "height_cm",
    ],
)
def test_error_product_creation_without_required_field(
    api_client,
    staff_user_obj,
    first_category,
    required_field_name,
):
    product_data = {
        "name": "Кока Кола",
        "manufacturer_name": "Кока Кола инк",
        "category": first_category.id,
        "sku": "H2O-1",
        "price": Decimal("100"),
        "weight_kg": Decimal("0.5"),
        "height_cm": Decimal("30"),
    }

    product_data.pop(required_field_name)

    api_client.force_authenticate(staff_user_obj)
    response = api_client.post(
        "/api/v1/catalog/products/",
        data=product_data,
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(Product.objects.all()) == 0


def test_error_product_creation_with_invalid_is_active(
        api_client,
        first_category,
        staff_user_obj
):
    product_data = {
        "name": "Кока Кола",
        "manufacturer_name": "Кока Кола инк",
        "category": first_category.id,
        "minimum_age": 7,
        "sku": "H2O-1",
        "price": Decimal("100"),
        "weight_kg": Decimal("0.5"),
        "height_cm": Decimal("30"),
        "is_active": "abc"
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.post(
        "/api/v1/catalog/products/",
        data=product_data,
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(Product.objects.all()) == 0


@pytest.mark.parametrize(
    "price, weight_kg, height_cm",
    [
        ("100000000000.00", "0.5", "30"),
        ("100000000.000", "0.5", "30"),
        ("100", "1000000000.00", "30"),
        ("100", "10000000.000", "30"),
        ("100", "0.5", "1000000000.00"),
        ("100", "0.5", "10000000.000")
    ]
)
def test_error_product_creation_big_decimal_value(
    api_client,
    first_category,
    staff_user_obj,
    price,
    weight_kg,
    height_cm,
):
    product_data = {
        "name": "Кока Кола",
        "manufacturer_name": "Кока Кола инк",
        "category": first_category.id,
        "minimum_age": 7,
        "sku": "H2O-1",
        "price": Decimal(price),
        "weight_kg": Decimal(weight_kg),
        "height_cm": Decimal(height_cm),
        "color": "black",
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.post(
        "/api/v1/catalog/products/",
        data=product_data,
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(Product.objects.all()) == 0


def test_anonymous_cant_get_list_product(
    api_client,
    first_category_first_product,
    second_category_first_product
):
    response = api_client.get(
        "/api/v1/catalog/products/"
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Authentication credentials were not provided."


def test_anonymous_cant_get_retrieve_product(api_client, first_category_first_product):
    response = api_client.get(
        f"/api/v1/catalog/products/{first_category_first_product.id}/"
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Authentication credentials were not provided."


def test_anonymous_cant_create_product(api_client, first_category):
    product_data = {
        "name": "Кока Кола",
        "manufacturer_name": "Кока Кола инк",
        "category": first_category.id,
        "sku": "H2O-1",
        "price": Decimal("100"),
        "weight_kg": Decimal("0.5"),
        "height_cm": Decimal("30"),
        }
    response = api_client.post(
        "/api/v1/catalog/products/",
        data=product_data,
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Authentication credentials were not provided."
    assert len(Product.objects.all()) == 0


def test_anonymous_cant_update_product(api_client, first_category_first_product):
    product_data = {
            "name": "Кока Колка",
        }
    response = api_client.patch(
        f"/api/v1/catalog/products/{first_category_first_product.id}/",
        data=product_data,
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Authentication credentials were not provided."
    assert (Product.objects.get(id=first_category_first_product.id).name ==
            first_category_first_product.name)


def test_anonymous_cant_delete_product(
    api_client,
    first_category_first_product
):
    response = api_client.delete(
        f"/api/v1/catalog/products/{first_category_first_product.id}/",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Authentication credentials were not provided."
    assert len(Product.objects.all()) == 1


def test_authenticated_can_get_list_product(
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
    assert len(response_data) == 2

    ids = {product["id"] for product in response_data}
    assert first_category_first_product.id in ids
    assert second_category_first_product.id in ids


def test_authenticated_can_get_retrieve_product(
    api_client,
    user_obj,
    first_category_first_product,
):
    api_client.force_authenticate(user_obj)
    response = api_client.get(
        f"/api/v1/catalog/products/{first_category_first_product.id}/"
    )
    assert response.status_code == status.HTTP_200_OK
    product_obj = Product.objects.get(id=response.json()["id"])
    assert product_obj == first_category_first_product


def test_authenticated_cant_create_product(
    api_client,
    user_obj,
    first_category,
):
    product_data = {
            "name": "Кока Кола",
            "manufacturer_name": "Кока Кола инк",
            "category": first_category.id,
            "sku": "H2O-1",
            "price": Decimal("100"),
            "weight_kg": Decimal("0.5"),
            "height_cm": Decimal("30"),
        }
    api_client.force_authenticate(user_obj)
    response = api_client.post(
        "/api/v1/catalog/products/",
        data=product_data,
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == ("You do not have permission "
                                         "to perform this action.")
    assert len(Product.objects.all()) == 0


def test_authenticated_cant_update_product(
    api_client,
    user_obj,
    first_category_first_product,
):
    product_data = {
            "name": "Кока Колка",
        }
    api_client.force_authenticate(user_obj)
    response = api_client.patch(
        f"/api/v1/catalog/products/{first_category_first_product.id}/",
        data=product_data,
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == ("You do not have permission "
                                         "to perform this action.")
    assert (Product.objects.get(id=first_category_first_product.id).name ==
            first_category_first_product.name)


def test_authenticated_cant_delete_product(
    api_client,
    user_obj,
    first_category_first_product,
):
    api_client.force_authenticate(user_obj)
    response = api_client.delete(
        f"/api/v1/catalog/products/{first_category_first_product.id}/",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == ("You do not have permission "
                                         "to perform this action.")
    assert len(Product.objects.all()) == 1


def test_staff_can_get_list_product(
    api_client,
    staff_user_obj,
    first_category_first_product,
    second_category_first_product,
):
    api_client.force_authenticate(staff_user_obj)
    response = api_client.get(
        "/api/v1/catalog/products/"
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert len(response_data) == 2

    ids = {product["id"] for product in response_data}
    assert first_category_first_product.id in ids
    assert second_category_first_product.id in ids


def test_staff_can_get_retrieve_product(
    api_client,
    staff_user_obj,
    first_category_first_product,
):
    api_client.force_authenticate(staff_user_obj)
    response = api_client.get(
        f"/api/v1/catalog/products/{first_category_first_product.id}/"
    )
    assert response.status_code == status.HTTP_200_OK
    product_obj = Product.objects.get(id=response.json()["id"])
    assert product_obj == first_category_first_product


def test_staff_can_delete_product(
    api_client,
    staff_user_obj,
    first_category_first_product,
):
    api_client.force_authenticate(staff_user_obj)
    response = api_client.delete(
        f"/api/v1/catalog/products/{first_category_first_product.id}/",
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(Product.objects.all()) == 0


def test_success_change_product_name(
    api_client,
    staff_user_obj,
    first_category_first_product,
):
    product_data = {
            "name": "Кока Колка",
        }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.patch(
        f"/api/v1/catalog/products/{first_category_first_product.id}/",
        data=product_data,
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    product_obj = Product.objects.get(id=response.json()["id"])
    assert product_obj.name == product_data["name"]
    assert (product_obj.manufacturer_name ==
            first_category_first_product.manufacturer_name)
    assert product_obj.category == first_category_first_product.category
    assert product_obj.minimum_age == first_category_first_product.minimum_age
    assert product_obj.sku == first_category_first_product.sku
    assert product_obj.price == first_category_first_product.price
    assert product_obj.weight_kg == first_category_first_product.weight_kg
    assert product_obj.height_cm == first_category_first_product.height_cm
    assert product_obj.color == first_category_first_product.color
    assert product_obj.is_active == first_category_first_product.is_active

def test_success_change_product_color(
    api_client,
    staff_user_obj,
    first_category_first_product,
):
    product_data = {
            "color": "red",
        }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.patch(
        f"/api/v1/catalog/products/{first_category_first_product.id}/",
        data=product_data,
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    product_obj = Product.objects.get(id=response.json()["id"])
    assert product_obj.color == product_data["color"]


@pytest.mark.parametrize(
    "price, weight_kg, height_cm",
    [
        ("0", "0.5", "30"),
        ("-1", "0.5", "30"),
        ("100", "0", "30"),
        ("100", "-1", "30"),
        ("100", "0.5", "0"),
        ("100", "0.5", "-1")
    ]
)
def test_error_change_product_constraints(
    api_client,
    first_category_first_product,
    staff_user_obj,
    price,
    weight_kg,
    height_cm,
):
    product_data = {
        "price": Decimal(price),
        "weight_kg": Decimal(weight_kg),
        "height_cm": Decimal(height_cm),
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.patch(
        f"/api/v1/catalog/products/{first_category_first_product.id}/",
        data=product_data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    product_obj = Product.objects.get(id=first_category_first_product.id)
    assert product_obj.price == first_category_first_product.price
    assert product_obj.weight_kg == first_category_first_product.weight_kg
    assert product_obj.height_cm == first_category_first_product.height_cm
