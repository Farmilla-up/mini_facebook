from rest_framework.response import Response
from rest_framework.views import APIView
from .utils import TestUserManager


class CreateTestUsersView(APIView):
    """Создает или возвращает двух тестовых пользователей и возвращает их ID"""

    def get(self, request):
        user1, user2 = TestUserManager.create_users()
        return Response({"user1_id": {
            "id": user1.id,
            "email": user1.email,
            "password": 12345,
        },
            "user2_id": {
            "id": user2.id,
            "email": user2.email,
            "password": 12345,
        }})


class CreateTestChatView(APIView):
    """Создает чат между двумя тестовыми пользователями и возвращает ID чата и пользователей"""

    def get(self, request):
        chat, user1, user2 = TestUserManager.create_chat()
        return Response(
            {"chat_id": chat.id, "user1_id": user1.id, "user2_id": user2.id}
        )


class CreateTestFriendshipView(APIView):
    """Создает дружбу между двумя тестовыми пользователями и возвращает ID дружбы и пользователей"""

    def get(self, request):
        friendship, user1, user2 = TestUserManager.create_friendship()
        return Response(
            {"friendship_id": friendship.id, "user1_id": user1.id, "user2_id": user2.id}
        )


class CreateTestPostView(APIView):
    """Создает пост одного из тестовых пользователей и возвращает ID поста и автора"""

    def get(self, request):
        post, user = TestUserManager.create_post()
        return Response({"post_id": post.id, "user_id": user.id})
