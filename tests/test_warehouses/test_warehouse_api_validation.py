import pytest
from rest_framework import status

from warehouses.models import Warehouse

pytestmark = pytest.mark.django_db

def test_default_api_creation_warehouse_is_active_true(
    api_client,
    staff_user_obj,
):
    warehouse_data = {
        "name": "third_warehouse",
        "code": "WR1-A3",
        "address": "Rostov-on-Don, bolshaya sadovaya street 39",
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.post(
        "/api/v1/warehouses/",
        data=warehouse_data,
        format="json"
    )
    assert response.status_code == status.HTTP_201_CREATED

    response_data = response.json()
    warehouse_obj = Warehouse.objects.get(id=response_data["id"])
    assert warehouse_obj.is_active is True


def test_error_create_warehouse_with_case_insensitive_duplicate_code(
    api_client,
    staff_user_obj,
    first_warehouse,
):
    warehouse_data = {
        "name": "third_warehouse",
        "code": first_warehouse.code.lower(),
        "address": "Rostov-on-Don, bolshaya sadovaya street 39",
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.post(
        "/api/v1/warehouses/",
        data=warehouse_data,
        format="json"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Warehouse with this code already exists." in response.json()["code"]
    assert len(Warehouse.objects.all()) == 1


def test_success_update_warehouse_with_unique_code(
    api_client,
    staff_user_obj,
    first_warehouse,
):
    warehouse_data = {
        "code": "WR1-A4",
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.patch(
        f"/api/v1/warehouses/{first_warehouse.id}/",
        data=warehouse_data,
        format="json"
    )
    assert response.status_code == status.HTTP_200_OK
    assert (Warehouse.objects.get(id=response.json()["id"]).code ==
            warehouse_data["code"])


def test_success_update_warehouse_with_code_case_change(
    api_client,
    staff_user_obj,
    first_warehouse,
):
    warehouse_data = {
        "code": first_warehouse.code.lower(),
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.patch(
        f"/api/v1/warehouses/{first_warehouse.id}/",
        data=warehouse_data,
        format="json"
    )
    assert response.status_code == status.HTTP_200_OK
    assert (Warehouse.objects.get(id=response.json()["id"]).code ==
            warehouse_data["code"])


def test_error_update_warehouse_with_another_warehouse_code(
    api_client,
    staff_user_obj,
    first_warehouse,
    second_warehouse,
):
    warehouse_data = {
        "code": second_warehouse.code,
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.patch(
        f"/api/v1/warehouses/{first_warehouse.id}/",
        data=warehouse_data,
        format="json"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Warehouse with this code already exists." in response.json()["code"]
    assert (Warehouse.objects.get(id=first_warehouse.id).code ==
            first_warehouse.code)


@pytest.mark.parametrize(
    "required_field",
    [
        "name",
        "code",
        "address"
    ]
)
def test_error_create_warehouse_without_required_field(
    api_client,
    staff_user_obj,
    required_field,
):
    warehouse_data = {
        "name": "first_warehouse",
        "code": "WR1-A1",
        "address": "Rostov-on-Don, bolshaya sadovaya street 34",
    }
    warehouse_data.pop(required_field)
    api_client.force_authenticate(staff_user_obj)
    response = api_client.post(
        "/api/v1/warehouses/",
        data=warehouse_data,
        format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not Warehouse.objects.all().exists()

