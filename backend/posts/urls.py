from django.urls import path

from posts.views import (
    ShowAllPostsView,
    ShowPrecisePostView,
    AddPostView,
    DeletePostView, MyNotifications,
)

urlpatterns = [
    path("<uuid:id>/posts/", ShowAllPostsView.as_view(), name="show_all_user_posts"),
    path(
        "<uuid:id>/precise/",
        ShowPrecisePostView.as_view(),
        name="show_precise_post",
    ),
    path("<uuid:id>/create/", AddPostView.as_view(), name="add_post_view"),
    path("<uuid:id>/delete/", DeletePostView.as_view(), name="delete_post"),
    path("<uuid:id>/notifications/", MyNotifications.as_view(), name = "my_notifications")
]
