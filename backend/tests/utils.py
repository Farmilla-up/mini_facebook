from datetime import timezone
from random import randint
from users.models import User, Friendship
from chat.models import Chat, ChatLastSeen
from posts.models import Post
from django.contrib.auth.hashers import make_password


class TestUserManager:
    """
    Класс-менеджер для создания и управления тестовыми объектами:
    - Два пользователя (user1 и user2)
    - Чат между ними
    - Дружба между ними
    - Пост одного из пользователей

    Использует get_or_create, чтобы не создавать дубликаты при повторном вызове.
    """

    user1 = None
    user2 = None

    @classmethod
    def create_users(cls):
        """
        Создает двух тестовых пользователей.
        Если пользователи уже существуют, возвращает существующих.
        """
        if cls.user1 and cls.user2:
            return cls.user1, cls.user2

        rand1, rand2 = randint(0, 1000000), randint(0, 1000000)
        cls.user1, _ = User.objects.get_or_create(
            username=f"@Test_username{rand1}",
            defaults={
                "name": f"Test_user_{rand1}",
                "email": f"Test_email_{rand1}@gmail.com",
                "password": make_password("12345"),
            },
        )
        cls.user2, _ = User.objects.get_or_create(
            username=f"@Test_username{rand2}",
            defaults={
                "name": f"Test_user_{rand2}",
                "email": f"Test_email_{rand2}@gmail.com",
                "password": make_password("12345"),
            },
        )
        return cls.user1, cls.user2

    @classmethod
    def create_chat(cls):
        """
        Создает чат между двумя тестовыми пользователями
        и добавляет записи о последнем просмотре чата.
        Возвращает: (chat, user1, user2)
        """
        user1, user2 = cls.create_users()
        chat = Chat.objects.create(from_user=user1, to_user=user2)
        ChatLastSeen.objects.create(chat=chat, user=user1)
        ChatLastSeen.objects.create(chat=chat, user=user2)
        return chat, user1, user2

    @classmethod
    def create_friendship(cls):
        """
        Создает дружбу между двумя тестовыми пользователями.
        Возвращает: (friendship, user1, user2)
        """
        cls.create_users()
        friendship, _ = Friendship.objects.get_or_create(
            user1=cls.user1, user2=cls.user2
        )
        return friendship, cls.user1, cls.user2

    @classmethod
    def create_post(cls, author=None, content=None):
        """
        Создает пост одного из тестовых пользователей.
        Аргументы:
        - author: пользователь, который создает пост (по умолчанию user1)
        - content: текст поста (по умолчанию: сгенерированный тестовый текст)
        Возвращает: (post, author)
        """
        cls.create_users()
        if not author:
            author = cls.user1
        post = Post.objects.create(
            author=author,
            content=content or f"Test post by {author.username} at {timezone.now()}",
        )
        return post, author
