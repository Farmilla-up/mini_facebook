from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
import uuid


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email должен быть указан")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser должен иметь is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=30, verbose_name="Имя")
    username = models.CharField(max_length=30, verbose_name="Юз")
    email = models.EmailField(unique=True, verbose_name="e-mail")
    avatar = models.ImageField(
        upload_to="photo", null=True, blank=True, verbose_name="Ава"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Когда зареган")
    friends = models.ManyToManyField(
        "self", through="Friendship", symmetrical=False, related_name="friends_of"
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "name"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.name


class PreRegistration(models.Model):
    """
    Модель для хранения предварительных регистраций с кодом подтверждения.
    """

    email = models.EmailField(max_length=100)
    name = models.CharField(max_length=30, verbose_name="Имя")
    code = models.IntegerField()
    username = models.CharField(max_length=30, verbose_name="Юз")
    password = models.CharField(max_length=255)
    avatar = models.ImageField(
        upload_to="photo", null=True, blank=True, verbose_name="Ава"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Friendship(models.Model):
    """
    Промежуточная модель для связи друзей и подписок.
    """

    from_user = models.ForeignKey(
        "User", related_name="sent_requests", on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        "User", related_name="received_requests", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
