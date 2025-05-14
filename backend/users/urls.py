from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CreateAccauntView, GetPreciseUserView, ChangeUserProfileView, DeleteUserView, \
    ShowAllFriends

router = DefaultRouter()

urlpatterns = [
    path('registrate/', CreateAccauntView.as_view(), name="registration"),
    path('users/', UserViewSet.as_view({'get': 'list'}), name='users_view'),
    path("<uuid:id>/precise/",GetPreciseUserView.as_view(),  name = "get_precise_profile"),
    path("<uuid:id>/change/", ChangeUserProfileView.as_view(), name = "change_user"),
    path("<uuid:id>/delete/", DeleteUserView.as_view(), name = "delete_user"),
    path("<uuid:id>/friends/", ShowAllFriends.as_view(), name = 'show_all_friends'),
    path("<uuid:id>/post/", include("posts.urls"))

]