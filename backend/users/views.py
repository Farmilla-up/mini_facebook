from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.generics import GenericAPIView, RetrieveAPIView, get_object_or_404, DestroyAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .permissions import NotAuthenticated
from .models import User, Friendship
from .serializer import UserSerializer, AddUserSerializer, ChangeUserSerializer


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

            if User.objects.filter(email=serializer.validated_data["username"]).exists():
                return Response({"error": "This username already is taken"}, status=400)

            serializer.save()
            return Response({"data": serializer.data}, status=201)

        except Exception as e:
            return Response({"error": str(e)})



class GetPreciseUserView(RetrieveAPIView):
    lookup_field = 'id'
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def get_object(self):
        user_id = self.kwargs['id']
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
    lookup_field = 'id'
    permission_classes = [AllowAny]


class ShowAllFriends(RetrieveAPIView):
    lookup_field = 'id'
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        sent = Friendship.objects.filter(from_user = user, accepted = True).values_list('to_user', flat=True)
        received = Friendship.objects.filter(from_user = user, accepted = True).values_list('from_user', flat=True)
        friends_id = list(sent) + list(received)
        friends = User.objects.filter(id__in = friends_id)

        serializer = self.get_serializer(friends, many = True)
        return Response(serializer.data)
