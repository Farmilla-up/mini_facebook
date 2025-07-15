from django.shortcuts import render
from rest_framework.generics import (
    GenericAPIView,
    RetrieveAPIView,
    get_object_or_404,
    DestroyAPIView,
    UpdateAPIView,
    ListAPIView, 
    CreateAPIView
)
from rest_framework.response import Response
from .models import Chat, Message
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from .serializer import ChatsSerializer, MessageSerializer, WriteMessageSerializer
from users.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404


class ViewMyChats(ListAPIView): 
    serializer_class = ChatsSerializer
    permission_classes = [AllowAny]
    queryset = Chat.objects.all()

    def list(self, request, *args, **kwargs):
        try: 
            user_id = self.kwargs["id"]
            cache_key = f'user_chats_{user_id}'
            cached_data = cache.get(cache_key)

            if cached_data:
                return Response(cached_data)

            user = User.objects.get(id=user_id)
            user_chats = Chat.objects.filter(Q(from_user=user) | Q(to_user=user))

            serializer = self.get_serializer(user_chats, many=True, context={"user": user})

            data = serializer.data


            cache.set(cache_key, data, timeout=60)
            return Response(data)

        except Exception as e:
            return Response({"error": str(e)}, status=400)




class ViewPreciseChat(ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [AllowAny]
    queryset = Message.objects.all() 

    def list(self, request, *args, **kwargs): 
        try: 
            user_id = self.kwargs["id"]
            chat_id = self.kwargs["chat_id"]
            cache_key = f'chat_{chat_id}'
            cache_qr = cache.get(cache_key)

            if cache_qr: 
                return Response(cache_qr)

            user = get_object_or_404(User, id=user_id)
            chat = get_object_or_404(Chat, id=chat_id)

            messages = Message.objects.filter(
                to_chat=chat
            ).order_by("-created_at")

            serializer = self.get_serializer(messages, many=True)
            data = serializer.data

            cache.set(cache_key, data, timeout=60)
            return Response(data)

        except Exception as e: 
            return Response({"error": str(e)}, status=400)


class WriteMessage(CreateAPIView):
    serializer_class = WriteMessageSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        chat = get_object_or_404(Chat, id=self.kwargs["chat_id"])
        user = get_object_or_404(User, id=self.kwargs["id"])
        serializer.save(to_chat=chat, from_who=user)


class DeleteChat(DestroyAPIView):
    pass 


        