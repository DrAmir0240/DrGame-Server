from rest_framework.permissions import BasePermission
from hr.services.permission_service import has_permission


class HasEmployeePermission(BasePermission):
    """
    Base class — مستقیم استفاده نکن، از employee_permission() بساز
    """
    required_module: str = None
    required_action: str = None
    required_extra_flag: str = None

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not hasattr(request.user, 'employee'):
            return False

        module     = getattr(view, 'required_module',     self.required_module)
        action     = getattr(view, 'required_action',     self.required_action)
        extra_flag = getattr(view, 'required_extra_flag', self.required_extra_flag)

        return has_permission(request.user.employee, module, action, extra_flag)


def employee_permission(module: str, action: str, extra_flag: str = None):
    """
    Factory — یه permission class آماده برمیگردونه

    مثال:
        permission_classes = [IsAuthenticated, employee_permission('accounting', 'read')]
    """
    return type(
        f'EmployeePerm_{module}_{action}',
        (HasEmployeePermission,),
        {
            'required_module':     module,
            'required_action':     action,
            'required_extra_flag': extra_flag,
        }
    )