from datetime import datetime, timedelta

from django.core.serializers import serialize
from django.db.models import Q
from django.shortcuts import render
from django.utils.autoreload import raise_last_exception
from rest_framework import viewsets, status
from rest_framework.exceptions import NotFound
from rest_framework.generics import (
    GenericAPIView,
    RetrieveAPIView,
    get_object_or_404,
    DestroyAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from posts.serializer import ShowAllPostsSerializer
from .permissions import NotAuthenticated
from .models import User, Friendship, PreRegistration
from .serializer import (
    UserSerializer,
    AddUserSerializer,
    ChangeUserSerializer,
    EmptySerializer,
    ConfirmationEmailSerializer,
)
from .utils import SendMail

from decouple import config
from random import randint
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.cache import cache
from .tasks import send_welcome_email, send_confirmation_code

from chat.models import Chat, ChatLastSeen
from django.core.cache import cache


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для просмотра и редактирования пользователей.
    Поддерживает все стандартные действия CRUD через /users/.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class CreateAccauntView(GenericAPIView):
    """
    Представление для создания аккаунта с предварительной регистрацией.
    Проверяет уникальность email и username, сохраняет данные во временную модель PreRegistration
    и отправляет код подтверждения на почту.
    """

    queryset = User.objects.all()
    serializer_class = AddUserSerializer
    permission_classes = [NotAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            if User.objects.filter(email=serializer.validated_data["email"]).exists():
                return Response({"error": "This email already logged in "}, status=400)

            if User.objects.filter(
                username=serializer.validated_data["username"]
            ).exists():
                return Response({"error": "This username already is taken"}, status=400)

            email = serializer.validated_data["email"]
            username = serializer.validated_data["username"]
            name = serializer.validated_data["name"]

            code = randint(10000, 99999)

            PreRegistration.objects.create(
                email=email,
                username=username,
                name=name,
                code=code,
            )

            send_confirmation_code.delay(email_to=email, code=code)

            return Response(
                {
                    "message": "please verify your email",
                    "next": "api/v1/user/confirm-email",
                    "email": email,
                },
                status=201,
            )

        except Exception as e:
            return Response({"error": str(e)})


class ConfirmEmailView(GenericAPIView):
    """
    Представление для подтверждения email с помощью кода.
    Проверяет корректность и срок действия кода. При успешной проверке создаёт пользователя.
    """

    queryset = []
    permission_classes = [AllowAny]
    serializer_class = ConfirmationEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            code = serializer.validated_data["code"]
            email = serializer.validated_data["email"]

            try:
                user = PreRegistration.objects.filter(email=email).first()
            except PreRegistration.DoesNotExist:
                return Response({"error": "Email not found"}, status=404)

            if user.code != code:
                return Response({"error": "Invalid code"}, status=400)

            if user.created_at < timezone.now() - timedelta(minutes=15):
                user.delete()
                return Response({"error": "Code expired"}, status=400)

            new_user = User.objects.create(
                username=user.username,
                email=user.email,
                name=user.name,
                avatar=user.avatar,
            )
            user.delete()

            send_welcome_email.delay(user.email, user.name)

            return Response(
                {"message": "Email confirmed, account created", "user_id": new_user.id},
                status=201,
            )

        except Exception as e:
            return Response({"error": str(e)})


class GetPreciseUserView(RetrieveAPIView):
    """
    Получение информации о конкретном пользователе по ID.
    Возвращает сериализованные данные пользователя.
    """

    lookup_field = "id"
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs["id"]
        cache_key = f"cache_user_{user_id}"

        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound(detail="User with this ID does not exist.")

        serializer = self.get_serializer(user)
        data = serializer.data
        cache.set(cache_key, data, timeout=60)
        return Response(data)


class ChangeUserProfileView(UpdateAPIView):
    """
    Представление для обновления данных пользователя по email (в URL).
    Использует ChangeUserSerializer для валидации и обновления.
    """

    queryset = User.objects.all()
    serializer_class = ChangeUserSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        return get_object_or_404(User, email=self.kwargs.get("id"))


class DeleteUserView(DestroyAPIView):
    """
    Представление для удаления пользователя по ID.
    """

    queryset = User.objects.all()
    lookup_field = "id"
    permission_classes = [AllowAny]


class ShowAllFriends(RetrieveAPIView):
    """
    Получение списка всех друзей пользователя (взаимная подписка).
    Возвращает список пользователей, с которыми установлена дружба.
    """

    lookup_field = "id"
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        cache_key = f"all_friends_{user.id}"
        cache_qr = cache.get(cache_key)
        if cache_qr:
            return Response(cache_qr)

        sent = Friendship.objects.filter(from_user=user, accepted=True).values_list(
            "to_user", flat=True
        )
        received = Friendship.objects.filter(to_user=user, accepted=True).values_list(
            "from_user", flat=True
        )
        friends_id = list(sent) + list(received)
        friends = User.objects.filter(id__in=friends_id)

        serializer = self.get_serializer(friends, many=True)
        data = serializer.data
        cache.set(cache_key, data, timeout=60)
        return Response(data)


class RequestsListFriendShipView(RetrieveAPIView):
    """
    Входящие запросы в друзья (тебе ещё нужно принять).
    """

    lookup_field = "id"
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        cache_key = f"friend_requests_{user.id}"
        cached = cache.get(cache_key)
        if cached:
            return Response({"data": cached})

        requests = Friendship.objects.filter(
            to_user=user,
            accepted=False,
        ).select_related("from_user")

        users = [f.from_user for f in requests]
        serializer = self.get_serializer(users, many=True)
        data = serializer.data
        cache.set(cache_key, data, timeout=60)
        return Response({"data": data})


class AcceptOrDenyFriendShip(GenericAPIView):
    """
    Обработка действий над запросом в друзья: принятие или отклонение.
    В зависимости от параметра 'action' в URL выполняет нужное действие.
    """

    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = EmptySerializer

    def post(self, request, *args, **kwargs):
        try:
            if kwargs["action"] == "accept":
                user = User.objects.get(id=kwargs["id"])
                from_who = User.objects.get(id=kwargs["from_who"])
                friend_request = Friendship.objects.filter(
                    to_user=user, from_user=from_who
                ).first()

                chat = Chat.objects.create(to_user=user, from_user=from_who)
                ChatLastSeen.objects.create(chat=chat, user=user)
                ChatLastSeen.objects.create(chat=chat, user=from_who)

                if not friend_request:
                    return Response(
                        {"error": "Friend request not found."},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                friend_request.accepted = True
                friend_request.save()
                return Response({"status": "Friend request accepted."})
            elif kwargs["action"] == "deny":
                return Response(
                    {"status": "Friend request denied. Subscription remains."}
                )

            else:
                return Response(
                    {"error": "Invalid action. Use 'accept' or 'deny'."}, status=400
                )
        except Exception as e:
            return Response({"error": str(e)})


class SubscribeView(GenericAPIView):
    """
    Отправка запроса на добавление в друзья (односторонняя подписка).
    Запрещает подписку на самого себя и повторные запросы.
    """

    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = EmptySerializer

    def post(self, request, *args, **kwargs):
        try:
            from_ = User.objects.get(id=kwargs["id"])
            to_ = User.objects.get(id=kwargs["to"])

            if from_ == to_:
                return Response(
                    {"error": "Cannot subscribe to yourself."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            existing = Friendship.objects.filter(from_user=from_, to_user=to_).first()
            if existing:
                return Response(
                    {"message": "Already sent request or already subscribed."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            friend_request = Friendship.objects.create(from_user=from_, to_user=to_)
            return Response({"success": True}, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SubscribesListView(RetrieveAPIView):
    """
    Пользователи, на которых ты подписан (ожидают подтверждения).
    """

    lookup_field = "id"
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        cache_key = f"subscribed_to_{user.id}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        sent = Friendship.objects.filter(from_user=user, accepted=False).values_list(
            "to_user", flat=True
        )
        users = User.objects.filter(id__in=sent)
        serializer = self.get_serializer(users, many=True)
        data = serializer.data
        cache.set(cache_key, data, timeout=60)
        return Response(data)


class SubscribersListView(RetrieveAPIView):
    """
    Пользователи, которые подписались на тебя (ждут подтверждения).
    """

    lookup_field = "id"
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        cache_key = f"subscribers_of_{user.id}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        sent = Friendship.objects.filter(to_user=user, accepted=False).values_list(
            "from_user", flat=True
        )
        users = User.objects.filter(id__in=sent)
        serializer = self.get_serializer(users, many=True)
        data = serializer.data
        cache.set(cache_key, data, timeout=60)
        return Response(data)


class DeleteFriendView(GenericAPIView):
    """
    Удаление друга из списка друзей (взаимная дружба разрывается).
    После удаления создаётся односторонняя подписка со стороны бывшего друга.
    """

    permission_classes = [AllowAny]
    serializer_class = EmptySerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=kwargs["id"])
            whom = User.objects.get(id=kwargs["whom"])

            friendship = Friendship.objects.filter(
                Q(from_user=user, to_user=whom) | Q(from_user=whom, to_user=user),
                accepted=True,
            ).first()

            if not friendship:
                return Response(
                    {"error": "Friendship not found."}, status=status.HTTP_404_NOT_FOUND
                )

            friendship.delete()

            other = (
                friendship.from_user
                if friendship.from_user != user
                else friendship.to_user
            )

            Friendship.objects.create(from_user=other, to_user=user, accepted=False)

            return Response(
                {"status": "Unfriended. Now one-way subscription."},
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
