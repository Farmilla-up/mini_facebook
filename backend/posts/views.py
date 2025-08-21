from linecache import cache

from django.core.serializers import serialize
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.exceptions import NotFound
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    RetrieveAPIView,
    DestroyAPIView,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from posts.serializer import (
    ShowAllPostsSerializer,
    AddPostSerializer,
    NotificationSerializer,
)
from users.models import User
from .models import Post, Notification
from django.core.cache import cache
from .tasks import notify_friends

# Create your views here.


class ShowAllPostsView(ListAPIView):
    """
    показывает все посты принадлежащие кому то
    """

    serializer_class = ShowAllPostsSerializer
    queryset = Post.objects.all()

    def list(self, request, *args, **kwargs):
        user_id = self.kwargs.get("id")
        cache_key = f"posts_from_user_{user_id}"
        cache_qr = cache.get(cache_key)
        if cache_qr:
            return Response(cache_qr)

        queryset = Post.objects.filter(owner_id=user_id).order_by("-created_at")
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        cache.set(cache_key, data, timeout=60)
        return Response(data)


class ShowPrecisePostView(RetrieveAPIView):
    """
    Показывает пост по айди
    """

    queryset = Post.objects.all()
    permission_classes = [AllowAny]
    serializer_class = ShowAllPostsSerializer

    def get(self, request, *args, **kwargs):
        try:
            post_id = self.kwargs.get("id")
            cache_key = f"post_{post_id}"
            cached_post = cache.get(cache_key)

            if cached_post:
                return Response(cached_post)

            post = Post.objects.get(id=post_id)

            serializer = self.get_serializer(post)
            data = serializer.data
            cache.set(cache_key, data, timeout=60)

            return Response(data)
        except Exception as e:
            return Response({"error": str(e)})


class AddPostView(GenericAPIView):
    """
    Добавляет пост
    """

    serializer_class = AddPostSerializer
    permission_classes = [AllowAny]
    queryset = Post.objects.all()

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

            if not data["text"] and not data["title"] and not data["file"]:
                return Response({"error": "Can't be empty"})
            user_id = kwargs["id"]
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=404)

            serializer.save(owner=user)
            post = serializer.instance
            notify_friends.delay(user.id, post.id)
            return Response({"data": serializer.data}, status=201)

        except Exception as e:
            return Response({"error": str(e)})


class DeletePostView(DestroyAPIView):
    """
    удаляет пост по айди
    """

    permission_classes = [AllowAny]
    queryset = Post.objects.all()
    lookup_field = "id"

    def perform_destroy(self, instance):
        instance.delete()


class MyNotifications(ListAPIView):
    """Мои оповещения"""

    permission_classes = [AllowAny]
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()

    def list(self, request, *args, **kwargs):
        user_id = kwargs.get("id")
        cache_key = f"notifications_about_post_{user_id}"
        cache_qr = cache.get(cache_key)

        if cache_qr:
            return cache_qr

        user = User.objects.get(id=user_id)

        queryset = Notification.objects.filter(recipient=user).order_by("-created_at")
        cache.set(cache_key, queryset, timeout=60)

        return queryset
