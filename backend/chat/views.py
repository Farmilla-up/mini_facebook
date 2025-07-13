from django.shortcuts import render
from rest_framework.generics import (
    GenericAPIView,
    RetrieveAPIView,
    get_object_or_404,
    DestroyAPIView,
    UpdateAPIView,
    ListAPIView
)
from rest_framework.response import Response
from .models import Chat
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from .serializer import ChatsSerializer
from users.models import User
from django.db.models import Q

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

        