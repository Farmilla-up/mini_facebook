from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CreateAccauntView, GetPreciseUserView, ChangeUserProfileView, DeleteUserView

router = DefaultRouter()

urlpatterns = [
    path('registrate/', CreateAccauntView.as_view(), name="registration"),
    path('users/', UserViewSet.as_view({'get': 'list'}), name='users_view'),
    path("<str:id>/precise/",GetPreciseUserView.as_view(),  name = "get_precise_profile"),
    path("<str:id>/change/", ChangeUserProfileView.as_view(), name = "change_user"),
    path("<str:id>/delete/", DeleteUserView.as_view(), name = "delete_user")

]