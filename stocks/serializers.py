from rest_framework import serializers

from stocks.models import Stock


class StockSerializer(serializers.ModelSerializer):
    reserved_quantity = serializers.IntegerField(
        label='Reserved quantity product in warehouse',
        max_value=2147483647,
        min_value=0,
        read_only=True,
    )
    class Meta:
        model = Stock
        fields = (
            "id",
            "warehouse",
            "product",
            "quantity",
            "reserved_quantity",
            "available_quantity",
            "created_at",
            "updated_at",
        )

    def validate_warehouse(self, value):
        if self.instance and self.instance.warehouse != value:
            raise serializers.ValidationError(
                "Warehouse in Stock can't be changed"
            )
        return value


    def validate_product(self, value):
        if self.instance and self.instance.product != value:
            raise serializers.ValidationError("Product in Stock can't be changed")
        return value


    def validate(self, attrs):
        if self.instance:
            quantity = attrs.get("quantity", self.instance.quantity)
            reserved_quantity = self.instance.reserved_quantity
            if reserved_quantity > quantity:
                raise serializers.ValidationError(
                    "Quantity cannot be lower than reserved quantity."
                )
        return attrs

