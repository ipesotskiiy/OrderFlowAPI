import pytest
from rest_framework import status
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

pytestmark = pytest.mark.django_db

def test_logout_blacklists_refresh_token(
    api_client,
    user_obj,
    access_and_refresh_tokens,
):
    refresh_string = access_and_refresh_tokens["refresh"]
    refresh_token = RefreshToken(refresh_string)

    response = api_client.post(
        "/api/v1/auth/logout/",
        data={
            "refresh": refresh_string,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    outstanding_token = OutstandingToken.objects.get(
        jti=refresh_token["jti"],
    )

    assert BlacklistedToken.objects.filter(
        token=outstanding_token,
    ).exists()


def test_logged_out_refresh_token_cannot_be_used(
    api_client,
    user_obj,
    access_and_refresh_tokens,
):
    refresh_string = access_and_refresh_tokens["refresh"]
    response = api_client.post(
        "/api/v1/auth/logout/",
        data={
            "refresh": refresh_string,
        },
    )
    assert response.status_code == status.HTTP_200_OK

    response = api_client.post(
        "/api/v1/auth/refresh/",
        data={
            "refresh": refresh_string,
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Token is blacklisted"


def test_logout_rejects_invalid_refresh_token(
    api_client,
    user_obj,
):
    response = api_client.post(
        "/api/v1/auth/logout/",
        data={
            "refresh": "abc",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Token is invalid"


def test_logout_does_not_invalidate_access_token(
    api_client,
    user_obj,
    access_and_refresh_tokens,
):
    access_token = access_and_refresh_tokens["access"]
    refresh_token = access_and_refresh_tokens["refresh"]

    response = api_client.post(
        "/api/v1/auth/logout/",
        data={
            "refresh": refresh_token,
        },
    )
    assert response.status_code == status.HTTP_200_OK

    response = api_client.get(
        "/api/v1/auth/me/",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )
    assert response.status_code == status.HTTP_200_OK
