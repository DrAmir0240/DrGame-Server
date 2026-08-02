from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from task_manager.filters import PlannedTaskFilter, DailyTaskFilter
from task_manager.helpers import get_task_stats, get_employee
from task_manager.mixins import _PermissionFilterMixin, _TaskActionMixin
from task_manager.models import PlannedTask, DailyTask
from task_manager.permissions import (
    task_management_permissions,
    has_read_permission,
    has_write_permission,
)
from task_manager.serializers import (
    TaskManagerDashboardSerializer,
    TaskChoicesSerializer,
    PlannedTaskListSerializer,
    PlannedTaskDetailSerializer,
    PersonalTaskCreateSerializer,
    OrganizeTaskCreateSerializer,
    PendingApprovalSerializer,
    ApproveRejectSerializer,
    TaskSearchSerializer,
    DailyTaskListSerializer,
    PersonalDailyTaskSerializer,
    OrganizeDailyTaskSerializer,
    DailyTaskSearchSerializer,
)


# ─── 1. stats and choices ────────────────────────────────────────────────────────────────
@extend_schema(
    summary="Task Manager Dashboard Stats",
    description="""
    Returns task statistics for the dashboard.

    - my_tasks : stats of the current user's tasks
    - all_tasks : stats of all staff (if the user has access)
    - permissions : Task Manager permissions
    """,
    responses=TaskManagerDashboardSerializer,
)
class PlannedTaskManagerDashboardAPIView(generics.GenericAPIView):
    serializer_class = TaskManagerDashboardSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        employee = get_employee(self.request)

        permissions = task_management_permissions(employee.role)

        my_queryset = PlannedTask.objects.filter(employee=employee, is_deleted=False)

        my_tasks = get_task_stats(my_queryset)

        all_tasks = None

        if has_read_permission(employee):
            all_queryset = PlannedTask.objects.filter(is_deleted=False)

            all_tasks = get_task_stats(all_queryset)

        serializer = self.get_serializer(
            {
                "permissions": permissions,
                "my_tasks": my_tasks,
                "all_tasks": all_tasks,
            }
        )

        return Response(serializer.data)


@extend_schema(
    summary="دریافت انتخاب‌ها و مقادیر ثابت",
    description=(
        "Returns the list of employees (id + name), statuses, priorities and task types. "
        "Used to fill the dropdowns of the task create/edit form."
    ),
    responses={200: TaskChoicesSerializer},
)
class TaskChoicesView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskChoicesSerializer

    def get_object(self):
        return {}


# ─── 2. search ────────────────────────────────────────────────────────────────
@extend_schema(
    summary="جستجو در تسک‌ها",
    description=(
        "Searches by title or description. "
        "Users with can_read_task_manager access see all tasks; "
        "others only see their own."
    ),
    parameters=[
        OpenApiParameter(
            "q", OpenApiTypes.STR, description="search text", required=True
        )
    ],
    responses={200: TaskSearchSerializer(many=True)},
)
class PlannedTaskSearchView(_PermissionFilterMixin, generics.ListAPIView):
    serializer_class = TaskSearchSerializer
    filter_backends = [SearchFilter]
    search_fields = ["title", "description"]

    def get_queryset(self):
        qs = super().get_queryset()
        employee = get_employee(self.request)
        if has_read_permission(employee):
            qs = qs.filter(Q(employee=employee) | Q(type="Organize"))
        else:
            qs = qs.filter(employee=employee)
        q = self.request.query_params.get("q", "").strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        return qs


# ─── 3. list ──────────────────────────────────────────────────────────────────
@extend_schema(
    summary="لیست تسک‌ها با فیلتر",
    description=(
        "Returns the list of tasks. Can be filtered by status, priority, type and "
        "employee_id. "
        "Users with can_read_task_manager access see all tasks; "
        "others only see their own."
    ),
    parameters=[
        OpenApiParameter(
            "status",
            OpenApiTypes.STR,
            description="status: planed | in_progress | done",
        ),
        OpenApiParameter(
            "priority",
            OpenApiTypes.STR,
            description="priority: immediate | high | medium | low | very_low",
        ),
        OpenApiParameter(
            "type", OpenApiTypes.STR, description="type: Personal | Organize"
        ),
        OpenApiParameter(
            "employee_id", OpenApiTypes.INT, description="filter by employee id"
        ),
    ],
    responses={200: PlannedTaskListSerializer(many=True)},
)
class PlannedTaskListView(_PermissionFilterMixin, generics.ListAPIView):
    serializer_class = PlannedTaskListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PlannedTaskFilter

    def get_queryset(self):
        employee = get_employee(self.request)

        qs = PlannedTask.objects.filter(is_deleted=False)

        if has_read_permission(employee):
            return qs.filter(Q(employee=employee) | Q(type="Organize"))
        return qs.filter(employee=employee)


# ─── 4. personal ──────────────────────────────────────────────────────────────
@extend_schema(
    summary="جزئیات، ویرایش و حذف تسک شخصی",
    description=(
        "The current user only has access to their own personal tasks. "
        "DELETE performs a soft-delete, not a real deletion."
    ),
    responses={200: PersonalTaskCreateSerializer},
)
class PersonalPlannedTaskRUDView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PersonalTaskCreateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "delete"]

    def get_queryset(self):
        return PlannedTask.objects.filter(
            employee=get_employee(self.request),
            type="Personal",
            is_deleted=False,
        )

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])


@extend_schema(
    summary="ایجاد تسک شخصی",
    description=(
        "Creates a personal task for the current user. "
        "The employee and type fields are set automatically."
    ),
    request=PersonalTaskCreateSerializer,
    responses={201: PersonalTaskCreateSerializer},
)
class PersonalPlannedTaskCreateView(generics.CreateAPIView):
    serializer_class = PersonalTaskCreateSerializer
    permission_classes = [IsAuthenticated]


# ─── 5. organize — pending approval ──────────────────────────────────────────
@extend_schema(
    summary="لیست تسک‌های منتظر تأیید",
    description=(
        "Returns organizational tasks that have a reward, whose status is done "
        "and which have not yet been approved."
    ),
    responses={200: PendingApprovalSerializer(many=True)},
)
class PendingApprovalPlannedTaskListView(generics.ListAPIView):
    serializer_class = PendingApprovalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            PlannedTask.objects.filter(
                type="Organize",
                has_reward=True,
                status="done",
                approved=False,
                is_deleted=False,
            )
            .select_related("employee")
            .order_by("-created_at")
        )


@extend_schema(
    summary="تأیید تسک",
    description="Approves the specified organizational task (approved=True).",
    request=ApproveRejectSerializer,
    responses={200: PendingApprovalSerializer},
)
class ApprovePlannedTaskView(_TaskActionMixin):
    def _action(self, task: PlannedTask) -> None:
        task.approved = True
        task.save()


@extend_schema(
    summary="رد تسک",
    description=(
        "Rejects the organizational task. "
        "The status returns to in_progress so the employee can try again."
    ),
    request=ApproveRejectSerializer,
    responses={200: PendingApprovalSerializer},
)
class RejectPlannedTaskView(_TaskActionMixin):
    def _action(self, task: PlannedTask) -> None:
        task.status = "in_progress"
        task.save()


# ─── 6. organize — CRUD ───────────────────────────────────────────────────────
@extend_schema(
    summary="جزئیات، ویرایش و حذف تسک سازمانی",
    description=(
        "Get details, edit (PATCH) or soft-delete an organizational task. "
        "Requires can_write_task_manager access to edit and delete."
    ),
    responses={200: PlannedTaskDetailSerializer},
)
class OrganizePlannedTaskRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PlannedTaskDetailSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "delete"]

    def get_queryset(self):
        return PlannedTask.objects.filter(
            type="Organize", is_deleted=False
        ).select_related("employee")

    def perform_update(self, serializer):
        employee = get_employee(self.request)
        if not has_write_permission(employee):
            raise PermissionDenied("You don't have permission.")
        serializer.save()

    def perform_destroy(self, instance):
        employee = get_employee(self.request)
        if not has_write_permission(employee):
            raise PermissionDenied("You don't have permission.")
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])


@extend_schema(
    summary="ایجاد تسک سازمانی",
    description=(
        "Creates a new organizational task for the specified employee. "
        "Requires can_write_task_manager access."
    ),
    request=OrganizeTaskCreateSerializer,
    responses={201: OrganizeTaskCreateSerializer},
)
class OrganizePlannedTaskCreateView(generics.CreateAPIView):
    serializer_class = OrganizeTaskCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        employee = get_employee(self.request)
        if not has_write_permission(employee):
            raise PermissionDenied("You don't have permission.")
        serializer.save()


@extend_schema(
    summary="جستجو در تسک‌ها",
    description=(
        "Searches by title or description. "
        "Users with can_read_task_manager access see all tasks; "
        "others only see their own."
    ),
    parameters=[
        OpenApiParameter(
            "q", OpenApiTypes.STR, description="search text", required=True
        )
    ],
    responses={200: DailyTaskListSerializer(many=True)},
)
class DailyTaskSearchAPIView(generics.ListAPIView):
    serializer_class = DailyTaskSearchSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["title", "description"]

    def get_queryset(self):
        qs = DailyTask.objects.filter(is_deleted=False)
        employee = get_employee(self.request)
        if has_read_permission(employee):
            qs = qs.filter(Q(employees=employee) | Q(type="Organize"))
        else:
            qs = qs.filter(employees=employee)
        q = self.request.query_params.get("q", "").strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        return qs.distinct()


@extend_schema(
    summary="دریافت لیست تسک‌ها",
    description=(
        "Returns the list of tasks. Users with "
        "can_read_task_manager access can see all tasks, and other users "
        "will only see their own."
    ),
    responses={200: DailyTaskListSerializer(many=True)},
)
class DailyTaskListAPIView(generics.ListAPIView):
    serializer_class = DailyTaskListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DailyTaskFilter

    def get_queryset(self):
        employee = get_employee(self.request)

        queryset = DailyTask.objects.filter(is_deleted=False).order_by("-created_at")

        if has_read_permission(employee):
            return queryset

        return queryset.filter(employees=employee)


@extend_schema(
    summary="ایجاد تسک شخصی",
    description=("Creates a personal task for the current user."),
    request=PersonalDailyTaskSerializer,
    responses={201: PersonalDailyTaskSerializer},
)
class PersonalDailyTaskCreateAPIView(generics.CreateAPIView):
    serializer_class = PersonalDailyTaskSerializer
    permission_classes = [IsAuthenticated]


@extend_schema(
    summary="دریافت، ویرایش و حذف تسک",
    description=("Details, edit and delete a task."),
)
class PersonalDailyTaskRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PersonalDailyTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        employee = get_employee(self.request)
        return DailyTask.objects.filter(
            employees=employee,
            type="Personal",
            is_deleted=False,
        )

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])


@extend_schema(
    summary="ایجاد تسک سازمانی",
    description=(
        "Creates a new organizational task for the specified employee. "
        "Requires can_write_task_manager access."
    ),
    request=OrganizeTaskCreateSerializer,
    responses={201: OrganizeTaskCreateSerializer},
)
class OrganizeDailyTaskCreateAPIView(generics.CreateAPIView):
    serializer_class = OrganizeDailyTaskSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        employee = get_employee(self.request)

        if not has_write_permission(employee):
            raise PermissionDenied("You don't have permission.")

        serializer.save()


@extend_schema(
    summary="مدیریت تسک سازمانی",
    description=(
        "Get, edit and delete organizational tasks. Requires can_write_task_manager access."
    ),
)
class OrganizeDailyTaskRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrganizeDailyTaskSerializer

    def get_queryset(self):
        return DailyTask.objects.filter(
            is_deleted=False,
            type="Organize",
        )

    def perform_update(self, serializer):
        employee = get_employee(self.request)

        if not has_write_permission(employee):
            raise PermissionDenied("You don't have permission.")

        serializer.save()

    def perform_destroy(self, instance):
        employee = get_employee(self.request)

        if not has_write_permission(employee):
            raise PermissionDenied("You don't have permission.")

        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])
