from django.shortcuts import render
from rest_framework.generics import (
    GenericAPIView,
    RetrieveAPIView,
    get_object_or_404,
    DestroyAPIView,
    UpdateAPIView,
    ListAPIView,
    CreateAPIView,
)
from rest_framework.response import Response
from .models import Chat, Message, ChatLastSeen
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from .serializer import (
    ChatsSerializer,
    MessageSerializer,
    WriteMessageSerializer,
    LastSeenSerializer,
)
from users.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

"""Логика создания чата и LastSeen находится в AcceptOrDenyFriendShip"""


class ViewMyChats(ListAPIView):
    """Возвращает список чатов пользователя (с кешированием)."""

    serializer_class = ChatsSerializer
    permission_classes = [AllowAny]
    queryset = Chat.objects.all()

    def list(self, request, *args, **kwargs):
        try:
            user_id = self.kwargs["id"]
            cache_key = f"user_chats_{user_id}"
            cached_data = cache.get(cache_key)

            if cached_data:
                return Response(cached_data)

            user = User.objects.get(id=user_id)
            user_chats = Chat.objects.filter(
                Q(from_user=user) | Q(to_user=user))

            serializer = self.get_serializer(
                user_chats, many=True, context={"user": user}
            )

            data = serializer.data

            cache.set(cache_key, data, timeout=60)
            return Response(data)

        except Exception as e:
            return Response({"error": str(e)}, status=400)


class ViewPreciseChat(ListAPIView):
    """Возвращает список сообщений конкретного чата (с кешированием)."""

    serializer_class = MessageSerializer
    permission_classes = [AllowAny]
    queryset = Message.objects.all()

    def list(self, request, *args, **kwargs):
        try:
            user_id = self.kwargs["id"]
            chat_id = self.kwargs["chat_id"]
            cache_key = f"chat_{chat_id}"
            cache_qr = cache.get(cache_key)

            if cache_qr:
                return Response(cache_qr)

            user = get_object_or_404(User, id=user_id)
            chat = get_object_or_404(Chat, id=chat_id)

            messages = Message.objects.filter(
                to_chat=chat).order_by("-created_at")

            ChatLastSeen.objects.update_or_create(
                chat=chat, user=user, defaults={"last_seen": timezone.now()}
            )

            serializer = self.get_serializer(messages, many=True)
            data = serializer.data

            cache.set(cache_key, data, timeout=60)
            return Response(data)

        except Exception as e:
            return Response({"error": str(e)}, status=400)


class WriteMessage(CreateAPIView):
    """Создаёт новое сообщение в чате."""

    serializer_class = WriteMessageSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        chat = get_object_or_404(Chat, id=self.kwargs["chat_id"])
        user = get_object_or_404(User, id=self.kwargs["id"])
        serializer.save(to_chat=chat, from_who=user)
        ChatLastSeen.objects.update_or_create(
            chat=chat, user=user, defaults={"last_seen": timezone.now()}
        )


class LastSeenView(GenericAPIView):
    """Показывает статус СОБЕСЕДНИКА (online / время последнего визита)."""

    permission_classes = [AllowAny]
    queryset = ChatLastSeen
    serializer_class = LastSeenSerializer

    def get(self, request, *args, **kwargs):
        try:
            user_id = self.kwargs["id"]
            chat_id = self.kwargs["chat_id"]
            cache_key = f"last_seen_{chat_id}_{user_id}"
            cache_qr = cache.get(cache_key)
            if cache_qr:
                return Response(cache_qr)

            user = get_object_or_404(User, id=user_id)
            chat = get_object_or_404(Chat, id=chat_id)

            if chat.from_user == user:
                other_user = chat.to_user

            else:
                other_user = chat.from_user

            last_seen_model = get_object_or_404(
                ChatLastSeen, chat=chat, user=other_user
            )
            last_seen = last_seen_model.last_seen
            _time = timezone.now() - last_seen

            if _time <= timedelta(seconds=30):
                status = "online"

            elif _time < timedelta(minutes=60):
                status = "last seen recently"

            elif _time < timedelta(days=1):
                status = "not long ago"
            else:
                status = "long ago"

            cache.set(cache_key, status, timeout=30)
            return Response({"status": status})

        except Exception as e:
            return Response({"error": str(e)}, status=400)


class DeleteChat(DestroyAPIView):
    pass
