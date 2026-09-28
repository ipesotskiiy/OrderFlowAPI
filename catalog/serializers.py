from rest_framework import serializers

from catalog.models import Category, Product


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "minimum_age",
            "created_at",
            "updated_at",
        )


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "manufacturer_name",
            "category",
            "minimum_age",
            "sku",
            "price",
            "weight_kg",
            "height_cm",
            "color",
            "is_active",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        weight_kg = attrs.get("weight_kg")
        if weight_kg is not None and weight_kg <= 0:
            raise serializers.ValidationError({"weight_kg": "Вес должен быть больше 0"})

        price = attrs.get("price")
        if price is not None and price <= 0:
            raise serializers.ValidationError({"price": "Цена должна быть больше 0"})

        height_cm = attrs.get("height_cm")
        if height_cm is not None and height_cm <= 0:
            raise serializers.ValidationError(
                {"height_cm": "Высота должна быть больше 0"}
            )

        return attrs



