from rest_framework.exceptions import NotFound
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    RetrieveAPIView,
    DestroyAPIView,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from posts.serializer import ShowAllPostsSerializer, AddPostSerializer
from users.models import User
from .models import Post

# Create your views here.


class ShowAllPostsView(ListAPIView):
    serializer_class = ShowAllPostsSerializer
    queryset = Post.objects.all()

    def get_object(self):
        return Post.objects.filter(owner_id=self.kwargs.get("id"))


class ShowPrecisePostView(RetrieveAPIView):
    queryset = Post.objects.all()
    permission_classes = [AllowAny]
    serializer_class = ShowAllPostsSerializer

    def get_object(self):
        try:
            post_id = self.kwargs.get("post_id")
            return Post.objects.get(post_id=post_id)
        except Post.DoesNotExist:
            raise NotFound("Пост не найден")


class AddPostView(GenericAPIView):
    serializer_class = AddPostSerializer
    permission_classes = [AllowAny]
    queryset = Post.objects.all()

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

            if not data["text"] and not data["title"] and not data["file"]:
                return Response({"error": "Can be empty"})
            user_id = kwargs.get("id")
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=404)

            serializer.save(owner_id=user)
            return Response({"data": serializer.data}, status=201)

        except Exception as e:
            return Response({"error": str(e)})


class DeletePostView(DestroyAPIView):
    permission_classes = [AllowAny]
    queryset = Post.objects.all()
    lookup_field = "post_id"

    def perform_destroy(self, instance):
        instance.delete()
