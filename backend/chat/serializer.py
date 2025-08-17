from rest_framework import serializers
from .models import Chat, Message, ChatLastSeen


class ChatsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка чатов.

    Дополнительные поля:
        chat_name (str): Имя собеседника в чате, вычисляется динамически
                         на основе текущего пользователя.
    """

    chat_name = serializers.SerializerMethodField()

    class Meta:  # Запрещена на территории Российской Федерации
        model = Chat
        fields = ["id", "chat_name"]

    def get_chat_name(self, obj):
        """
        Определяет имя чата для отображения.

        Если текущий пользователь (из контекста сериализатора) является
        инициатором чата, то возвращаем имя второго участника.
        В противном случае — инициатора.

        Args:
            obj (Chat): Экземпляр модели Chat.

        Returns:
            str: Имя собеседника.
        """
        user = self.context.get("user")
        if obj.from_user == user:
            return str(obj.to_user)
        return str(obj.from_user)


class MessageSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор для модели Message.
    Сериализует все поля модели.
    """

    class Meta:
        model = Message
        fields = "__all__"


class WriteMessageSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания сообщений.

    Ограничивает ввод только текстом сообщения.
    """

    class Meta:
        model = Message
        fields = ["text"]

    def create(self, validated_data):
        """
        Создаёт новое сообщение.

        Args:
            validated_data (dict): Валидированные данные из запроса.

        Returns:
            Message: Созданное сообщение.
        """
        return Message.objects.create(**validated_data)


class LastSeenSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отметки последнего прочтения чата.
    Содержит только поле last_seen.
    """

    class Meta:
        model = ChatLastSeen
        fields = ["last_seen"]
