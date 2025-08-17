from django.urls import include

from django.contrib import admin
from django.db import router
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenVerifyView,
    TokenRefreshView,
    TokenObtainPairView,
)
from users.views import UserViewSet

router = DefaultRouter()


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/user/", include("users.urls")),
    path("api/v1/feed/", include("feed.urls")),
    path("api/v1/like/", include("likes.urls")),
    path("api/v1/post/", include("posts.urls")),
    path("api/v1/chat/", include("chat.urls")),
    path("api/v1/test/", include("tests.urls")),
    path("api/v1/comment/", include("comments.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
