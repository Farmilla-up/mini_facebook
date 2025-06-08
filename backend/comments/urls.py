from django.urls import path

from comments.views import CreateCommentView, ListOfComments, DeleteCommentView

urlpatterns = [
    path(
        "<uuid:id>/create/<uuid:post_id>/<int:parent_comment_id>/",
        CreateCommentView.as_view(),
        name="create_comment_as_reply",
    ),
    path(
        "<uuid:id>/create/<uuid:post_id>/",
        CreateCommentView.as_view(),
        name="create_comment",
    ),
    path("comments/<uuid:post_id>/", ListOfComments.as_view(), name="all_comments"),
    path("delete/<int:id>/", DeleteCommentView.as_view(), name="delete_comments"),
]
