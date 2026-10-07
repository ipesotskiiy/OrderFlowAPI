from datetime import date
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from accounts.models import User
from catalog.models import Category, Product
from stocks.models import Stock
from warehouses.models import Warehouse, WarehouseManagerAssignment


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
def second_user_obj(user_data):
    user = User.objects.create_user(
        email="test_another_user@mail.com",
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


@pytest.fixture
def first_warehouse():
    warehouse_data = {
        "name": "first_warehouse",
        "code": "WR1-A1",
        "address": "Rostov-on-Don, bolshaya sadovaya street 34",
    }

    return Warehouse.objects.create(**warehouse_data)


@pytest.fixture
def second_warehouse():
    warehouse_data = {
        "name": "second_warehouse",
        "code": "WR1-A2",
        "address": "Rostov-on-Don, bolshaya sadovaya street 38",
    }

    return Warehouse.objects.create(**warehouse_data)


@pytest.fixture
def first_warehouse_manager_assignment(
    first_warehouse,
    user_obj,
):
    warehouse_manager_assignment_data = {
        "warehouse": first_warehouse,
        "user": user_obj
    }
    return WarehouseManagerAssignment.objects.create(
        **warehouse_manager_assignment_data
    )

@pytest.fixture
def second_warehouse_manager_assignment(
    second_warehouse,
    user_obj,
):
    warehouse_manager_assignment_data = {
        "warehouse": second_warehouse,
        "user": user_obj
    }
    return WarehouseManagerAssignment.objects.create(
        **warehouse_manager_assignment_data
    )

@pytest.fixture
def second_warehouse_manager_assignment_another_user(
    second_warehouse,
    second_user_obj,
):
    warehouse_manager_assignment_data = {
        "warehouse": second_warehouse,
        "user": second_user_obj
    }
    return WarehouseManagerAssignment.objects.create(
        **warehouse_manager_assignment_data
    )

@pytest.fixture
def third_warehouse():
    warehouse_data = {
        "name": "third_warehouse",
        "code": "WR1-A3",
        "address": "Rostov-on-Don, bolshaya sadovaya street 38",
    }

    return Warehouse.objects.create(**warehouse_data)

@pytest.fixture
def fourth_warehouse():
    warehouse_data = {
        "name": "fourth_warehouse",
        "code": "WR1-A4",
        "address": "Rostov-on-Don, bolshaya sadovaya street 38",
    }

    return Warehouse.objects.create(**warehouse_data)

@pytest.fixture
def third_warehouse_manager_assignment_another_user(
    third_warehouse,
    second_user_obj,
):
    warehouse_manager_assignment_data = {
        "warehouse": third_warehouse,
        "user": second_user_obj
    }
    return WarehouseManagerAssignment.objects.create(
        **warehouse_manager_assignment_data
    )


@pytest.fixture
def first_stock_with_first_warehouse_and_first_product(
    first_warehouse,
    first_category_first_product,
):
    stock_data = {
        "warehouse": first_warehouse,
        "product": first_category_first_product,
        "quantity": 10,
        "reserved_quantity": 2,
    }

    return Stock.objects.create(**stock_data)


@pytest.fixture
def second_stock_with_first_warehouse_and_second_product(
    first_warehouse,
    first_category_second_product,
):
    stock_data = {
        "warehouse": first_warehouse,
        "product": first_category_second_product,
        "quantity": 20,
        "reserved_quantity": 5,
    }

    return Stock.objects.create(**stock_data)


@pytest.fixture
def third_stock_with_third_warehouse_and_third_product(
    third_warehouse,
    second_category_first_product,
):
    stock_data = {
        "warehouse": third_warehouse,
        "product": second_category_first_product,
        "quantity": 30,
        "reserved_quantity": 10,
    }

    return Stock.objects.create(**stock_data)


@pytest.fixture
def fourth_stock_with_second_warehouse_and_second_product(
    second_warehouse,
    first_category_second_product,
):
    stock_data = {
        "warehouse": second_warehouse,
        "product": first_category_second_product,
        "quantity": 40,
        "reserved_quantity": 20,
    }

    return Stock.objects.create(**stock_data)


@pytest.fixture
def first_category_third_product(first_category):
    product_data = {
        "name": "Fanta",
        "manufacturer_name": "Кока Кола инк",
        "category": first_category,
        "minimum_age": 7,
        "sku": "H2O-8",
        "price": Decimal("100"),
        "weight_kg": Decimal("0.5"),
        "height_cm": Decimal("30"),
        "color": "black",
    }
    return Product.objects.create(**product_data)
