from posts.models import Post
from users.models import Friendship
from rest_framework import serializers


class TestFriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ["id", "from_user", "to_user"]


class TestPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "author", "content"]
