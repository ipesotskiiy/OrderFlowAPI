from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.validators import UniqueValidator

from accounts.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    password = serializers.CharField(
        max_length=128,
        required=True,
        write_only=True,
    )
    first_name = serializers.CharField(max_length=25, required=True)
    middle_name = serializers.CharField(
        max_length=25,
        allow_blank=True,
        required=False
    )
    last_name = serializers.CharField(max_length=30, required=True)
    birth_date = serializers.DateField(required=True)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "first_name",
            "middle_name",
            "last_name",
            "birth_date",
        )

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def validate(self, attrs):
        password = attrs.get("password")
        user = User(
            email=attrs.get("email"),
            first_name=attrs.get("first_name"),
            last_name=attrs.get("last_name"),
        )

        try:
            validate_password(password, user)
        except DjangoValidationError as e:
            raise DRFValidationError({"password": e.messages})

        return attrs


class MeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
        )
