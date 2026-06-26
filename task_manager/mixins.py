from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from task_manager.helpers import get_employee
from task_manager.models import PlannedTask
from task_manager.permissions import has_read_permission
from task_manager.serializers import ApproveRejectSerializer, PendingApprovalSerializer


class _PermissionFilterMixin(generics.GenericAPIView):
    """فیلتر queryset بر اساس پرمیژن کاربر جاری."""

    def get_queryset(self):
        employee = get_employee(self.request)
        qs = PlannedTask.objects.filter(is_deleted=False).select_related("employee")
        if not has_read_permission(employee):
            qs = qs.filter(employee=employee)
        return qs.order_by("-created_at")





class _TaskActionMixin(generics.GenericAPIView):
    """بیس مشترک برای Approve و Reject — منطق fetch تسک را مرکزی می‌کند."""

    permission_classes = [IsAuthenticated]
    serializer_class = ApproveRejectSerializer

    _pending_filter = dict(
        type="Organize",
        has_reward=True,
        status="done",
        approved=False,
        is_deleted=False,
    )

    def _get_pending_task(self, pk: int) -> PlannedTask:
        return generics.get_object_or_404(PlannedTask, pk=pk, **self._pending_filter)

    def _action(self, task: PlannedTask) -> None:
        raise NotImplementedError

    def post(self, request, pk):
        task = self._get_pending_task(pk)
        self._action(task)
        return Response(PendingApprovalSerializer(task).data, status=status.HTTP_200_OK)
