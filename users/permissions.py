from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
from django.http import HttpResponseForbidden, HttpResponse
from django.utils.decorators import method_decorator
from functools import wraps


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return hasattr(request.user, 'customer') or hasattr(request.user, 'business_customer')


class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'employee')


class IsRepairman(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'repairman')


class IsMainManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'main_manager')


class IsSuperuserOrHasRole(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.is_superuser:
            return True
        return (hasattr(request.user, 'customer') or
                hasattr(request.user, 'business_customer') or
                hasattr(request.user, 'employee') or
                hasattr(request.user, 'main_manager'))


# permission decorator
def restrict_access(*user_boolean_fields):
    def decorator(view_class):
        original_initial = view_class.initial

        @wraps(view_class)
        def new_initial(self, request, *args, **kwargs):
            user = request.user
            if not user or not user.is_authenticated:
                raise PermissionDenied("Access denied: user not authenticated.")
            if hasattr(user, 'main_manager'):
                print("hello")
                return original_initial(self, request, *args, **kwargs)
            if hasattr(user, 'employee'):
                employee = request.user.employee
                print("hello 2")
                for field in user_boolean_fields:
                    value = getattr(employee, field, None)
                    print(f"{field}: {value}")

                for field in user_boolean_fields:
                    if not getattr(employee, field, False):
                        raise PermissionDenied(f"Access denied: {field} is not True.")

                return original_initial(self, request, *args, **kwargs)
            if hasattr(user, 'customer'):
                customer = request.user.customer
                print("hello 3")
                for field in user_boolean_fields:
                    value = getattr(customer, field, None)
                    print(f"{field}: {value}")

                for field in user_boolean_fields:
                    if not getattr(customer, field, False):
                        raise PermissionDenied(f"Access denied: {field} is not True.")

                return original_initial(self, request, *args, **kwargs)

        view_class.initial = new_initial
        return view_class

    return decorator
