from rest_framework.viewsets import ModelViewSet

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
