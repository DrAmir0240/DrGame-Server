from hr.models import EmployeeRole


def task_management_permissions(role: EmployeeRole):
    can_read_task_manger = False
    can_write_task_manger = False
    if role.can_read_task_manager:
        can_read_task_manger = True
    if role.can_write_task_manager:
        can_write_task_manger = True

    return {"can_read_task_manger": can_read_task_manger, "can_write_task_manger": can_write_task_manger}
