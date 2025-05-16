from django.urls import path

from posts.views import (
    ShowAllPostsView,
    ShowPrecisePostView,
    AddPostView,
    DeletePostView,
)

urlpatterns = [
    path("posts/", ShowAllPostsView.as_view(), name="show_all_user_posts"),
    path(
        "precise/<uuid:post_id>/",
        ShowPrecisePostView.as_view(),
        name="show_precise_post",
    ),
    path("create/", AddPostView.as_view(), name="add_post_view"),
    path("delete/<uuid:post_id>/", DeletePostView.as_view(), name="delete_post"),
]
