from rest_framework import permissions


class AuthorModifyOrReadOnly1(permissions.IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return  request.user == obj.user
    
class AuthorModifyOrReadOnly2(permissions.IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return  request.user == obj