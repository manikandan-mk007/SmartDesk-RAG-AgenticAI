from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    message = "Only admin users can access this resource."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "ADMIN"
        )


class IsAgentRole(BasePermission):
    message = "Only support agents can access this resource."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "AGENT"
        )


class IsUserRole(BasePermission):
    message = "Only normal users can access this resource."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "USER"
        )


class IsAgentOrAdminRole(BasePermission):
    message = "Only agents or admins can access this resource."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ["AGENT", "ADMIN"]
        )


class IsUserAgentOrAdminRole(BasePermission):
    message = "Authenticated users only."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ["USER", "AGENT", "ADMIN"]
        )