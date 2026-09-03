import pytest
from django.conf import settings
from django.db import connection

pytestmark = pytest.mark.django_db

def test_database_connection_uses_postgresql():
    assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"
    assert connection.vendor == "postgresql"
