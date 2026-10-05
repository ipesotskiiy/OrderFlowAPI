import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db

def test_manager_can_get_only_assigned_warehouses(
    api_client,
    user_obj,
    first_warehouse,
    second_warehouse,
    first_warehouse_manager_assignment,
):
    api_client.force_authenticate(user_obj)
    response = api_client.get("/api/v1/warehouses/")

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()

    ids = {warehouse["id"] for warehouse in response_data}
    assert first_warehouse.id in ids
    assert second_warehouse.id not in ids


def test_manager_cant_retrieve_unassigned_warehouse(
    api_client,
    user_obj,
    second_warehouse,
    first_warehouse_manager_assignment,
    second_warehouse_manager_assignment_another_user,
):
    api_client.force_authenticate(user_obj)
    response = api_client.get(f"/api/v1/warehouses/{second_warehouse.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "No Warehouse matches the given query." == response.json()["detail"]


def test_manager_with_multiple_assignments_gets_all_assigned_warehouses(
    api_client,
    user_obj,
    first_warehouse,
    second_warehouse,
    third_warehouse,
    first_warehouse_manager_assignment,
    second_warehouse_manager_assignment,
    third_warehouse_manager_assignment_another_user,
):
    api_client.force_authenticate(user_obj)
    response = api_client.get("/api/v1/warehouses/")

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()

    ids = {warehouse["id"] for warehouse in response_data}
    assert first_warehouse.id in ids
    assert second_warehouse.id in ids
    assert third_warehouse.id not in ids


def test_staff_can_get_all_warehouses(
    api_client,
    staff_user_obj,
    first_warehouse,
    second_warehouse,
    third_warehouse,
):
    api_client.force_authenticate(staff_user_obj)
    response = api_client.get("/api/v1/warehouses/")

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()

    ids = {warehouse["id"] for warehouse in response_data}
    assert first_warehouse.id in ids
    assert second_warehouse.id in ids
    assert third_warehouse.id in ids
