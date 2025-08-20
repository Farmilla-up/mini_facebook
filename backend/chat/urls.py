from django.urls import path
from .views import ViewMyChats, ViewPreciseChat, WriteMessage, DeleteChat, LastSeenView

urlpatterns = [
    path("<uuid:id>/chats/", ViewMyChats.as_view(), name="my_chats"),
    path(
        "<uuid:id>/my_chat/<int:chat_id>/",
        ViewPreciseChat.as_view(),
        name="precsise_chat",
    ),
    path(
        "<uuid:id>/write/<int:chat_id>/", WriteMessage.as_view(), name="write_message"
    ),
    path("<uuid:id>/delete/<int:chat_id>/",
         DeleteChat.as_view(), name="delete_chat"),
    path(
        "<uuid:id>/last_seen/<int:chat_id>/", LastSeenView.as_view(), name="last_seen"
    ),
]
