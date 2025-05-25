from django.db.models import TextField, Model
from rest_framework import serializers

from comments.models import Comment


class CommentCreateSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=10000)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        exclude = ["created_at", "updated_at"]
