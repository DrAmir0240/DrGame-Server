from rest_framework.permissions import BasePermission


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "customer")
            and not request.user.customer.is_deleted
        )


class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "employee")
            and not request.user.employee.is_deleted
        )


class IsRepairman(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "repairman")


class IsMainManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "main_manager")


class IsCustomerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return (
            request.user.is_authenticated
            and hasattr(request.user, "customer")
            and not request.user.customer.is_deleted
        )


class IsTicketOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "customer")
            and obj.customer.user == request.user
        )


class IsSuperuserOrHasRole(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.is_superuser:
            return True
        return (
            hasattr(request.user, "customer")
            or hasattr(request.user, "business_customer")
            or hasattr(request.user, "employee")
            or hasattr(request.user, "main_manager")
        )
