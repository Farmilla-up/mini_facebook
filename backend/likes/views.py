from django.shortcuts import render
from django.views.generic import CreateView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView, GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from likes.models import Like
from posts.models import Post
from posts.serializer import ShowAllPostsSerializer
from users.models import User
from users.serializer import EmptySerializer


# Create your views here.



class LikeActionPostView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class =  EmptySerializer


    def create(self, request, *args, **kwargs):
        try:
            from_user = User.objects.get(id=self.kwargs["id"])
            to_post = Post.objects.get(id=self.kwargs["post_id"])

            like_qs = Like.objects.filter(from_who=from_user, to_post=to_post)

            if like_qs.exists():
                like_qs.delete()
                to_post.likes_number -= 1
                return Response({"status": "unliked"}, status=status.HTTP_200_OK)
            else:
                Like.objects.create(from_who=from_user, to_post=to_post)
                to_post.likes_number += 1
                return Response({"status": "liked"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MyLikesView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = Like.objects.all()
    serializer_class = ShowAllPostsSerializer

    def get_queryset(self):
        user = User.objects.get(id = self.kwargs['id'])
        liked = Like.objects.filter(from_who = user).values_list('to_post_id', flat= True)
        return Post.objects.filter(id__in = liked).order_by("-created_at")







