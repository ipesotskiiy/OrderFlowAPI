from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView


class HealthCheck(APIView):
    def get(self, request):
        return Response(
            {
                "status": "ok"
            },
            status=HTTP_200_OK,
        )
