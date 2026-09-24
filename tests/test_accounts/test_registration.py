import pytest
from django.db import IntegrityError
from django.urls import reverse
from psycopg.errors import UniqueViolation
from rest_framework import status

from accounts.models import User
from accounts.serializers import UserRegistrationSerializer

pytestmark = pytest.mark.django_db


def test_registration_success(api_client, user_data):
    response = api_client.post(
        "/api/v1/auth/register/",
        data=user_data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()

    user = User.objects.get(email=user_data["email"])

    assert user is not None
    assert isinstance(user, User)
    assert user.email == user_data["email"]
    assert user.first_name == user_data["first_name"]
    assert user.last_name == user_data["last_name"]
    assert user.birth_date == user_data["birth_date"]
    assert "password" not in response_data
    assert "access" not in response_data
    assert "refresh" not in response_data


def test_registration_rejects_invalid_email(api_client, user_data):
    user_data["email"] = "abc"
    response = api_client.post(
        "/api/v1/auth/register/",
        data=user_data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["email"][0] == "Enter a valid email address."
    assert len(User.objects.all()) == 0


def test_registration_rejects_empty_email(api_client, user_data):
    user_data["email"] = ""
    response = api_client.post(
        "/api/v1/auth/register/",
        data=user_data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["email"][0] == "This field may not be blank."
    assert len(User.objects.all()) == 0


def test_registration_rejects_duplicate_email(api_client, user_data, user_obj):
    response = api_client.post(
        "/api/v1/auth/register/",
        data=user_data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["email"][0] == "This field must be unique."
    assert len(User.objects.all()) == 1


def test_registration_rejects_empty_first_name(api_client, user_data):
    user_data["first_name"] = ""
    response = api_client.post(
        "/api/v1/auth/register/",
        data=user_data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["first_name"][0] == "This field may not be blank."
    assert len(User.objects.all()) == 0


def test_registration_rejects_too_long_first_name(api_client, user_data):
    user_data["first_name"] = "veeeeeeeeeeryyyyyyyyyy loooooooooong naaaaaaaaameeeeeee"
    response = api_client.post(
        "/api/v1/auth/register/",
        data=user_data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (response.json()["first_name"][0] ==
            "Ensure this field has no more than 25 characters.")
    assert len(User.objects.all()) == 0


def test_registration_rejects_too_long_middle_name(api_client, user_data):
    user_data["middle_name"] = "veeeeeeeeeeryyyyyyyyyy loooooooooong naaaaaaaaameeeeeee"
    response = api_client.post(
        "/api/v1/auth/register/",
        data=user_data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (response.json()["middle_name"][0] ==
            "Ensure this field has no more than 25 characters.")
    assert len(User.objects.all()) == 0


def test_registration_rejects_empty_last_name(api_client, user_data):
    user_data["last_name"] = ""
    response = api_client.post(
        "/api/v1/auth/register/",
        data=user_data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["last_name"][0] == "This field may not be blank."
    assert len(User.objects.all()) == 0


def test_registration_rejects_too_long_last_name(api_client, user_data):
    user_data["last_name"] = "veeeeeeeeeeryyyyyyyyyy loooooooooong naaaaaaaaameeeeeee"
    response = api_client.post(
        "/api/v1/auth/register/",
        data=user_data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (response.json()["last_name"][0] ==
            "Ensure this field has no more than 30 characters.")
    assert len(User.objects.all()) == 0


def test_registration_rejects_missing_birth_date(api_client, user_data):
    user_data.pop("birth_date")
    response = api_client.post(
        "/api/v1/auth/register/",
        data=user_data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["birth_date"][0] == "This field is required."
    assert len(User.objects.all()) == 0


@pytest.mark.parametrize(
    "password",
    [
        "test_user@mail.com",
        "Igoresha_man",
        "Pesotskiiy",
    ]
)
def test_registration_rejects_password_similar_to_user_attributes(
        api_client,
        user_data,
        password
):
    user_data["password"] = password
    response = api_client.post(
        "/api/v1/auth/register/",
        data=user_data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    if password == "test_user@mail.com":
        assert (response.json()["password"][0] ==
                "The password is too similar to the User email.")
    elif password == "Igoresha_man":
        assert (response.json()["password"][0] ==
                "The password is too similar to the User first name.")
    elif password == "Pesotskiiy":
        assert (response.json()["password"][0] ==
                "The password is too similar to the User last name.")
    assert len(User.objects.all()) == 0


def test_registration_rejects_too_short_password(
        api_client,
        user_data
):
    user_data["password"] = "hardek"
    response = api_client.post(
        "/api/v1/auth/register/",
        data=user_data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (response.json()["password"][0] ==
            "This password is too short. It must contain at least 10 characters.")
    assert len(User.objects.all()) == 0


def test_registration_rejects_common_password(api_client, user_data):
    user_data["password"] = "qwertyuiop"
    response = api_client.post(
        "/api/v1/auth/register/",
        data=user_data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["password"][0] == "This password is too common."
    assert len(User.objects.all()) == 0


def test_registration_rejects_numeric_password(api_client, user_data):
    user_data["password"] = "1234567890123456"
    response = api_client.post(
        "/api/v1/auth/register/",
        data=user_data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["password"][0] == "This password is entirely numeric."
    assert len(User.objects.all()) == 0


def test_registration_unique_violation_returns_validation_error(
    api_client,
    monkeypatch,
):
    def raise_unique_violation_on_create(self, validated_data):
        database_error = UniqueViolation(
            "duplicate key value violates unique constraint"
        )

        raise IntegrityError(
            "duplicate key value violates unique constraint"
        ) from database_error

    monkeypatch.setattr(
        UserRegistrationSerializer,
        "create",
        raise_unique_violation_on_create,
    )

    registration_data = {
        "email": "unique@example.com",
        "password": "SomeStrongPassword123!",
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "birth_date": "2000-01-01",
    }

    response = api_client.post(
        reverse("register"),
        data=registration_data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["email"] == ["Email already exists"]

