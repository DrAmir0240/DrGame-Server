from django.core.cache import cache
from hr.models import Permission


CACHE_TTL = 60 * 15  # 15 دقیقه


def _cache_key(employee_id: int) -> str:
    return f'emp_perms_{employee_id}'


def get_employee_permissions(employee) -> dict:
    """
    خروجی:
    {
        "accounting": {"read": True, "write": False},
        "inventory":  {"read": True, "all_inventory": True},
        "messenger":  {"access": True, "start_chat": False},
    }
    """
    key = _cache_key(employee.id)
    cached = cache.get(key)
    if cached is not None:
        return cached

    perms = (
        Permission.objects
        .filter(roles__employees=employee, roles__is_deleted=False)
        .values_list('module', 'action', 'extra_flag')
        .distinct()
    )

    result: dict = {}
    for module, action, extra_flag in perms:
        if module not in result:
            result[module] = {}
        if extra_flag:
            result[module][extra_flag] = True
        else:
            result[module][action] = True

    cache.set(key, result, CACHE_TTL)
    return result


def has_permission(
    employee,
    module: str,
    action: str,
    extra_flag: str = None
) -> bool:
    perms = get_employee_permissions(employee)
    module_perms = perms.get(module, {})
    key = extra_flag if extra_flag else action
    return module_perms.get(key, False)


def invalidate_employee_permissions(employee_id: int) -> None:
    cache.delete(_cache_key(employee_id))