from django.utils import timezone

from hr.models import Employee


def get_employee(request) -> Employee:
    return request.user.employee


def get_task_stats(queryset):
    today = timezone.now().date()

    return {
        "not_started": queryset.filter(
            status="planed"
        ).count(),

        "in_progress": queryset.filter(
            status="in_progress"
        ).count(),

        "done": queryset.filter(
            status="done"
        ).count(),

        "expired": queryset.filter(
            deadline__lt=today
        ).exclude(
            status="done"
        ).count(),
    }


