from django.core.management.base import BaseCommand
from hr.models import Permission

PERMISSIONS = [
    # module,           action,   extra_flag
    ('dashboard', 'access', None),
    ('task_manager', 'read', None),
    ('task_manager', 'write', None),
    ('accounting', 'read', None),
    ('accounting', 'write', None),
    ('inventory', 'read', None),
    ('inventory', 'write', None),
    ('inventory', 'access', 'all_inventory'),
    ('orders', 'read', None),
    ('orders', 'write', None),
    ('account_orders', 'read', None),
    ('account_orders', 'write', None),
    ('account_orders', 'access', 'all_accounts'),
    ('account_orders', 'access', 'is_account_employee'),
    ('repairs', 'read', None),
    ('repairs', 'write', None),
    ('hr', 'read', None),
    ('hr', 'write', None),
    ('site', 'read', None),
    ('site', 'write', None),
    ('branch', 'read', None),
    ('branch', 'write', None),
    ('docs', 'read', None),
    ('docs', 'write', None),
    ('settings', 'access', None),
    ('messenger', 'access', None),
    ('messenger', 'access', 'start_chat'),
]


class Command(BaseCommand):
    help = 'Seed all system permissions'

    def handle(self, *args, **kwargs):
        created = 0
        for module, action, extra_flag in PERMISSIONS:
            _, is_new = Permission.objects.get_or_create(
                module=module,
                action=action,
                extra_flag=extra_flag,
            )
            if is_new:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(f'{created} permission(s) created, {len(PERMISSIONS) - created} already existed.')
        )
