import pytest
from rest_framework import status

from catalog.models import Category

pytestmark = pytest.mark.django_db

def test_anonymous_cant_get_list_category(api_client, first_category, second_category):
    response = api_client.get(
        "/api/v1/catalog/categories/"
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Authentication credentials were not provided."


def test_anonymous_cant_get_retrieve_category(api_client, first_category):
    response = api_client.get(
        f"/api/v1/catalog/categories/{first_category.id}/"
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Authentication credentials were not provided."


def test_anonymous_cant_create_category(api_client):
    response = api_client.post(
        "/api/v1/catalog/categories/",
        data={
            "name": "Напитки",
            "minimum_age": 12,
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Authentication credentials were not provided."
    assert len(Category.objects.all()) == 0


def test_anonymous_cant_update_category(api_client, first_category):
    old_name = first_category.name
    response = api_client.patch(
        f"/api/v1/catalog/categories/{first_category.id}/",
        data={
            "name": "Напиточки",
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Authentication credentials were not provided."

    first_category_obj = Category.objects.get(id=first_category.id)
    assert first_category_obj.name == old_name


def test_anonymous_cant_delete_category(api_client, first_category):
    response = api_client.delete(
        f"/api/v1/catalog/categories/{first_category.id}/",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Authentication credentials were not provided."

    categories_queryset = Category.objects.filter(id=first_category.id)
    assert len(categories_queryset) == 1
    assert first_category in categories_queryset


def test_authenticated_can_get_list_category(
    api_client,
    first_category,
    second_category,
    user_obj,
):
    api_client.force_authenticate(user_obj)
    response = api_client.get(
        "/api/v1/catalog/categories/"
    )
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert len(response_data) == 2

    ids = {category["id"] for category in response_data}
    assert first_category.id in ids
    assert second_category.id in ids


def test_authenticated_can_get_retrieve_category(api_client, first_category, user_obj):
    api_client.force_authenticate(user_obj)
    response = api_client.get(
        f"/api/v1/catalog/categories/{first_category.id}/"
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()

    cat_obj = Category.objects.get(id=response_data["id"])
    assert first_category == cat_obj


def test_authenticated_cant_create_category(api_client, user_obj):
    api_client.force_authenticate(user_obj)
    response = api_client.post(
        "/api/v1/catalog/categories/",
        data={
            "name": "Напитки",
            "minimum_age": 12,
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == ("You do not have permission "
                                         "to perform this action.")
    assert len(Category.objects.all()) == 0


def test_authenticated_cant_update_category(api_client, first_category, user_obj):
    old_name = first_category.name

    api_client.force_authenticate(user_obj)
    response = api_client.patch(
        f"/api/v1/catalog/categories/{first_category.id}/",
        data={
            "name": "Напиточки",
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == ("You do not have permission "
                                         "to perform this action.")

    first_category_obj = Category.objects.get(id=first_category.id)
    assert first_category_obj.name == old_name


def test_authenticated_cant_delete_category(api_client, first_category, user_obj):
    api_client.force_authenticate(user_obj)
    response = api_client.delete(
        f"/api/v1/catalog/categories/{first_category.id}/",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == ("You do not have permission "
                                         "to perform this action.")

    categories_queryset = Category.objects.filter(id=first_category.id)
    assert len(categories_queryset) == 1
    assert first_category in categories_queryset


def test_staff_can_get_list_category(
        api_client,
        first_category,
        second_category,
        staff_user_obj,
):
    api_client.force_authenticate(staff_user_obj)
    response = api_client.get(
        "/api/v1/catalog/categories/"
    )
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert len(response_data) == 2

    ids = {category["id"] for category in response_data}
    assert first_category.id in ids
    assert second_category.id in ids


def test_staff_can_get_retrieve_category(api_client, first_category, staff_user_obj):
    api_client.force_authenticate(staff_user_obj)
    response = api_client.get(
        f"/api/v1/catalog/categories/{first_category.id}/"
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()

    cat_obj = Category.objects.get(id=response_data["id"])
    assert first_category == cat_obj


def test_staff_can_create_category(api_client, staff_user_obj):
    api_client.force_authenticate(staff_user_obj)
    category_data = {
            "name": "Напитки",
            "minimum_age": 12,
        }
    response = api_client.post(
        "/api/v1/catalog/categories/",
        data=category_data
    )
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    category_obj = Category.objects.get(id=response_data["id"])
    assert category_obj.name == category_data["name"]
    assert category_obj.minimum_age == category_data["minimum_age"]
    assert len(Category.objects.all()) == 1


def test_staff_can_update_category(api_client, first_category, staff_user_obj):
    old_name = first_category.name
    old_minimum_age = first_category.minimum_age

    api_client.force_authenticate(staff_user_obj)
    category_data = {
            "name": "Напиточки",
        }
    response = api_client.patch(
        f"/api/v1/catalog/categories/{first_category.id}/",
        data=category_data
    )
    assert response.status_code == status.HTTP_200_OK

    first_category_obj = Category.objects.get(id=first_category.id)
    assert first_category_obj.name != old_name
    assert first_category_obj.name == category_data["name"]
    assert first_category_obj.minimum_age == old_minimum_age


def test_staff_can_delete_category(api_client, first_category, staff_user_obj):
    api_client.force_authenticate(staff_user_obj)
    response = api_client.delete(
        f"/api/v1/catalog/categories/{first_category.id}/",
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    categories_queryset = Category.objects.filter(id=first_category.id)
    assert len(categories_queryset) == 0


def test_create_category_api_minimum_age_equal_zero(api_client, staff_user_obj):
    api_client.force_authenticate(staff_user_obj)
    category_data = {
            "name": "Напитки",
        }
    response = api_client.post(
        "/api/v1/catalog/categories/",
        data=category_data
    )
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    category_obj = Category.objects.get(id=response_data["id"])
    assert category_obj.name == category_data["name"]
    assert category_obj.minimum_age == 0
    assert len(Category.objects.all()) == 1


def test_error_api_create_category_with_equal_names(
    api_client,
    staff_user_obj,
    first_category,
):
    api_client.force_authenticate(staff_user_obj)
    category_data = {
        "name": "напитки",
        "minimum_age": 12,
    }

    response = api_client.post(
        "/api/v1/catalog/categories/",
        data=category_data
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(Category.objects.all()) == 1


def test_success_patch_category_with_same_name(
    api_client,
    staff_user_obj,
    first_category
):
    api_client.force_authenticate(staff_user_obj)
    category_data = {
        "name": first_category.name,
    }
    response = api_client.patch(
        f"/api/v1/catalog/categories/{first_category.id}/",
        data=category_data
    )
    assert response.status_code == status.HTTP_200_OK
    assert Category.objects.get(id=first_category.id).name == first_category.name


def test_success_patch_category_change_only_name_case(
    api_client,
    staff_user_obj,
    first_category
):
    api_client.force_authenticate(staff_user_obj)
    category_data = {
        "name": first_category.name.lower(),
    }
    response = api_client.patch(
        f"/api/v1/catalog/categories/{first_category.id}/",
        data=category_data
    )
    assert response.status_code == status.HTTP_200_OK
    assert Category.objects.get(id=first_category.id).name == category_data["name"]


def test_error_patch_category_with_another_existing_category_name(
    api_client,
    staff_user_obj,
    first_category,
    second_category
):
    api_client.force_authenticate(staff_user_obj)
    category_data = {
        "name": second_category.name,
    }
    response = api_client.patch(
        f"/api/v1/catalog/categories/{first_category.id}/",
        data=category_data
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert Category.objects.get(id=first_category.id).name == first_category.name
