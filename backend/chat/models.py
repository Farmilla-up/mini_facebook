from django.db import models
from users.models import User


class Chat(models.Model):
    """
    Модель, описывающая чат между двумя пользователями.

    Атрибуты:
        from_user (User): Пользователь, который создал чат.
        to_user (User): Пользователь, который принял приглашение/участвует в чате.
        created_at (datetime): Дата и время создания чата.
    """

    from_user = models.ForeignKey(
        "users.User",
        related_name="chat_who_created",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Пользователь, который инициировал чат",
    )
    to_user = models.ForeignKey(
        "users.User",
        related_name="chat_who_accepted",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Пользователь, который участвует в чате",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Дата и время создания чата"
    )

    class Meta:
        """
        Уникальность: между двумя пользователями может быть только один чат.
        """

        unique_together = ("to_user", "from_user")
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"

    def __str__(self):
        return f"Чат {self.from_user} ↔ {self.to_user} "


class Message(models.Model):
    """
    Модель, описывающая сообщение в чате.

    Атрибуты:
        text (str): Текст сообщения.
        to_chat (Chat): Чат, к которому относится сообщение.
        from_who (User): Автор сообщения.
        created_at (datetime): Время отправки сообщения.
    """

    text = models.TextField(
        max_length=1000, help_text="Текст сообщения (до 1000 символов)"
    )
    to_chat = models.ForeignKey(
        "Chat",
        related_name="message_to_chat",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Чат, в котором отправлено сообщение",
    )
    from_who = models.ForeignKey(
        "users.User",
        related_name="message_owner",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Автор сообщения",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Дата и время отправки сообщения"
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self):
        return f"Сообщение от {self.from_who} в чате {self.to_chat}"


class ChatLastSeen(models.Model):
    """
    Модель для отслеживания последнего прочитанного сообщения в чате
    конкретным пользователем.

    Атрибуты:
        chat (Chat): Чат, в котором отслеживается статус.
        user (User): Пользователь, для которого сохраняется отметка.
        last_seen (datetime): Время последнего прочтения.
    """

    chat = models.ForeignKey(
        Chat, on_delete=models.CASCADE, help_text="Чат, к которому относится отметка"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text="Пользователь, который читал чат"
    )
    last_seen = models.DateTimeField(
        auto_now=True, help_text="Дата и время последнего прочтения чата пользователем"
    )

    class Meta:
        """
        Уникальность: у одного пользователя может быть только одна отметка
        'последнего прочтения' для конкретного чата.
        """

        unique_together = ("chat", "user")
        verbose_name = "Последнее прочтение чата"
        verbose_name_plural = "Последние прочтения чатов"

    def __str__(self):
        return f"Последнее прочтение чата {self.chat} пользователем {self.user}"
