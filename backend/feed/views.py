from django.contrib.admin.utils import lookup_field
from django.shortcuts import render
from kombu.asynchronous.http import Response
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from posts.models import Post
from posts.serializer import ShowAllPostsSerializer
from users.models import User, Friendship


class MyFeedView(ListAPIView):
    serializer_class = ShowAllPostsSerializer
    permission_classes = [AllowAny]
    queryset = Post.objects.all()

    def get_queryset(self):
        user = User.objects.get(id = self.kwargs['id'])

        friends_from_or_subscribed  = Friendship.objects.filter(from_user = user ).values_list("to_user", flat= True)
        friends_to = Friendship.objects.filter(to_user = user , accepted = True).values_list("from_user", flat= True)

        all_id = list(friends_to) + list(friends_from_or_subscribed)

        posts = Post.objects.filter(owner_id__in = all_id).order_by("-created_at")

        return posts

