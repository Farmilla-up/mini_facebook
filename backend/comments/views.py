from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    DestroyAPIView,
    UpdateAPIView,
    GenericAPIView,
)
from rest_framework.permissions import AllowAny
from six import raise_from
from posts.models import Post
from users.models import User
from .models import Comment
from comments.serializer import CommentCreateSerializer, CommentSerializer
from django.core.cache import cache


class CreateCommentView(GenericAPIView):
    """
    Позволяет добавить коментарий, он может быть дочерним (т е ответом на какой то ), а может и не быть
    """

    serializer_class = CommentCreateSerializer
    permission_classes = [AllowAny]
    queryset = Comment.objects.all()

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

            post = get_object_or_404(Post, id=self.kwargs.get("post_id"))
            owner = get_object_or_404(User, id=self.kwargs.get("id"))
            text = data["text"]

            parent_comment_id = self.kwargs.get("parent_comment_id")

            if not parent_comment_id:
                comment = Comment.objects.create(
                    to_post=post, from_who=owner, text=text
                )
            else:
                parent_comment = get_object_or_404(
                    Comment, id=parent_comment_id)
                comment = Comment.objects.create(
                    to_post=post,
                    from_who=owner,
                    text=text,
                    parent_comment=parent_comment,
                )

            post.comments_number += 1
            post.save()
            return Response({"success": True}, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=400)


class ListOfComments(ListAPIView):
    """
    Показывает все коментарии на пост
    """

    serializer_class = CommentSerializer
    permission_classes = [AllowAny]
    queryset = Comment.objects.all()

    def get(self, request, *args, **kwargs):
        post_id = self.kwargs["post_id"]
        cache_key = f"comments_for_post_{post_id}"
        data = cache.get(cache_key)

        if data is not None:
            return Response(data)

        queryset = Comment.objects.filter(to_post=post_id)
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        cache.set(cache_key, data, timeout=30)
        return Response(data)


class DeleteCommentView(DestroyAPIView):
    """
    Удаляет коментарий и все ответы на него соотвественно
    """

    permission_classes = [AllowAny]
    queryset = Comment.objects.all()
    lookup_field = "id"

    def perform_destroy(self, instance):
        def count_total_comments(comment):
            """
            считает кол во ответов на коментарий (рекурсивно)
            :param comment:
            :return:
            """
            count = 1
            for reply in comment.replies.all():
                count += count_total_comments(reply)
            return count

        total_to_delete = count_total_comments(instance)
        post = instance.to_post
        post.comments_number = max(0, post.comments_number - total_to_delete)
        post.save()
        instance.delete()


class ChangeCommentView(UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
