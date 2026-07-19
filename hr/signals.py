from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from hr.services.permission_service import invalidate_employee_permissions


@receiver(m2m_changed, sender='hr.Employee_roles')
def invalidate_on_employee_roles_change(sender, instance, **kwargs):
    from hr.models import Employee
    if isinstance(instance, Employee):
        invalidate_employee_permissions(instance.id)


@receiver(m2m_changed, sender='hr.EmployeeRole_permissions')
def invalidate_on_role_permissions_change(sender, instance, action, pk_set, **kwargs):
    """
    وقتی پرمیژن یه رول عوض شد،
    کش تمام کارمندان اون رول invalidate میشه
    """
    if action not in ('post_add', 'post_remove', 'post_clear'):
        return

    from hr.models import EmployeeRole
    if isinstance(instance, EmployeeRole):
        employee_ids = instance.employees.values_list('id', flat=True)
        for emp_id in employee_ids:
            invalidate_employee_permissions(emp_id)