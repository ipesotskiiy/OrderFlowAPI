from datetime import date

import pytest
from rest_framework.test import APIClient

from accounts.models import User


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
