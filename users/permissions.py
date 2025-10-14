from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allow access if user is admin or owns the object.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_staff
            or request.user.is_superuser
            or obj == request.user
        )
