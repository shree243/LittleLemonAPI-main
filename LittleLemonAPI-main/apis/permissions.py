from rest_framework import permissions


class IsManager(permissions.BasePermission):
    """
    Check permission if the user is in 'Manager' group
    """

    def has_permission(self, request, view):
        if request.user and request.user.groups.filter(name="Manager"):
            return True
        return False


class IsDeliveryCrew(permissions.BasePermission):
    """
    Check permission if the user is in 'Delivery Crew' group
    """

    def has_permission(self, request, view):
        if request.user and request.user.groups.filter(name="Delivery Crew"):
            return True
        return False
