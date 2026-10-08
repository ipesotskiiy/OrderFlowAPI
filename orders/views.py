from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from orders.models import Order
from orders.serializers import OrderCreateSerializer


# Create your views here.
class OrderViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = OrderCreateSerializer
    queryset = Order.objects.all()

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

