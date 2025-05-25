from celery.bin.control import status
from django.core.serializers import serialize
from django.shortcuts import render, get_object_or_404
from django.utils.autoreload import raise_last_exception
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, GenericAPIView
from rest_framework.permissions import AllowAny
from six import raise_from
from posts.models import Post
from users.models import User
from .models import Comment
from comments.serializer import CommentCreateSerializer, CommentSerializer


class CreateCommentView(GenericAPIView):
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
                comment = Comment.objects.create(to_post=post, from_who=owner, text=text)
            else:
                parent_comment = get_object_or_404(Comment, id=parent_comment_id)
                comment = Comment.objects.create(
                    to_post=post,
                    from_who=owner,
                    text=text,
                    parent_comment=parent_comment
                )

            post.comments_number += 1
            post.save()
            return Response({"success": True}, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=400)


class ListOfComments(ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]
    queryset = Comment.objects.all()

    def get_object(self):
        return Comment.objects.filter(id = self.kwargs["post_id"])




class DeleteCommentView(DestroyAPIView):
    permission_classes = [AllowAny]
    queryset = Comment.objects.all()
    lookup_field = "id"

    def perform_destroy(self, instance):
        def count_total_comments(comment):
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
    pass