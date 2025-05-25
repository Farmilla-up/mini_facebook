from django.urls import path, include

from feed.views import MyFeedView

urlpatterns = [path("<uuid:id>/main/", MyFeedView.as_view(), name="feed")]
