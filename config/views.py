from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import status, serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView


class HealthCheck(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        responses={
            status.HTTP_200_OK: inline_serializer(
                name="HealthCheckResponse",
                fields={
                    "status": serializers.CharField()
                }
            )
        }
    )
    def get(self, request):
        return Response(
            {
                "status": "ok"
            },
            status=HTTP_200_OK,
        )
