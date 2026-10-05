from datetime import datetime

import pytest
from django.db import IntegrityError

from warehouses.models import Warehouse

pytestmark = pytest.mark.django_db

def test_success_create_warehouse():
    warehouse_data = {
        "name": "first_warehouse",
        "code": "WR1-A1",
        "address": "Rostov-on-Don, bolshaya sadovaya street 34",
    }

    warehouse_obj = Warehouse.objects.create(**warehouse_data)
    assert isinstance(warehouse_obj, Warehouse)
    assert warehouse_obj.name == warehouse_data["name"]
    assert warehouse_obj.code == warehouse_data["code"]
    assert warehouse_obj.address == warehouse_data["address"]


def test_error_create_warehouse_with_case_insensitive_duplicate_code(
    first_warehouse,
):
    warehouse_data = {
        "name": "second_warehouse",
        "code": first_warehouse.code.lower(),
        "address": "Rostov-on-Don, bolshaya sadovaya street 38",
    }

    with pytest.raises(IntegrityError) as exc:
        Warehouse.objects.create(**warehouse_data)

    assert "unique_lower_warehouse_code" in str(exc.value)


def test_warehouse_default_is_active_is_true():
    warehouse_data = {
        "name": "first_warehouse",
        "code": "WR1-A1",
        "address": "Rostov-on-Don, bolshaya sadovaya street 34",
    }

    warehouse_obj = Warehouse.objects.create(**warehouse_data)
    assert warehouse_obj.is_active is True


def test_warehouse_created_at_updated_at(first_warehouse):
    assert first_warehouse.created_at is not None
    assert isinstance(first_warehouse.created_at, datetime)
    assert first_warehouse.updated_at is not None
    assert isinstance(first_warehouse.updated_at, datetime)


def test_warehouse_change_updated_at(first_warehouse):
    old_updated_at = first_warehouse.updated_at
    first_warehouse.name = "first warehouse update"
    first_warehouse.save()

    assert old_updated_at < first_warehouse.updated_at
