from django.db import models


class Chat(models.Model):
    from_user = models.ForeignKey(
        "users.User",
        related_name="chat_who_created",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    to_user = models.ForeignKey(
        "users.User",
        related_name="chat_who_accepted",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Гарантирует только один чат у пользователей"""
        unique_together = ('to_user', 'from_user')


class Message(models.Model):
    text = models.TextField(max_length=1000)
    to_chat = models.ForeignKey(
        "Chat",
        related_name="message_to_chat",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    from_who = models.ForeignKey(
        "users.User",
        related_name="message_owner",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
