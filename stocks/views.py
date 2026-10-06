from rest_framework import viewsets

from stocks.models import Stock
from stocks.permissions import IsAdminOrStockWarehouseManagerReadAndUpdate
from stocks.serializers import StockSerializer


# Create your views here.
class StockViewSet(viewsets.ModelViewSet):
    serializer_class = StockSerializer
    queryset = Stock.objects.all()
    permission_classes = (IsAdminOrStockWarehouseManagerReadAndUpdate,)
    http_method_names = [
        "get",
        "post",
        "patch",
        "delete",
        "head",
        "options",
    ]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Stock.objects.all()
        return Stock.objects.filter(
            warehouse__manager_assignments__user=self.request.user
        )

