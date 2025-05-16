from django.core.serializers import serialize
from rest_framework import serializers
from .models import Post


class ShowAllPostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"


class AddPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        exclude = ["post_id", "owner_id", "created_at", "updated_at", "likes_number"]
