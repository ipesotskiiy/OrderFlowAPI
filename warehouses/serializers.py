from rest_framework import serializers

from warehouses.models import Warehouse, WarehouseManagerAssignment


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = (
            "id",
            "name",
            "code",
            "address",
            "is_active",
            "created_at",
            "updated_at",
        )

    def validate_code(self, value):
        if Warehouse.objects.filter(code__iexact=value).exists():
            if self.instance:
                if Warehouse.objects.filter(
                        code__iexact=value
                ).exclude(
                    id=self.instance.id
                ).exists():
                    raise serializers.ValidationError(
                        "Warehouse with this code already exists."
                    )
                return value
            raise serializers.ValidationError(
                "Warehouse with this code already exists."
            )
        return value


class WarehouseManagerAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarehouseManagerAssignment
        fields=(
            "id",
            "warehouse",
            "user",
            "created_at",
        )
