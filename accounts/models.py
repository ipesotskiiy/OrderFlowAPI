from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone

from accounts.managers import CustomUserManager


# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name="User email",
        unique=True,
        db_index=True,
    )
    first_name = models.CharField(verbose_name="User first name", max_length=25)
    middle_name = models.CharField(
        verbose_name="User middle name",
        max_length=25,
        blank=True,
    )
    last_name = models.CharField(
        verbose_name="User last name",
        max_length=30,
    )
    birth_date = models.DateField(verbose_name="User birth date")
    is_active = models.BooleanField(verbose_name="User is active?", default=True)
    is_staff = models.BooleanField(verbose_name="User is staff", default=False)
    created_at = models.DateTimeField(verbose_name="User create", auto_now_add=True)
    updated_at = models.DateTimeField(
        verbose_name="User last update datetime",
        auto_now=True,
    )

    @property
    def age(self):
        today = timezone.localdate()
        return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "birth_date",
    ]

    objects = CustomUserManager()
