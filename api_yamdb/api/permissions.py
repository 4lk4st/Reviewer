from rest_framework import permissions


class ReviewCommentPermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user == obj.author and request.user.role == 'user')
            or (request.user.is_authenticated and request.user.role == 'admin')
            or (request.user.is_authenticated
                and request.user.role == 'moderator'))


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return (request.user.is_authenticated
                    and request.user.role == 'admin')


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == 'admin':
            return True
