import pytest
from rest_framework import status

from warehouses.models import Warehouse

pytestmark = pytest.mark.django_db


def test_anonymous_cant_get_list_warehouse(
    api_client,
    first_warehouse,
    second_warehouse,
):
    response = api_client.get("/api/v1/warehouses/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Authentication credentials were not provided." == response.json()["detail"]


def test_anonymous_cant_get_retrieve_warehouse(
    api_client,
    first_warehouse,
):
    response = api_client.get(f"/api/v1/warehouses/{first_warehouse.id}/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Authentication credentials were not provided." == response.json()["detail"]


def test_anonymous_cant_create_warehouse(api_client):
    warehouse_data = {
        "name": "first_warehouse",
        "code": "WR1-A1",
        "address": "Rostov-on-Don, bolshaya sadovaya street 34",
    }
    response = api_client.post(
        "/api/v1/warehouses/",
        data=warehouse_data,
        format="json"
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Authentication credentials were not provided." == response.json()["detail"]
    assert not Warehouse.objects.all().exists()


def test_anonymous_cant_update_warehouse(
    api_client,
    first_warehouse,
):
    warehouse_data = {"name": "first_warehouse_update"}
    response = api_client.patch(
        f"/api/v1/warehouses/{first_warehouse.id}/",
        data=warehouse_data,
        format="json"
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Authentication credentials were not provided." == response.json()["detail"]
    assert (Warehouse.objects.get(id=first_warehouse.id).name ==
            first_warehouse.name)

def test_anonymous_cant_delete_warehouse(
    api_client,
    first_warehouse,
):
    response = api_client.delete(
        f"/api/v1/warehouses/{first_warehouse.id}/",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Authentication credentials were not provided." == response.json()["detail"]
    assert Warehouse.objects.get(id=first_warehouse.id) == first_warehouse


def test_non_manager_cant_get_list_warehouse(
    api_client,
    user_obj,
    first_warehouse,
    second_warehouse,
):
    api_client.force_authenticate(user_obj)
    response = api_client.get("/api/v1/warehouses/")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert ("You do not have permission to perform this action." ==
            response.json()["detail"])


def test_non_manager_cant_get_retrieve_warehouse(
    api_client,
    user_obj,
    first_warehouse,
):
    api_client.force_authenticate(user_obj)
    response = api_client.get(f"/api/v1/warehouses/{first_warehouse.id}/")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert ("You do not have permission to perform this action." ==
            response.json()["detail"])


def test_non_manager_cant_create_warehouse(
    api_client,
    user_obj,
):
    warehouse_data = {
        "name": "first_warehouse",
        "code": "WR1-A1",
        "address": "Rostov-on-Don, bolshaya sadovaya street 34",
    }
    api_client.force_authenticate(user_obj)
    response = api_client.post(
        "/api/v1/warehouses/",
        data=warehouse_data,
        format="json"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert ("You do not have permission to perform this action." ==
            response.json()["detail"])
    assert not Warehouse.objects.all().exists()


def test_non_manager_cant_update_warehouse(
    api_client,
    user_obj,
    first_warehouse,
):
    warehouse_data = {"name": "first_warehouse_update"}
    api_client.force_authenticate(user_obj)
    response = api_client.patch(
        f"/api/v1/warehouses/{first_warehouse.id}/",
        data=warehouse_data,
        format="json"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert ("You do not have permission to perform this action." ==
            response.json()["detail"])
    assert (Warehouse.objects.get(id=first_warehouse.id).name ==
            first_warehouse.name)


def test_non_manager_cant_delete_warehouse(
    api_client,
    user_obj,
    first_warehouse,
):
    api_client.force_authenticate(user_obj)
    response = api_client.delete(
        f"/api/v1/warehouses/{first_warehouse.id}/",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert ("You do not have permission to perform this action." ==
            response.json()["detail"])
    assert Warehouse.objects.get(id=first_warehouse.id) == first_warehouse


def test_manager_can_get_list_warehouse(
    api_client,
    user_obj,
    first_warehouse,
    second_warehouse,
    first_warehouse_manager_assignment,
    second_warehouse_manager_assignment,
):
    api_client.force_authenticate(user_obj)
    response = api_client.get("/api/v1/warehouses/")

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()

    ids = {warehouse["id"] for warehouse in response_data}
    assert first_warehouse.id in ids
    assert second_warehouse.id in ids


def test_manager_can_get_retrieve_warehouse(
    api_client,
    user_obj,
    first_warehouse,
    first_warehouse_manager_assignment,
):
    api_client.force_authenticate(user_obj)
    response = api_client.get(f"/api/v1/warehouses/{first_warehouse.id}/")

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()

    assert Warehouse.objects.get(id=response_data["id"]) == first_warehouse


def test_manager_cant_create_warehouse(
    api_client,
    user_obj,
    first_warehouse_manager_assignment,
):
    warehouse_data = {
        "name": "third_warehouse",
        "code": "WR1-A3",
        "address": "Rostov-on-Don, bolshaya sadovaya street 39",
    }
    api_client.force_authenticate(user_obj)
    response = api_client.post(
        "/api/v1/warehouses/",
        data=warehouse_data,
        format="json"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert ("You do not have permission to perform this action." ==
            response.json()["detail"])
    warehouse_queryset = Warehouse.objects.all()
    assert len(warehouse_queryset) == 1


def test_manager_cant_update_warehouse(
    api_client,
    user_obj,
    first_warehouse,
    first_warehouse_manager_assignment,
):
    warehouse_data = {
        "name": "third_warehouse",
    }
    api_client.force_authenticate(user_obj)
    response = api_client.patch(
        f"/api/v1/warehouses/{first_warehouse.id}/",
        data=warehouse_data,
        format="json"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert ("You do not have permission to perform this action." ==
            response.json()["detail"])
    assert (Warehouse.objects.get(id=first_warehouse.id).name ==
            first_warehouse.name)


def test_manager_cant_delete_warehouse(
    api_client,
    user_obj,
    first_warehouse,
    first_warehouse_manager_assignment,
):
    api_client.force_authenticate(user_obj)
    response = api_client.delete(
        f"/api/v1/warehouses/{first_warehouse.id}/",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert ("You do not have permission to perform this action." ==
            response.json()["detail"])
    assert Warehouse.objects.get(id=first_warehouse.id) == first_warehouse


def test_staff_can_get_list_warehouse(
    api_client,
    staff_user_obj,
    first_warehouse,
    second_warehouse,
):
    api_client.force_authenticate(staff_user_obj)
    response = api_client.get("/api/v1/warehouses/")

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()

    ids = {warehouse["id"] for warehouse in response_data}
    assert first_warehouse.id in ids
    assert second_warehouse.id in ids


def test_staff_can_get_retrieve_warehouse(
    api_client,
    staff_user_obj,
    first_warehouse,
):
    api_client.force_authenticate(staff_user_obj)
    response = api_client.get(f"/api/v1/warehouses/{first_warehouse.id}/")

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()

    assert Warehouse.objects.get(id=response_data["id"]) == first_warehouse


def test_staff_can_create_warehouse(
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
    assert warehouse_obj.name == warehouse_data["name"]
    assert warehouse_obj.code == warehouse_data["code"]
    assert warehouse_obj.address == warehouse_data["address"]


def test_staff_can_update_warehouse(
    api_client,
    staff_user_obj,
    first_warehouse,
    first_warehouse_manager_assignment,
):
    warehouse_data = {
        "name": "third_warehouse",
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.patch(
        f"/api/v1/warehouses/{first_warehouse.id}/",
        data=warehouse_data,
        format="json"
    )
    assert response.status_code == status.HTTP_200_OK
    assert (Warehouse.objects.get(id=first_warehouse.id).name ==
            warehouse_data["name"])


def test_staff_can_delete_warehouse(
    api_client,
    staff_user_obj,
    first_warehouse,
):
    api_client.force_authenticate(staff_user_obj)
    response = api_client.delete(
        f"/api/v1/warehouses/{first_warehouse.id}/",
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Warehouse.objects.all().exists()


def test_staff_cant_update_warehouse_with_put(
    api_client,
    staff_user_obj,
    first_warehouse,
):
    warehouse_data = {
        "name": "third_warehouse",
        "code": "WR1-A3",
        "address": "Rostov-on-Don, bolshaya sadovaya street 39",
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.put(
        f"/api/v1/warehouses/{first_warehouse.id}/",
        data=warehouse_data,
        format="json"
    )
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert Warehouse.objects.get(id=first_warehouse.id) == first_warehouse


