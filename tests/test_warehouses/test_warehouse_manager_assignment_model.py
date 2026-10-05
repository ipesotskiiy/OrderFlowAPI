import pytest
from django.db import IntegrityError

from accounts.models import User
from warehouses.models import WarehouseManagerAssignment, Warehouse

pytestmark = pytest.mark.django_db

def test_success_create_warehouse_manager_assignment(
    first_warehouse,
    user_obj,
):
    warehouse_manager_assignment_data = {
        "warehouse": first_warehouse,
        "user": user_obj
    }
    warehouse_manager_assignment_obj = WarehouseManagerAssignment.objects.create(
        **warehouse_manager_assignment_data
    )
    assert isinstance(warehouse_manager_assignment_obj, WarehouseManagerAssignment)
    assert (warehouse_manager_assignment_obj.warehouse ==
            warehouse_manager_assignment_data["warehouse"])
    assert (warehouse_manager_assignment_obj.user ==
            warehouse_manager_assignment_data["user"])


def test_error_create_duplicate_warehouse_and_user(
    first_warehouse,
    user_obj,
    first_warehouse_manager_assignment,
):
    warehouse_manager_assignment_data = {
        "warehouse": first_warehouse,
        "user": user_obj
    }

    with pytest.raises(IntegrityError) as exc:
        WarehouseManagerAssignment.objects.create(**warehouse_manager_assignment_data)

    assert "unique_user_warehouse_relation" in str(exc.value)

def test_assignment_deleted_when_warehouse_deleted(
    first_warehouse,
    user_obj,
    first_warehouse_manager_assignment,
):
    first_warehouse.delete()
    assert len(
        WarehouseManagerAssignment.objects.filter(
            id=first_warehouse_manager_assignment.id
        )
    ) == 0

    assert User.objects.get(id=user_obj.id)

def test_assignment_deleted_when_user_deleted(
    first_warehouse,
    user_obj,
    first_warehouse_manager_assignment,
):
    user_obj.delete()
    assert len(
        WarehouseManagerAssignment.objects.filter(
            id=first_warehouse_manager_assignment.id
        )
    ) == 0

    assert Warehouse.objects.get(id=first_warehouse.id)
