from datetime import date
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from accounts.models import User
from catalog.models import Category, Product


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        "email": "test_user@mail.com",
        "first_name": "Igoresha_man",
        "last_name": "Pesotskiiy",
        "birth_date": date(1998, 8, 20),
        "password": "test_password",
    }


@pytest.fixture
def user_obj(user_data):
    user = User.objects.create_user(
        email=user_data["email"],
        password=user_data["password"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        birth_date=user_data["birth_date"],
    )
    return user


@pytest.fixture
def access_and_refresh_tokens(api_client, user_obj, user_data):
    response = api_client.post(
        "/api/v1/auth/login/",
        data={
            "email": user_obj.email,
            "password": user_data["password"]
        }
    )
    return response.json()

@pytest.fixture
def first_category():
    category_data = {
        "name": "Напитки",
        "minimum_age": 12,
    }

    return Category.objects.create(**category_data)


@pytest.fixture
def first_category_first_product(first_category):
    product_data = {
        "name": "Кока Кола",
        "manufacturer_name": "Кока Кола инк",
        "category": first_category,
        "minimum_age": 7,
        "sku": "H2O-1",
        "price": Decimal("100"),
        "weight_kg": Decimal("0.5"),
        "height_cm": Decimal("30"),
        "color": "black",
    }
    return Product.objects.create(**product_data)


@pytest.fixture
def first_category_second_product(first_category):
    product_data = {
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
    return Product.objects.create(**product_data)


@pytest.fixture
def second_category():
    category_data = {
        "name": "Вода",
        "minimum_age": 0,
    }

    return Category.objects.create(**category_data)


@pytest.fixture
def second_category_first_product(second_category):
    product_data = {
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
    return Product.objects.create(**product_data)


@pytest.fixture
def staff_user_obj(user_data):
    user = User.objects.create_user(
        email="test_user_staff@mail.ru",
        password=user_data["password"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        birth_date=user_data["birth_date"],
        is_staff=True
    )
    return user
