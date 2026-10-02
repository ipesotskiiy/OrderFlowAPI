from django.db.utils import IntegrityError
from drf_spectacular.utils import extend_schema, inline_serializer
from psycopg.errors import UniqueViolation
from rest_framework import status, serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import MeSerializer, UserRegistrationSerializer


# Create your views here.
class RegistrationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    @extend_schema(
        responses={
            status.HTTP_201_CREATED: serializer_class
        }
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except IntegrityError as error:
            database_error = error.__cause__

            if isinstance(database_error, UniqueViolation):
                raise serializers.ValidationError(
                    {"email": ["Email already exists"]}
                )

            raise
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MeView(APIView):
    @extend_schema(
        responses=inline_serializer(
            name="MeResponse",
            fields={
                "user": MeSerializer(),
            }
        )
    )
    def get(self, request):
        return Response(
            {
                "user": MeSerializer(request.user).data,
            }
        )
