from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from task_manager.filters import PlannedTaskFilter
from task_manager.helpers import get_task_stats, get_employee
from task_manager.models import PlannedTask
from task_manager.permissions import task_management_permissions, has_read_permission
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
)


@extend_schema(
    tags=["Task Management"],
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

    def get(self, request, *args, **kwargs):
        employee = get_employee(self.request)

        permissions = task_management_permissions(employee.role)

        my_queryset = PlannedTask.objects.filter(
            employee=employee,
            is_deleted=False
        )

        my_tasks = get_task_stats(my_queryset)

        all_tasks = None

        if has_read_permission(employee):
            all_queryset = PlannedTask.objects.filter(
                is_deleted=False
            )

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
    tags=["Task Management"],
    summary="دریافت انتخاب‌ها و مقادیر ثابت",
    description=(
            "لیست کارمندان (id + نام)، وضعیت‌ها، اولویت‌ها و انواع تسک را "
            "برمی‌گرداند. برای پر کردن dropdown های فرم ایجاد/ویرایش تسک استفاده می‌شود."
    ),
    responses={200: TaskChoicesSerializer},
)
class TaskChoicesView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer = TaskChoicesSerializer()

    def get(self, request):
        return Response(self.serializer.data)


@extend_schema(
    tags=["Task Management"],
    summary="جستجو در تسک‌ها",
    description=(
            "جستجو بر اساس عنوان یا توضیحات. "
            "کاربران با دسترسی can_read_task_manager همه تسک‌ها را می‌بینند؛ "
            "سایرین فقط تسک‌های خودشان را."
    ),
    parameters=[
        OpenApiParameter("q", OpenApiTypes.STR, description="متن جستجو", required=True),
    ],
    responses={200: TaskSearchSerializer(many=True)},
)
class TaskSearchView(generics.ListAPIView):
    serializer_class = TaskSearchSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["title", "description"]

    def get_queryset(self):
        employee = get_employee(self.request)
        qs = PlannedTask.objects.filter(is_deleted=False)
        if not has_read_permission(employee):
            qs = qs.filter(employee=employee)
        q = self.request.query_params.get("q", "")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        return qs.order_by("-created_at")


@extend_schema(
    tags=["Task Management"],
    summary="لیست تسک‌ها با فیلتر",
    description=(
            "لیست تسک‌ها را برمی‌گرداند. می‌توان بر اساس status، priority، type و "
            "employee_id فیلتر کرد. "
            "کاربران با دسترسی can_read_task_manager همه تسک‌ها را می‌بینند؛ "
            "سایرین فقط تسک‌های خودشان را."
    ),
    parameters=[
        OpenApiParameter("status", OpenApiTypes.STR, description="وضعیت: planed | in_progress | done"),
        OpenApiParameter("priority", OpenApiTypes.STR,
                         description="اولویت: immediate | high | medium | low | very_low"),
        OpenApiParameter("type", OpenApiTypes.STR, description="نوع: Personal | Organize"),
        OpenApiParameter("employee_id", OpenApiTypes.INT, description="فیلتر بر اساس شناسه کارمند"),
    ],
    responses={200: PlannedTaskListSerializer(many=True)},
)
class TaskListView(generics.ListAPIView):
    serializer_class = PlannedTaskListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = PlannedTaskFilter

    def get_queryset(self):
        employee = get_employee(self.request)
        qs = PlannedTask.objects.filter(is_deleted=False).select_related("employee")
        if not has_read_permission(employee):
            qs = qs.filter(employee=employee)
        return qs.order_by("-created_at")


@extend_schema(
    tags=["Task Management"],
    summary="جزئیات، ویرایش و حذف تسک شخصی",
    description=(
            "کاربر جاری فقط به تسک‌های شخصی خودش دسترسی دارد. "
            "DELETE باعث soft-delete (is_deleted=True) می‌شود نه حذف واقعی."
    ),
    responses={200: PersonalTaskCreateSerializer},
)
class PersonalTaskRUDView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PersonalTaskCreateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "delete"]

    def get_queryset(self):
        employee = get_employee(self.request)
        return PlannedTask.objects.filter(
            employee=employee,
            type="Personal",
            is_deleted=False,
        )

    def get_object(self):
        # تسک شخصی فقط یک رکورد دارد؛ pk از URL می‌آید
        return generics.get_object_or_404(self.get_queryset(), pk=self.kwargs.get("pk"))

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


@extend_schema(
    tags=["Task Management"],
    summary="ایجاد تسک شخصی",
    description=(
            "تسک شخصی برای کاربر جاری ایجاد می‌کند. "
            "فیلد employee و type به‌صورت خودکار تنظیم می‌شوند."
    ),
    request=PersonalTaskCreateSerializer,
    responses={201: PersonalTaskCreateSerializer},
)
class PersonalTaskCreateView(generics.CreateAPIView):
    serializer_class = PersonalTaskCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


@extend_schema(
    tags=["Task Management"],
    summary="لیست تسک‌های منتظر تأیید",
    description=(
            "تسک‌های سازمانی که پاداش دارند (has_reward=True)، "
            "وضعیتشان «انجام شده» (done) است و هنوز تأیید نشده‌اند (approved=False) "
            "را برمی‌گرداند."
    ),
    responses={200: PendingApprovalSerializer(many=True)},
)
class PendingApprovalListView(generics.ListAPIView):
    serializer_class = PendingApprovalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PlannedTask.objects.filter(
            type="Organize",
            has_reward=True,
            status="done",
            approved=False,
            is_deleted=False,
        ).select_related("employee").order_by("-created_at")


@extend_schema(
    tags=["Task Management"],
    summary="تأیید تسک",
    description="تسک سازمانی مورد نظر را تأیید می‌کند (approved=True).",
    request=ApproveRejectSerializer,
    responses={200: PendingApprovalSerializer},
)
class ApproveTaskView(generics.GenericAPIView):
    serializer_class = ApproveRejectSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        task = generics.get_object_or_404(
            PlannedTask,
            pk=pk,
            type="Organize",
            has_reward=True,
            status="done",
            approva=False,
            is_deleted=False,
        )
        task.approved = True
        task.save()
        return Response(PendingApprovalSerializer(task).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Task Management"],
    summary="رد تسک",
    description=(
            "تسک سازمانی را رد می‌کند. "
            "وضعیت به in_progress برمی‌گردد تا کارمند بتواند دوباره تلاش کند."
    ),
    request=ApproveRejectSerializer,
    responses={200: PendingApprovalSerializer},
)
class RejectTaskView(generics.GenericAPIView):
    serializer_class = ApproveRejectSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        task = generics.get_object_or_404(
            PlannedTask,
            pk=pk,
            type="Organize",
            has_reward=True,
            status="done",
            approved=False,
            is_deleted=False,
        )
        task.status = "in_progress"
        task.save()
        return Response(PendingApprovalSerializer(task).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Task Management"],
    summary="جزئیات، ویرایش و حذف تسک سازمانی",
    description=(
            "دریافت جزئیات، ویرایش (PATCH) یا soft-delete تسک سازمانی. "
            "نیازمند دسترسی can_write_task_manager برای ویرایش و حذف."
    ),
    responses={200: PlannedTaskDetailSerializer},
)
class OrganizeTaskRUDView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PlannedTaskDetailSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "delete"]

    def get_queryset(self):
        return PlannedTask.objects.filter(type="Organize", is_deleted=False).select_related("employee")

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


@extend_schema(
    tags=["Task Management"],
    summary="ایجاد تسک سازمانی",
    description=(
            "تسک سازمانی جدید برای کارمند مشخص‌شده ایجاد می‌کند. "
            "نیازمند دسترسی can_write_task_manager."
    ),
    request=OrganizeTaskCreateSerializer,
    responses={201: OrganizeTaskCreateSerializer},
)
class OrganizeTaskCreateView(generics.CreateAPIView):
    serializer_class = OrganizeTaskCreateSerializer
    permission_classes = [IsAuthenticated]
