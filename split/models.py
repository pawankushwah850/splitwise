from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser as BaseUser
from django.contrib.auth.models import UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        if not email:
            raise ValueError("The given email must be set")

        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(BaseUser):
    username = None
    email = models.EmailField(_("email address"), unique=True, db_index=True)
    phone_number = PhoneNumberField()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()


class SplitAmountToUser(models.Model):
    borrow_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name="borrow_by")  # who is giving money
    borrow_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="borrow_from")  # who is taking money
    amount = models.DecimalField(decimal_places=2, max_digits=8)

    created_at = models.DateTimeField(auto_now=True, auto_created=True)

    class Meta:
        unique_together = (
            "borrow_from",
            "borrow_by",
        )
