from django.db import models
import uuid


class User(models.Model):
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

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.name


class Friendship(models.Model):
    from_user = models.ForeignKey(
        "User", related_name="sent_requests", on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        "User", related_name="received_requests", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    # в будущем добавить is denied
