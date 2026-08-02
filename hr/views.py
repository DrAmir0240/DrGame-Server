from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from accounting.models import Invoice, Transaction
from hr.models import (
    Permission,
    EmployeeRole,
    Employee,
    EmployeeFile,
    EmployeeOvertime,
    EmploymentResume,
    EmployeeRequest,
    EmployeeRequestType,
    EmployeeArrival,
)
from hr.permissions import employee_permission
from hr.filters import (
    EmployeeFilter,
    EmployeeOvertimeFilter,
    EmployeeArrivalFilter,
    EmployeeRequestFilter,
)
from hr.serializers import (
    PermissionSerializer,
    EmployeeRoleDetailSerializer,
    EmployeeRoleListSerializer,
    EmployeeListSerializer,
    EmployeeDetailSerializer,
    EmployeeCreateUpdateSerializer,
    EmployeeFileSerializer,
    EmployeeOvertimeSerializer,
    EmploymentResumeSerializer,
    PayrollInvoiceListSerializer,
    PayrollInvoiceDetailSerializer,
    PayrollCreateSerializer,
    PayrollTransactionSerializer,
    EmployeeRequestListSerializer,
    EmployeeRequestDetailSerializer,
    EmployeeRequestCreateSerializer,
    EmployeeRequestStatusSerializer,
    EmployeeRequestTypeSerializer,
    EmployeeArrivalSerializer,
    EmployeeArrivalCreateSerializer,
)
from hr.services.permission_service import get_employee_permissions


class PermissionListView(generics.ListAPIView):
    """List all permissions defined in the system — admin only"""

    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, employee_permission("hr", "read")]
    queryset = Permission.objects.all().order_by("module", "action")


class MyPermissionsView(generics.GenericAPIView):
    """
    The frontend calls this on login
    GET /hr/my-permissions/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if hasattr(self.request.user, "employee"):
            perms = get_employee_permissions(self.request.user.employee)
            return Response(perms)
        return Response({})


class BaseRoleView:
    permission_classes = [IsAuthenticated, employee_permission("hr", "read")]
    queryset = EmployeeRole.objects.filter(is_deleted=False).order_by("-created_at")


class EmployeeRoleListView(BaseRoleView, generics.ListAPIView):
    serializer_class = EmployeeRoleListSerializer


class EmployeeRoleCreateView(generics.CreateAPIView):
    serializer_class = EmployeeRoleDetailSerializer
    permission_classes = [IsAuthenticated, employee_permission("hr", "write")]
    queryset = EmployeeRole.objects.filter(is_deleted=False)


class EmployeeRoleDetailView(BaseRoleView, generics.RetrieveAPIView):
    serializer_class = EmployeeRoleDetailSerializer


class EmployeeRoleUpdateView(generics.UpdateAPIView):
    serializer_class = EmployeeRoleDetailSerializer
    permission_classes = [IsAuthenticated, employee_permission("hr", "write")]
    queryset = EmployeeRole.objects.filter(is_deleted=False)
    http_method_names = ["patch"]


class EmployeeRoleDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, employee_permission("hr", "write")]
    queryset = EmployeeRole.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])


# -----------------------------------------------------------
# Section 1 — Employee files
# -----------------------------------------------------------


@extend_schema(summary='لیست کارمندان')
class EmployeeListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeListSerializer
    filterset_class = EmployeeFilter
    queryset = (
        Employee.objects.filter(is_deleted=False)
        .prefetch_related("roles")
        .order_by("-created_at")
    )


@extend_schema(summary='ایجاد کارمند')
class EmployeeCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeCreateUpdateSerializer
    queryset = Employee.objects.filter(is_deleted=False)


@extend_schema(summary='جزئیات کارمند')
class EmployeeDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeDetailSerializer
    queryset = (
        Employee.objects.filter(is_deleted=False)
        .prefetch_related("roles", "files", "requests", "arrivals", "overtimes")
        .select_related("user__wallet")
    )


@extend_schema(summary='ویرایش کارمند')
class EmployeeUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeCreateUpdateSerializer
    queryset = Employee.objects.filter(is_deleted=False)
    http_method_names = ["patch"]


@extend_schema(summary='حذف کارمند')
class EmployeeDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Employee.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])


# -----------------------------------------------------------
# Employee Files — nested under employee
# -----------------------------------------------------------


@extend_schema(summary='لیست فایل‌های کارمند')
class EmployeeFileListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeFileSerializer

    def get_queryset(self):
        return EmployeeFile.objects.filter(
            employee_id=self.kwargs["employee_id"], is_deleted=False
        ).order_by("-created_at")


@extend_schema(summary='آپلود فایل برای کارمند')
class EmployeeFileCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeFileSerializer
    queryset = EmployeeFile.objects.filter(is_deleted=False)


@extend_schema(summary='حذف فایل کارمند')
class EmployeeFileDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = EmployeeFile.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])


# -----------------------------------------------------------
# Overtime
# -----------------------------------------------------------


@extend_schema(summary='لیست اضافه‌کاری‌ها')
class EmployeeOvertimeListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeOvertimeSerializer
    filterset_class = EmployeeOvertimeFilter
    queryset = EmployeeOvertime.objects.filter(is_deleted=False).order_by("-date")


@extend_schema(summary='ثبت اضافه‌کاری')
class EmployeeOvertimeCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeOvertimeSerializer
    queryset = EmployeeOvertime.objects.filter(is_deleted=False)


@extend_schema(summary='تایید اضافه‌کاری')
class EmployeeOvertimeApproveView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeOvertimeSerializer
    queryset = EmployeeOvertime.objects.filter(is_deleted=False)
    http_method_names = ["patch"]

    def perform_update(self, serializer):
        # approved_by must be the logged-in employee
        serializer.save(is_approved=True, approved_by=self.request.user.employee)


@extend_schema(summary='حذف اضافه‌کاری')
class EmployeeOvertimeDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = EmployeeOvertime.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])


# -----------------------------------------------------------
# Section 2 — Recruitment
# -----------------------------------------------------------


@extend_schema(summary='لیست رزومه‌ها')
class EmploymentResumeListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmploymentResumeSerializer
    queryset = EmploymentResume.objects.filter(is_deleted=False).order_by("-created_at")


@extend_schema(summary='جزئیات رزومه')
class EmploymentResumeDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmploymentResumeSerializer
    queryset = EmploymentResume.objects.filter(is_deleted=False)


@extend_schema(summary='ثبت رزومه')
class EmploymentResumeCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmploymentResumeSerializer
    queryset = EmploymentResume.objects.filter(is_deleted=False)


@extend_schema(summary='حذف رزومه')
class EmploymentResumeDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = EmploymentResume.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])


# -----------------------------------------------------------
# Section 3 — Payroll
# -----------------------------------------------------------


@extend_schema(summary='لیست فیش‌های حقوقی')
class PayrollListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PayrollInvoiceListSerializer
    queryset = (
        Invoice.objects.filter(is_payroll=True, is_deleted=False)
        .select_related("account_side")
        .order_by("-created_at")
    )


@extend_schema(summary='جزئیات فیش حقوقی')
class PayrollDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PayrollInvoiceDetailSerializer
    queryset = Invoice.objects.filter(is_payroll=True, is_deleted=False)


@extend_schema(summary='صدور فیش حقوقی')
class PayrollCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PayrollCreateSerializer

    def perform_create(self, serializer):
        serializer.save()


@extend_schema(summary='لیست پرداخت‌های یک فیش')
class PayrollTransactionListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PayrollTransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(
            invoice_id=self.kwargs["invoice_id"], is_deleted=False
        ).order_by("-created_at")


# -----------------------------------------------------------
# Section 4 — Requests
# -----------------------------------------------------------


@extend_schema(summary='لیست درخواست‌ها')
class EmployeeRequestListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeRequestListSerializer
    filterset_class = EmployeeRequestFilter
    queryset = EmployeeRequest.objects.filter(is_deleted=False).order_by("-created_at")


@extend_schema(summary='جزئیات درخواست')
class EmployeeRequestDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeRequestDetailSerializer
    queryset = EmployeeRequest.objects.filter(is_deleted=False)


@extend_schema(summary='ثبت درخواست')
class EmployeeRequestCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeRequestCreateSerializer
    queryset = EmployeeRequest.objects.filter(is_deleted=False)


@extend_schema(summary='تغییر وضعیت درخواست')
class EmployeeRequestStatusUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeRequestStatusSerializer
    queryset = EmployeeRequest.objects.filter(is_deleted=False)
    http_method_names = ["patch"]


@extend_schema(summary='حذف درخواست')
class EmployeeRequestDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = EmployeeRequest.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])


@extend_schema(summary='لیست انواع درخواست')
class EmployeeRequestTypeListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeRequestTypeSerializer
    queryset = EmployeeRequestType.objects.filter(is_deleted=False)


@extend_schema(summary='ایجاد نوع درخواست')
class EmployeeRequestTypeCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeRequestTypeSerializer
    queryset = EmployeeRequestType.objects.filter(is_deleted=False)


@extend_schema(summary='حذف نوع درخواست')
class EmployeeRequestTypeDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = EmployeeRequestType.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])


# -----------------------------------------------------------
# Section 5 — Attendance
# -----------------------------------------------------------


@extend_schema(summary='لیست حضور و غیاب')
class EmployeeArrivalListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeArrivalSerializer
    filterset_class = EmployeeArrivalFilter
    queryset = EmployeeArrival.objects.filter(is_deleted=False).order_by("-check_in")


@extend_schema(summary='ثبت حضور و غیاب')
class EmployeeArrivalCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeArrivalCreateSerializer
    queryset = EmployeeArrival.objects.filter(is_deleted=False)


@extend_schema(summary='ویرایش حضور و غیاب')
class EmployeeArrivalUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeArrivalCreateSerializer
    queryset = EmployeeArrival.objects.filter(is_deleted=False)
    http_method_names = ["patch"]


@extend_schema(summary='حذف رکورد حضور و غیاب')
class EmployeeArrivalDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = EmployeeArrival.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])
