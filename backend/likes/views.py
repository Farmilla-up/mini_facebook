from django.shortcuts import render
from django.views.generic import CreateView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    RetrieveAPIView,
    ListAPIView,
    GenericAPIView,
)
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from likes.models import Like
from posts.models import Post
from posts.serializer import ShowAllPostsSerializer
from users.models import User
from users.serializer import EmptySerializer


# Create your views here.


class LikeActionPostView(CreateAPIView):
    """
    Позволяет лайкнуть или УБРАТЬ лайк (т е дизлайков нет)
    """
    permission_classes = [AllowAny]
    serializer_class = EmptySerializer

    def create(self, request, *args, **kwargs):
        try:
            action = self.kwargs["action"]
            if action not in ("like", "away"):
                return Response(
                    {"error": "action must be 'like' or 'away'"}, status=400
                )
            from_user = User.objects.get(id=self.kwargs["id"])

            to_post = Post.objects.get(id=self.kwargs["post_id"])

            like_qs = Like.objects.filter(from_who=from_user, to_post=to_post)
            is_exist = like_qs.exists()

            if action == "away" and is_exist:
                like_qs.delete()
                to_post.likes_number -= max(0, to_post.likes_number + 1)
                to_post.save()
                return Response({"status": "unliked"}, status=status.HTTP_200_OK)

            elif action == "like" and not is_exist:
                Like.objects.create(from_who=from_user, to_post=to_post)
                to_post.likes_number += 1
                to_post.save()
                return Response({"status": "liked"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "action is not correct"}, status=400)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MyLikesView(ListAPIView):
    """
    Все посты которым ты поставил лайк
    """
    permission_classes = [AllowAny]
    queryset = Like.objects.all()
    serializer_class = ShowAllPostsSerializer

    def get_queryset(self):
        user = User.objects.get(id=self.kwargs["id"])
        liked = Like.objects.filter(from_who=user).values_list("to_post_id", flat=True)
        return Post.objects.filter(id__in=liked).order_by("-created_at")
