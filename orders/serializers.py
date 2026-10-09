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

class OrderUpdateSerializer(OrderCreateSerializer):
    def update(self, instance, validated_data):
        new_order_items = validated_data.pop("order_items", None)

        if instance.status != Order.Status.DRAFT:
            raise serializers.ValidationError(
                "Only orders with draft status can be changed"
            )

        instance.warehouse = validated_data.pop("warehouse", instance.warehouse)
        instance.save()

        instance_order_items = instance.order_items.all()

        existing_order_items_by_product_id = {order_item.product_id: order_item for order_item in instance_order_items}

        if new_order_items is not None:
            existing_items_to_update = []
            new_items_to_create = []
            for new_order_item in new_order_items:
                if new_order_item["product"].id in existing_order_items_by_product_id:
                   existing_items_to_update.append(new_order_item)
                else:
                   new_items_to_create.append(new_order_item)

            for item_to_update in existing_items_to_update:
                updating_item = existing_order_items_by_product_id.get(item_to_update["product"].id)
                updating_item.quantity = item_to_update["quantity"]
                updating_item.save()

            for new_item_to_create in new_items_to_create:
                unit_price = new_item_to_create["product"].price
                OrderItem.objects.create(order=instance, unit_price=unit_price, **new_item_to_create)

            product_items_in_update_request = set(item["product"].id for item in new_order_items)
            for item in instance_order_items:
                if item.product_id not in product_items_in_update_request:
                    item.delete()

        return instance
