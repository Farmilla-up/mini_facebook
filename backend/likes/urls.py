from django.urls import path

from likes.views import LikeActionPostView,MyLikesView

urlpatterns = [
    path("<uuid:id>/like_action/<uuid:post_id>/", LikeActionPostView.as_view(), name = 'like_action_post'),
    path("<uuid:id>/my_likes/", MyLikesView.as_view(), name = "my_likes")
]