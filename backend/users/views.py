from django.db.models import Q
from django.shortcuts import render
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

from .permissions import NotAuthenticated
from .models import User, Friendship
from .serializer import (
    UserSerializer,
    AddUserSerializer,
    ChangeUserSerializer,
    EmptySerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class CreateAccauntView(GenericAPIView):
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
                email=serializer.validated_data["username"]
            ).exists():
                return Response({"error": "This username already is taken"}, status=400)

            serializer.save()
            return Response({"data": serializer.data}, status=201)

        except Exception as e:
            return Response({"error": str(e)})


class GetPreciseUserView(RetrieveAPIView):
    lookup_field = "id"
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def get_object(self):
        user_id = self.kwargs["id"]
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound(detail="User with this email does not exist.")


class ChangeUserProfileView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ChangeUserSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        return get_object_or_404(User, email=self.kwargs.get("id"))


class DeleteUserView(DestroyAPIView):
    queryset = User.objects.all()
    lookup_field = "id"
    permission_classes = [AllowAny]


class ShowAllFriends(RetrieveAPIView):
    lookup_field = "id"
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        sent = Friendship.objects.filter(from_user=user, accepted=True).values_list(
            "to_user", flat=True
        )
        received = Friendship.objects.filter(to_user=user, accepted=True).values_list(
            "from_user", flat=True
        )
        friends_id = list(sent) + list(received)
        friends = User.objects.filter(id__in=friends_id)

        serializer = self.get_serializer(friends, many=True)
        return Response(serializer.data)


class RequestsListFriendShipView(RetrieveAPIView):
    lookup_field = "id"
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            requests = Friendship.objects.filter(
                to_user=user,
                accepted=False,
            ).select_related("from_user")

            users = [f.from_user for f in requests]
            serializer = self.get_serializer(users, many=True)
            return Response({"data": serializer.data})
        except Exception as e:
            return Response({"error": str(e)})


class AcceptOrDenyFriendShip(GenericAPIView):
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
    lookup_field = "id"
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        sent = Friendship.objects.filter(from_user=user, accepted=False).values_list(
            "to_user", flat=True
        )
        users = User.objects.filter(id__in=sent)

        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)


class SubscribersListView(RetrieveAPIView):
    lookup_field = "id"
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            sent = Friendship.objects.filter(to_user=user, accepted=False).values_list(
                "from_user", flat=True
            )
            users = User.objects.filter(id__in=sent)

            serializer = self.get_serializer(users, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)})


class DeleteFriendView(GenericAPIView):
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
