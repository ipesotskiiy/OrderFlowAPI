import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_me_returns_authenticated_user(
    api_client,
    user_obj,
    access_and_refresh_tokens,
):
    access_token = access_and_refresh_tokens["access"]
    response = api_client.get(
        "/api/v1/auth/me/",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    response_user_data = response.json()["user"]
    for key in response_user_data.keys():
        assert key in ("email", "first_name", "last_name")
    assert response_user_data["email"] == user_obj.email
    assert response_user_data["first_name"] == user_obj.first_name
    assert response_user_data["last_name"] == user_obj.last_name


def test_me_rejects_unauthenticated_request(
    api_client,
    user_obj,
):
    response = api_client.get("/api/v1/auth/me/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Authentication credentials were not provided."


def test_me_rejects_refresh_token_as_authorization(
    api_client,
    user_obj,
    access_and_refresh_tokens,
):
    refresh_token = access_and_refresh_tokens["refresh"]
    response = api_client.get(
        "/api/v1/auth/me/",
        headers={
            "Authorization": f"Bearer {refresh_token}"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Given token not valid for any token type"


def test_me_rejects_access_token_of_inactive_user(
    api_client,
    user_obj,
    access_and_refresh_tokens,
):
    user_obj.is_active = False
    user_obj.save()
    access_token = access_and_refresh_tokens["access"]
    response = api_client.get(
        "/api/v1/auth/me/",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "User is inactive"
