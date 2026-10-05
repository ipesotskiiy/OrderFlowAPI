import pytest
from rest_framework import status

from warehouses.models import WarehouseManagerAssignment

pytestmark = pytest.mark.django_db


def test_staff_can_get_list_warehouse_manager_assignment(
    api_client,
    staff_user_obj,
    first_warehouse_manager_assignment,
    second_warehouse_manager_assignment,
):
    api_client.force_authenticate(staff_user_obj)
    response = api_client.get(
        "/api/v1/warehouses/assignments/",
    )
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    ids = {warehouse["id"] for warehouse in response_data}
    assert first_warehouse_manager_assignment.id in ids
    assert second_warehouse_manager_assignment.id in ids


def test_staff_can_get_retrieve_warehouse_manager_assignment(
    api_client,
    staff_user_obj,
    first_warehouse_manager_assignment,
):
    api_client.force_authenticate(staff_user_obj)
    response = api_client.get(
        f"/api/v1/warehouses/assignments/{first_warehouse_manager_assignment.id}/",
    )
    assert response.status_code == status.HTTP_200_OK
    assert (WarehouseManagerAssignment.objects.get(id=response.json()["id"]) ==
            first_warehouse_manager_assignment)


def test_staff_can_create_warehouse_manager_assignment(
    api_client,
    staff_user_obj,
    first_warehouse,
    user_obj,
):
    warehouse_manager_assignment_data = {
        "warehouse": first_warehouse.id,
        "user": user_obj.id,
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.post(
        "/api/v1/warehouses/assignments/",
        data=warehouse_manager_assignment_data,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    warehouse_manager_assignment_obj = (
        WarehouseManagerAssignment.objects.get(id=response.json()["id"]))
    assert warehouse_manager_assignment_obj.user_id == user_obj.id
    assert warehouse_manager_assignment_obj.warehouse_id == first_warehouse.id


def test_staff_can_delete_warehouse_manager_assignment(
    api_client,
    staff_user_obj,
    first_warehouse_manager_assignment,
):
    api_client.force_authenticate(staff_user_obj)
    response = api_client.delete(
        f"/api/v1/warehouses/assignments/{first_warehouse_manager_assignment.id}/",
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not WarehouseManagerAssignment.objects.all().exists()


def test_error_create_duplicate_warehouse_manager_assignment(
    api_client,
    staff_user_obj,
    first_warehouse,
    user_obj,
    first_warehouse_manager_assignment,
):
    warehouse_manager_assignment_data = {
        "warehouse": first_warehouse.id,
        "user": user_obj.id,
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.post(
        "/api/v1/warehouses/assignments/",
        data=warehouse_manager_assignment_data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (response.json()["non_field_errors"][0] ==
            "This user is already assigned to this warehouse.")


def test_non_manager_cant_get_list_warehouse_manager_assignment(
    api_client,
    user_obj,
    second_warehouse_manager_assignment_another_user
):
    api_client.force_authenticate(user_obj)
    response = api_client.get(
        "/api/v1/warehouses/assignments/",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert ("You do not have permission to perform this action." ==
            response.json()["detail"])


def test_non_manager_cant_get_retrieve_warehouse_manager_assignment(
    api_client,
    user_obj,
    second_warehouse_manager_assignment_another_user
):
    api_client.force_authenticate(user_obj)
    response = api_client.get(
        f"/api/v1/warehouses/assignments/{second_warehouse_manager_assignment_another_user.id}/",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert ("You do not have permission to perform this action." ==
            response.json()["detail"])


def test_non_manager_cant_create_warehouse_manager_assignment(
    api_client,
    first_warehouse,
    user_obj,
):
    warehouse_manager_assignment_data = {
        "warehouse": first_warehouse.id,
        "user": user_obj.id,
    }
    api_client.force_authenticate(user_obj)
    response = api_client.post(
        "/api/v1/warehouses/assignments/",
        data=warehouse_manager_assignment_data,
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert ("You do not have permission to perform this action." ==
            response.json()["detail"])
    assert not WarehouseManagerAssignment.objects.all().exists()


def test_non_manager_cant_delete_warehouse_manager_assignment(
    api_client,
    second_warehouse_manager_assignment_another_user,
    user_obj,
):
    api_client.force_authenticate(user_obj)
    response = api_client.delete(
        f"/api/v1/warehouses/assignments/{second_warehouse_manager_assignment_another_user.id}/",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert ("You do not have permission to perform this action." ==
            response.json()["detail"])
    assert len(WarehouseManagerAssignment.objects.all()) == 1


def test_manager_cant_get_list_warehouse_manager_assignment(
    api_client,
    user_obj,
    first_warehouse_manager_assignment,
    second_warehouse_manager_assignment_another_user,
):
    api_client.force_authenticate(user_obj)
    response = api_client.get(
        "/api/v1/warehouses/assignments/",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert ("You do not have permission to perform this action." ==
            response.json()["detail"])


def test_manager_cant_get_retrieve_warehouse_manager_assignment(
    api_client,
    user_obj,
    first_warehouse_manager_assignment,
):
    api_client.force_authenticate(user_obj)
    response = api_client.get(
        f"/api/v1/warehouses/assignments/{first_warehouse_manager_assignment.id}/",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert ("You do not have permission to perform this action." ==
            response.json()["detail"])


def test_manager_cant_create_warehouse_manager_assignment(
    api_client,
    first_warehouse,
    user_obj,
    second_warehouse_manager_assignment,
):
    warehouse_manager_assignment_data = {
        "warehouse": first_warehouse.id,
        "user": user_obj.id,
    }
    api_client.force_authenticate(user_obj)
    response = api_client.post(
        "/api/v1/warehouses/assignments/",
        data=warehouse_manager_assignment_data,
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert ("You do not have permission to perform this action." ==
            response.json()["detail"])
    assert len(WarehouseManagerAssignment.objects.all()) == 1


def test_manager_cant_delete_warehouse_manager_assignment(
    api_client,
    first_warehouse_manager_assignment,
    user_obj,
):
    api_client.force_authenticate(user_obj)
    response = api_client.delete(
        f"/api/v1/warehouses/assignments/{first_warehouse_manager_assignment.id}/",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert ("You do not have permission to perform this action." ==
            response.json()["detail"])
    assert len(WarehouseManagerAssignment.objects.all()) == 1


def test_anonymous_cant_get_list_warehouse_manager_assignment(
    api_client,
    first_warehouse_manager_assignment,
    second_warehouse_manager_assignment_another_user,
):
    response = api_client.get(
        "/api/v1/warehouses/assignments/",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert ("Authentication credentials were not provided." ==
            response.json()["detail"])


def test_anonymous_cant_get_retrieve_warehouse_manager_assignment(
    api_client,
    first_warehouse_manager_assignment,
):
    response = api_client.get(
        f"/api/v1/warehouses/assignments/{first_warehouse_manager_assignment.id}/",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert ("Authentication credentials were not provided." ==
            response.json()["detail"])


def test_anonymous_cant_create_warehouse_manager_assignment(
    api_client,
    first_warehouse,
    user_obj,
):
    warehouse_manager_assignment_data = {
        "warehouse": first_warehouse.id,
        "user": user_obj.id,
    }
    response = api_client.post(
        "/api/v1/warehouses/assignments/",
        data=warehouse_manager_assignment_data,
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert ("Authentication credentials were not provided." ==
            response.json()["detail"])
    assert not WarehouseManagerAssignment.objects.all().exists()


def test_anonymous_cant_delete_warehouse_manager_assignment(
    api_client,
    first_warehouse_manager_assignment,
):
    response = api_client.delete(
        f"/api/v1/warehouses/assignments/{first_warehouse_manager_assignment.id}/",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert ("Authentication credentials were not provided." ==
            response.json()["detail"])
    assert len(WarehouseManagerAssignment.objects.all()) == 1


def test_method_put_closed_warehouse_manager_assignment(
    api_client,
    staff_user_obj,
    second_warehouse,
    first_warehouse_manager_assignment,
    second_user_obj,
):
    warehouse_manager_assignment_data = {
        "warehouse": second_warehouse.id,
        "user": second_user_obj.id,
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.put(
        f"/api/v1/warehouses/assignments/{first_warehouse_manager_assignment.id}/",
        data=warehouse_manager_assignment_data,
        format="json",
    )
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    warehouse_manager_assignment_obj = WarehouseManagerAssignment.objects.get(
        id=first_warehouse_manager_assignment.id
    )
    assert (warehouse_manager_assignment_obj.user==
            first_warehouse_manager_assignment.user)
    assert (warehouse_manager_assignment_obj.warehouse ==
            first_warehouse_manager_assignment.warehouse)


def test_method_patch_closed_warehouse_manager_assignment(
    api_client,
    staff_user_obj,
    second_warehouse,
    first_warehouse_manager_assignment,
):
    warehouse_manager_assignment_data = {
        "warehouse": second_warehouse.id,
    }
    api_client.force_authenticate(staff_user_obj)
    response = api_client.patch(
        f"/api/v1/warehouses/assignments/{first_warehouse_manager_assignment.id}/",
        data=warehouse_manager_assignment_data,
        format="json",
    )
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    warehouse_manager_assignment_obj = WarehouseManagerAssignment.objects.get(
        id=first_warehouse_manager_assignment.id
    )
    assert (warehouse_manager_assignment_obj.warehouse ==
            first_warehouse_manager_assignment.warehouse)
