from datetime import date, timedelta

import pytest
from django.utils import timezone

from accounts.models import User

pytestmark = pytest.mark.django_db

def test_create_user_success(user_data):
    not_required_user_data = {
        "middle_name": "Romanovich",
    }

    user = User.objects.create_user(
        email=user_data["email"],
        password=user_data["password"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        birth_date=user_data["birth_date"],
        **not_required_user_data,
    )
    assert user is not None
    assert isinstance(user, User)
    assert user.email == user_data["email"]
    assert user.first_name == user_data["first_name"]
    assert user.middle_name == not_required_user_data["middle_name"]
    assert user.last_name == user_data["last_name"]
    assert user.birth_date == user_data["birth_date"]


def test_create_user_hashes_password(user_data):
    user = User.objects.create_user(
        email=user_data["email"],
        password=user_data["password"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        birth_date=user_data["birth_date"],
    )
    assert user.password != user_data["password"]
    assert len(user.password) > len(user_data["password"])
    assert user.check_password(user_data["password"]) is True


def test_create_user_normalizes_email_domain(user_data):
    user_data["email"] = "Test_User@MAIL.COM"
    user = User.objects.create_user(
        email=user_data["email"],
        password=user_data["password"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        birth_date=user_data["birth_date"],
    )
    assert user.email == "Test_User@mail.com"


@pytest.mark.parametrize(
    "custom_user_data",
    [
        {
            "email": "",
            "first_name": "igor",
            "last_name": "Pesotskiy",
            "birth_date": "1998-08-20",
            "password": "test_password",
        },
        {
            "email": "test_user@mail.com",
            "first_name": "",
            "last_name": "Pesotskiy",
            "birth_date": "1998-08-20",
            "password": "test_password",
        },
        {
            "email": "test_user@mail.com",
            "first_name": "igor",
            "last_name": "",
            "birth_date": "1998-08-20",
            "password": "test_password",
        },
        {
            "email": "test_user@mail.com",
            "first_name": "igor",
            "last_name": "Pesotskiy",
            "birth_date": "",
            "password": "test_password",
        },
        {
            "email": "test_user@mail.com",
            "first_name": "igor",
            "last_name": "Pesotskiy",
            "birth_date": "1998-08-20",
            "password": "",
        },
    ]
)
def test_create_user_rejects_empty_required_fields(custom_user_data):
    with pytest.raises(ValueError) as exc:
        User.objects.create_user(
            email=custom_user_data["email"],
            password=custom_user_data["password"],
            first_name=custom_user_data["first_name"],
            last_name=custom_user_data["last_name"],
            birth_date=custom_user_data["birth_date"],
        )
    if not custom_user_data["email"]:
        assert str(exc.value) == "Users must have an email address"
    elif not custom_user_data["password"]:
        assert str(exc.value) == "User password must be not None"
    elif not custom_user_data["first_name"]:
        assert str(exc.value) == "Users must have a first name"
    elif not custom_user_data["last_name"]:
        assert str(exc.value) == "Users must have a last name"
    elif not custom_user_data["birth_date"]:
        assert str(exc.value) == "Users must have a birth_date"


def test_create_user_allows_inactive_user(user_data):
    not_required_user_data = {
        "is_active": False,
    }

    user = User.objects.create_user(
        email=user_data["email"],
        password=user_data["password"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        birth_date=user_data["birth_date"],
        **not_required_user_data,
    )
    assert user is not None
    assert isinstance(user, User)
    assert user.is_active is False


def test_create_superuser_sets_required_flags(user_data):
    user = User.objects.create_superuser(
        email=user_data["email"],
        password=user_data["password"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        birth_date=user_data["birth_date"],
    )

    assert user.is_active is True
    assert user.is_superuser is True
    assert user.is_staff is True


@pytest.mark.parametrize(
    "not_required_user_data",
    [
        {
            "is_active": False,
        },
        {
            "is_superuser": False,
        },
        {
            "is_staff": False,
        },
    ]
)
def test_create_superuser_rejects_invalid_flags(user_data, not_required_user_data):
    with pytest.raises(ValueError) as exc:
        User.objects.create_superuser(
            email=user_data["email"],
            password=user_data["password"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            birth_date=user_data["birth_date"],
            **not_required_user_data,
        )
    if "is_active" in not_required_user_data:
        assert str(exc.value) == "Superuser must have is_active=True."
    elif "is_superuser" in not_required_user_data:
        assert str(exc.value) == "Superuser must have is_superuser=True."
    elif "is_staff" in not_required_user_data:
        assert str(exc.value) == "Superuser must have is_staff=True."


def test_user_age_before_birthday(user_data):
    current_date = timezone.localdate(timezone.now())
    current_date = current_date + timedelta(days=1)
    user_data["birth_date"] = date(
        current_date.year - 30,
        current_date.month,
        current_date.day
    )

    user = User.objects.create(
        email=user_data["email"],
        password=user_data["password"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        birth_date=user_data["birth_date"],
    )
    assert user.age == 29


def test_user_age_on_or_after_birthday(user_data):
    current_date = timezone.localdate(timezone.now())
    current_date = current_date - timedelta(days=1)
    user_data["birth_date"] = date(
        current_date.year - 30,
        current_date.month,
        current_date.day
    )

    user = User.objects.create(
        email=user_data["email"],
        password=user_data["password"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        birth_date=user_data["birth_date"],
    )
    assert user.age == 30

    current_date = timezone.localdate(timezone.now())
    user_data["birth_date"] = date(
        current_date.year - 30,
        current_date.month,
        current_date.day
    )

    user = User.objects.create(
        email="second_test@mail.ru",
        password="test_password2",
        first_name="Ilya",
        last_name="Testovich",
        birth_date=user_data["birth_date"],
    )
    assert user.age == 30



