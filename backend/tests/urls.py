from django.urls import path
from .views import (
    CreateTestChatView,
    CreateTestUsersView,
    CreateTestPostView,
    CreateTestFriendshipView,
)


urlpatterns = [
    path("create_chat/", CreateTestChatView.as_view()),
    path("create_user/", CreateTestUsersView.as_view()),
    path("create_friendship/", CreateTestFriendshipView.as_view()),
    path("create_post/", CreateTestPostView.as_view()),
]
