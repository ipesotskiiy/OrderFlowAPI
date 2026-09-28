from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.viewsets import ModelViewSet

from catalog.filters import ProductFilter
from catalog.models import Category, Product
from catalog.permissions import IsAdminOrIsAuthenticatedReadOnly
from catalog.serializers import CategorySerializer, ProductSerializer


# Create your views here.
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrIsAuthenticatedReadOnly,)


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAdminOrIsAuthenticatedReadOnly,)
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    )
    filterset_class = ProductFilter
    search_fields = ("name", "sku")
    ordering_fields = ["price", "created_at", "name"]
