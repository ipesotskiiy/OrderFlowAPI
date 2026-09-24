import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_login_returns_access_and_refresh_tokens(api_client, user_obj, user_data):
    response = api_client.post(
        "/api/v1/auth/login/",
        data={
            "email": user_obj.email,
            "password": user_data["password"]
        }
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert "access" in response_data
    assert response_data["access"] is not None
    assert "refresh" in response_data
    assert response_data["refresh"] is not None


def test_login_rejects_wrong_email(api_client, user_obj, user_data):
    response = api_client.post(
        "/api/v1/auth/login/",
        data={
            "email": "wrong_email@mail.ru",
            "password": user_data["password"]
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert (response.json()["detail"] ==
            "No active account found with the given credentials")


def test_login_rejects_wrong_password(api_client, user_obj, user_data):
    response = api_client.post(
        "/api/v1/auth/login/",
        data={
            "email": user_obj.email,
            "password": "wrong_password"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert (response.json()["detail"] ==
            "No active account found with the given credentials")


def test_login_rejects_inactive_user(api_client, user_obj, user_data):
    user_obj.is_active = False
    user_obj.save()
    response = api_client.post(
        "/api/v1/auth/login/",
        data={
            "email": user_obj.email,
            "password": user_data["password"]
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert (response.json()["detail"] ==
            "No active account found with the given credentials")
