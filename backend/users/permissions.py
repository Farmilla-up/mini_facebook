from rest_framework.permissions import IsAuthenticated, BasePermission


class NotAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return not request.user or not request.user.is_authenticated



