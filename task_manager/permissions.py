from hr.models import EmployeeRole, Employee


def task_management_permissions(role: EmployeeRole) -> dict:
    return {
        "can_read_task_manager": bool(role.can_read_task_manager),
        "can_write_task_manager": bool(role.can_write_task_manager),
    }


def has_write_permission(employee: Employee) -> bool:
    return employee.role and employee.role.can_write_task_manager


def has_read_permission(employee: Employee) -> bool:
    return employee.role and employee.role.can_read_task_manager
