from rest_framework import permissions
from users.models import User


class ReviewCommentPermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user == obj.author
                and request.user.role == User.USER_ROLE_USER)
            or (request.user.is_authenticated
                and request.user.role == User.USER_ROLE_ADMIN)
            or (request.user.is_authenticated
                and request.user.role == User.USER_ROLE_MODERATOR))


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return (request.user.is_authenticated
                    and request.user.role == User.USER_ROLE_ADMIN)


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if (
            request.user.is_authenticated
            and request.user.role == User.USER_ROLE_ADMIN
        ):
            return True
