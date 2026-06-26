from hr.models import EmployeeRole, Employee


def task_management_permissions(role: EmployeeRole) -> dict:
    can_read_task_manger = False
    can_write_task_manger = False
    if role.can_read_task_manager:
        can_read_task_manger = True
    if role.can_write_task_manager:
        can_write_task_manger = True

    return {"can_read_task_manger": can_read_task_manger, "can_write_task_manger": can_write_task_manger}


def has_write_permission(employee: Employee) -> bool:
    return employee.role and employee.role.can_write_task_manager


def has_read_permission(employee: Employee) -> bool:
    return employee.role and employee.role.can_read_task_manager
