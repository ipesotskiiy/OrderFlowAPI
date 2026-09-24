from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

pytestmark = pytest.mark.django_db

def test_refresh_returns_new_access_and_refresh_tokens(
    api_client,
    user_obj,
    access_and_refresh_tokens
):
    refresh_token = access_and_refresh_tokens["refresh"]
    response = api_client.post(
        "/api/v1/auth/refresh/",
        data={
            "refresh": refresh_token
        }
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert "access" in response_data
    assert response_data["access"] is not None
    assert "refresh" in response_data
    assert response_data["refresh"] is not None


def test_refresh_blacklists_used_refresh_token(
    api_client,
    user_obj,
    access_and_refresh_tokens
):
    refresh_token = access_and_refresh_tokens["refresh"]

    response = api_client.post(
        "/api/v1/auth/refresh/",
        data={
            "refresh": refresh_token
        }
    )
    assert response.status_code == status.HTTP_200_OK

    response = api_client.post(
        "/api/v1/auth/refresh/",
        data={
            "refresh": refresh_token
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_accepts_rotated_refresh_token(
    api_client,
    user_obj,
    access_and_refresh_tokens
):
    old_refresh_token = access_and_refresh_tokens["refresh"]
    response = api_client.post(
        "/api/v1/auth/refresh/",
        data={
            "refresh": old_refresh_token
        }
    )
    assert response.status_code == status.HTTP_200_OK
    new_refresh = response.json()["refresh"]
    assert response.json()["refresh"] != old_refresh_token
    response = api_client.post(
        "/api/v1/auth/refresh/",
        data={
            "refresh": new_refresh
        }
    )
    assert response.status_code == status.HTTP_200_OK


def test_refresh_rejects_invalid_token(api_client, user_obj):
    response = api_client.post(
        "/api/v1/auth/refresh/",
        data={
            "refresh": "abc"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Token is invalid"


def test_refresh_rejects_expired_refresh_token(api_client, user_obj):
    refresh_token = RefreshToken.for_user(user_obj)

    refresh_token.set_exp(
        from_time=timezone.now(),
        lifetime=timedelta(seconds=-1),
    )
    response = api_client.post(
        "/api/v1/auth/refresh/",
        data={
            "refresh": str(refresh_token)
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Token is expired"


def test_refresh_rejects_access_token_instead_of_refresh(
    api_client,
    user_obj,
    access_and_refresh_tokens
):
    access_token = access_and_refresh_tokens["access"]
    response = api_client.post(
        "/api/v1/auth/refresh/",
        data={
            "refresh": access_token
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Token has wrong type"

