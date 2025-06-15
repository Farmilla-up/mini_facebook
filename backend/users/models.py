from django.db import models
import uuid


class User(models.Model):
    """
    Основная модель пользователя.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=30, verbose_name="Имя")
    username = models.CharField(max_length=30, verbose_name="Юз")
    email = models.EmailField(verbose_name="e-mail")
    avatar = models.ImageField(
        upload_to="photo", null=True, blank=True, verbose_name="Ава"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Когда зареган")
    friends = models.ManyToManyField(
        "self", through="Friendship", symmetrical=False, related_name="friends_of"
    )

    # закрытый ли профиль
    # password
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
