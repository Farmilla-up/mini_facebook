from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    CreateAccauntView,
    GetPreciseUserView,
    ChangeUserProfileView,
    DeleteUserView,
    ShowAllFriends,
    RequestsListFriendShipView,
    AcceptOrDenyFriendShip,
    SubscribeView,
    SubscribesListView,
    SubscribersListView,
    DeleteFriendView,
    ConfirmEmailView,
    LoginView,
)

router = DefaultRouter()

urlpatterns = [
    path("registrate/", CreateAccauntView.as_view(), name="registration"),
    path("confirm-email/", ConfirmEmailView.as_view(), name="confirm_email"),
    path("login/", LoginView.as_view(), name="login"),
    path("users/", UserViewSet.as_view({"get": "list"}), name="users_view"),
    path(
        "<uuid:id>/precise/", GetPreciseUserView.as_view(), name="get_precise_profile"
    ),
    path("<uuid:id>/change/", ChangeUserProfileView.as_view(), name="change_user"),
    path("<uuid:id>/delete/", DeleteUserView.as_view(), name="delete_user"),
    path("<uuid:id>/friends/", ShowAllFriends.as_view(), name="show_all_friends"),
    path(
        "<uuid:id>/friends_request/",
        RequestsListFriendShipView.as_view(),
        name="friends_request",
    ),
    path(
        "<uuid:id>/accept_friendship/<uuid:from_who>/<str:action>/",
        AcceptOrDenyFriendShip.as_view(),
        name="accept_or_deny_friendship",
    ),
    path("<uuid:id>/subscribe/<uuid:to>/",
         SubscribeView.as_view(), name="subscribe"),
    path("<uuid:id>/subscribes/",
         SubscribesListView.as_view(), name="all_subscribes"),
    path(
        "<uuid:id>/subscribers/", SubscribersListView.as_view(), name="all_subscribers"
    ),
    path(
        "<uuid:id>/unfriend/<uuid:whom>/",
        DeleteFriendView.as_view(),
        name="all_subscribers",
    ),
]
# В будущем на лог ин
