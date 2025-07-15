from django.core.serializers import serialize
from rest_framework import serializers
from .models import Post, Notification


class ShowAllPostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"


class AddPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        exclude = [
            "id",
            "owner",
            "created_at",
            "updated_at",
            "likes_number",
            "comments_number",
        ]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        exclude = ["recipient"]
