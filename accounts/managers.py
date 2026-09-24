from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(
        self,
        email,
        password,
        first_name,
        last_name,
        birth_date,
        **extra_fields,
    ):
        self.check_required_users_field(
            email,
            password,
            first_name,
            last_name,
            birth_date,
        )

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(
        self,
        email,
        password,
        first_name,
        last_name,
        birth_date,
        **extra_fields,
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is False:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is False:
            raise ValueError("Superuser must have is_superuser=True.")

        if extra_fields.get("is_active") is False:
            raise ValueError("Superuser must have is_active=True.")

        return self.create_user(
            email,
            password,
            first_name,
            last_name,
            birth_date,
            **extra_fields,
        )

    @staticmethod
    def check_required_users_field(
        email,
        password,
        first_name,
        last_name,
        birth_date,
    ):
        if not email:
            raise ValueError("Users must have an email address")

        if not password:
            raise ValueError("User password must be not None")

        if not first_name:
            raise ValueError("Users must have a first name")

        if not last_name:
            raise ValueError("Users must have a last name")

        if not birth_date:
            raise ValueError("Users must have a birth_date")
