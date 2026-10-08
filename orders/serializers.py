from rest_framework import serializers

from orders.models import Order, OrderItem


class OrderItemCreateSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(
        label="Quantity product in order",
        max_value=2147483647,
        min_value=1,
    )
    class Meta:
        model = OrderItem
        fields = ("product", "quantity")



class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product",
            "quantity",
            "unit_price",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "unit_price",
            "created_at",
            "updated_at",
        )


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "customer",
            "warehouse",
            "status",
            "order_items",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "customer",
            "status",
            "created_at",
            "updated_at",
        )


class OrderCreateSerializer(serializers.ModelSerializer):
    order_items = OrderItemCreateSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = (
            "id",
            "customer",
            "warehouse",
            "status",
            "order_items",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "customer",
            "status",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        order_items = validated_data.pop("order_items")
        customer = validated_data.pop("customer")
        order = Order.objects.create(customer=customer, **validated_data)
        for order_item in order_items:
            unit_price = order_item["product"].price
            OrderItem.objects.create(order=order, unit_price=unit_price, **order_item)

        return order

    def validate_order_items(self, value):
        if len(value) != len(set(item["product"] for item in value)):
            raise serializers.ValidationError("Order contains duplicate products")
        return value
