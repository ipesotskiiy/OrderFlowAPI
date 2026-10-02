from rest_framework import status
from rest_framework.exceptions import APIException


class CategoryProtectedException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Cannot delete this object because other records depend on it."
