import django_filters

from stocks.models import Stock


class StockFilter(django_filters.FilterSet):
    quantity_min = django_filters.NumberFilter(
        field_name="quantity",
        lookup_expr="gte",
    )
    quantity_max = django_filters.NumberFilter(
        field_name="quantity",
        lookup_expr="lte",
    )
    reserved_quantity_min = django_filters.NumberFilter(
        field_name="reserved_quantity",
        lookup_expr="gte",
    )
    reserved_quantity_max = django_filters.NumberFilter(
        field_name="reserved_quantity",
        lookup_expr="lte",
    )

    class Meta:
        model = Stock
        fields = ("warehouse", "product", "quantity", "reserved_quantity")
