from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.response import Response

from task_manager.models import PlannedTask
from .permissions import task_management_permissions
from .serializers import TaskManagerDashboardSerializer

@extend_schema(
    tags=["Task Manager"],
    summary="Task Manager Dashboard Stats",
    description="""
    برگرداندن آمار تسک‌ها برای داشبورد.

    - my_tasks : آمار تسک‌های کاربر جاری
    - all_tasks : آمار تمام پرسنل (در صورت داشتن دسترسی)
    - permissions : دسترسی‌های Task Manager
    """,
    responses=TaskManagerDashboardSerializer
)
class TaskManagerDashboardAPIView(generics.GenericAPIView):
    serializer_class = TaskManagerDashboardSerializer

    def get_task_stats(self, queryset):
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

    def get(self, request, *args, **kwargs):
        employee = request.user.employee

        permissions = task_management_permissions(employee.role)

        my_queryset = PlannedTask.objects.filter(
            employee=employee,
            is_deleted=False
        )

        my_tasks = self.get_task_stats(my_queryset)

        all_tasks = None

        if permissions["can_read_task_manger"]:
            all_queryset = PlannedTask.objects.filter(
                is_deleted=False
            )

            all_tasks = self.get_task_stats(all_queryset)

        serializer = self.get_serializer(
            {
                "permissions": permissions,
                "my_tasks": my_tasks,
                "all_tasks": all_tasks,
            }
        )

        return Response(serializer.data)