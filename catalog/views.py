from django.db.models import ProtectedError
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiResponse,
    inline_serializer
)
from rest_framework import filters, status, serializers
from rest_framework.viewsets import ModelViewSet

from catalog.exceptions import CategoryProtectedException
from catalog.filters import ProductFilter
from catalog.models import Category, Product
from catalog.permissions import IsAdminOrIsAuthenticatedReadOnly
from catalog.serializers import CategorySerializer, ProductSerializer


@extend_schema_view(
    destroy=extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(
                description="Category deleted successfully."
            ),
            status.HTTP_409_CONFLICT: OpenApiResponse(
                response=inline_serializer(
                    name="CategoryProtectedError",
                    fields={
                        "detail": serializers.CharField(),
                    },
                ),
                description="Category cannot be deleted because products depend on it.",
            ),
        }
    )
)
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrIsAuthenticatedReadOnly,)
    http_method_names = [
        "get",
        "post",
        "patch",
        "delete",
        "head",
        "options",
    ]

    def perform_destroy(self, instance):
        try:
            super().perform_destroy(instance)
        except ProtectedError:
            raise CategoryProtectedException()


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
    http_method_names = [
        "get",
        "post",
        "patch",
        "delete",
        "head",
        "options",
    ]
