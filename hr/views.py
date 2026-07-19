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


@extend_schema(tags=['HR — Permissions'])
class PermissionListView(generics.ListAPIView):
    """لیست تمام پرمیژن‌های تعریف‌شده در سیستم — فقط مدیر"""
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, employee_permission('hr', 'read')]
    queryset = Permission.objects.all().order_by('module', 'action')


@extend_schema(tags=['HR — Permissions'])
class MyPermissionsView(generics.GenericAPIView):
    """
    فرانت موقع لاگین این رو صدا میزنه
    GET /hr/my-permissions/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if hasattr(self.request.user, 'employee'):
            perms = get_employee_permissions(self.request.user.employee)
            return Response(perms)
        return Response({})


class BaseRoleView:
    permission_classes = [IsAuthenticated, employee_permission('hr', 'read')]
    queryset = EmployeeRole.objects.filter(is_deleted=False).order_by('-created_at')


@extend_schema(tags=['HR — Roles'])
class EmployeeRoleListView(BaseRoleView, generics.ListAPIView):
    serializer_class = EmployeeRoleListSerializer


@extend_schema(tags=['HR — Roles'])
class EmployeeRoleCreateView(generics.CreateAPIView):
    serializer_class = EmployeeRoleDetailSerializer
    permission_classes = [IsAuthenticated, employee_permission('hr', 'write')]
    queryset = EmployeeRole.objects.filter(is_deleted=False)


@extend_schema(tags=['HR — Roles'])
class EmployeeRoleDetailView(BaseRoleView, generics.RetrieveAPIView):
    serializer_class = EmployeeRoleDetailSerializer


@extend_schema(tags=['HR — Roles'])
class EmployeeRoleUpdateView(generics.UpdateAPIView):
    serializer_class = EmployeeRoleDetailSerializer
    permission_classes = [IsAuthenticated, employee_permission('hr', 'write')]
    queryset = EmployeeRole.objects.filter(is_deleted=False)
    http_method_names = ['patch']


@extend_schema(tags=['HR — Roles'])
class EmployeeRoleDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, employee_permission('hr', 'write')]
    queryset = EmployeeRole.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


# -----------------------------------------------------------
# بخش ۱ — پرونده کارمندان
# -----------------------------------------------------------

@extend_schema(tags=['HR — Employees'], summary='لیست کارمندان')
class EmployeeListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeListSerializer
    filterset_class = EmployeeFilter
    queryset = Employee.objects.filter(is_deleted=False).prefetch_related('roles').order_by('-created_at')


@extend_schema(tags=['HR — Employees'], summary='ایجاد کارمند')
class EmployeeCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeCreateUpdateSerializer
    queryset = Employee.objects.filter(is_deleted=False)


@extend_schema(tags=['HR — Employees'], summary='جزئیات کارمند')
class EmployeeDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeDetailSerializer
    queryset = Employee.objects.filter(is_deleted=False).prefetch_related(
        'roles', 'files', 'requests', 'arrivals', 'overtimes'
    ).select_related('user__wallet')


@extend_schema(tags=['HR — Employees'], summary='ویرایش کارمند')
class EmployeeUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeCreateUpdateSerializer
    queryset = Employee.objects.filter(is_deleted=False)
    http_method_names = ['patch']


@extend_schema(tags=['HR — Employees'], summary='حذف کارمند')
class EmployeeDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Employee.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


# -----------------------------------------------------------
# Employee Files — nested under employee
# -----------------------------------------------------------

@extend_schema(tags=['HR — Employee Files'], summary='لیست فایل‌های کارمند')
class EmployeeFileListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeFileSerializer

    def get_queryset(self):
        return EmployeeFile.objects.filter(
            employee_id=self.kwargs['employee_id'],
            is_deleted=False
        ).order_by('-created_at')


@extend_schema(tags=['HR — Employee Files'], summary='آپلود فایل برای کارمند')
class EmployeeFileCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeFileSerializer
    queryset = EmployeeFile.objects.filter(is_deleted=False)


@extend_schema(tags=['HR — Employee Files'], summary='حذف فایل کارمند')
class EmployeeFileDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = EmployeeFile.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


# -----------------------------------------------------------
# Overtime
# -----------------------------------------------------------

@extend_schema(tags=['HR — Overtime'], summary='لیست اضافه‌کاری‌ها')
class EmployeeOvertimeListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeOvertimeSerializer
    filterset_class = EmployeeOvertimeFilter
    queryset = EmployeeOvertime.objects.filter(is_deleted=False).order_by('-date')


@extend_schema(tags=['HR — Overtime'], summary='ثبت اضافه‌کاری')
class EmployeeOvertimeCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeOvertimeSerializer
    queryset = EmployeeOvertime.objects.filter(is_deleted=False)


@extend_schema(tags=['HR — Overtime'], summary='تایید اضافه‌کاری')
class EmployeeOvertimeApproveView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeOvertimeSerializer
    queryset = EmployeeOvertime.objects.filter(is_deleted=False)
    http_method_names = ['patch']

    def perform_update(self, serializer):
        # approved_by باید کارمند لاگین‌کرده باشه
        serializer.save(
            is_approved=True,
            approved_by=self.request.user.employee
        )


@extend_schema(tags=['HR — Overtime'], summary='حذف اضافه‌کاری')
class EmployeeOvertimeDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = EmployeeOvertime.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


# -----------------------------------------------------------
# بخش ۲ — استخدام
# -----------------------------------------------------------

@extend_schema(tags=['HR — Recruitment'], summary='لیست رزومه‌ها')
class EmploymentResumeListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmploymentResumeSerializer
    queryset = EmploymentResume.objects.filter(is_deleted=False).order_by('-created_at')


@extend_schema(tags=['HR — Recruitment'], summary='جزئیات رزومه')
class EmploymentResumeDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmploymentResumeSerializer
    queryset = EmploymentResume.objects.filter(is_deleted=False)


@extend_schema(tags=['HR — Recruitment'], summary='ثبت رزومه')
class EmploymentResumeCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmploymentResumeSerializer
    queryset = EmploymentResume.objects.filter(is_deleted=False)


@extend_schema(tags=['HR — Recruitment'], summary='حذف رزومه')
class EmploymentResumeDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = EmploymentResume.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


# -----------------------------------------------------------
# بخش ۳ — فیش حقوقی
# -----------------------------------------------------------

@extend_schema(tags=['HR — Payroll'], summary='لیست فیش‌های حقوقی')
class PayrollListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PayrollInvoiceListSerializer
    queryset = Invoice.objects.filter(
        is_payroll=True, is_deleted=False
    ).select_related('account_side').order_by('-created_at')


@extend_schema(tags=['HR — Payroll'], summary='جزئیات فیش حقوقی')
class PayrollDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PayrollInvoiceDetailSerializer
    queryset = Invoice.objects.filter(is_payroll=True, is_deleted=False)


@extend_schema(tags=['HR — Payroll'], summary='صدور فیش حقوقی')
class PayrollCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PayrollCreateSerializer

    def perform_create(self, serializer):
        serializer.save()


@extend_schema(tags=['HR — Payroll'], summary='لیست پرداخت‌های یک فیش')
class PayrollTransactionListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PayrollTransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(
            invoice_id=self.kwargs['invoice_id'],
            is_deleted=False
        ).order_by('-created_at')


# -----------------------------------------------------------
# بخش ۴ — درخواست‌ها
# -----------------------------------------------------------

@extend_schema(tags=['HR — Requests'], summary='لیست درخواست‌ها')
class EmployeeRequestListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeRequestListSerializer
    filterset_class = EmployeeRequestFilter
    queryset = EmployeeRequest.objects.filter(is_deleted=False).order_by('-created_at')


@extend_schema(tags=['HR — Requests'], summary='جزئیات درخواست')
class EmployeeRequestDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeRequestDetailSerializer
    queryset = EmployeeRequest.objects.filter(is_deleted=False)


@extend_schema(tags=['HR — Requests'], summary='ثبت درخواست')
class EmployeeRequestCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeRequestCreateSerializer
    queryset = EmployeeRequest.objects.filter(is_deleted=False)


@extend_schema(tags=['HR — Requests'], summary='تغییر وضعیت درخواست')
class EmployeeRequestStatusUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeRequestStatusSerializer
    queryset = EmployeeRequest.objects.filter(is_deleted=False)
    http_method_names = ['patch']


@extend_schema(tags=['HR — Requests'], summary='حذف درخواست')
class EmployeeRequestDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = EmployeeRequest.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


@extend_schema(tags=['HR — Requests'], summary='لیست انواع درخواست')
class EmployeeRequestTypeListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeRequestTypeSerializer
    queryset = EmployeeRequestType.objects.filter(is_deleted=False)


@extend_schema(tags=['HR — Requests'], summary='ایجاد نوع درخواست')
class EmployeeRequestTypeCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeRequestTypeSerializer
    queryset = EmployeeRequestType.objects.filter(is_deleted=False)


@extend_schema(tags=['HR — Requests'], summary='حذف نوع درخواست')
class EmployeeRequestTypeDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = EmployeeRequestType.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


# -----------------------------------------------------------
# بخش ۵ — حضور و غیاب
# -----------------------------------------------------------

@extend_schema(tags=['HR — Attendance'], summary='لیست حضور و غیاب')
class EmployeeArrivalListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeArrivalSerializer
    filterset_class = EmployeeArrivalFilter
    queryset = EmployeeArrival.objects.filter(is_deleted=False).order_by('-check_in')


@extend_schema(tags=['HR — Attendance'], summary='ثبت حضور و غیاب')
class EmployeeArrivalCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeArrivalCreateSerializer
    queryset = EmployeeArrival.objects.filter(is_deleted=False)


@extend_schema(tags=['HR — Attendance'], summary='ویرایش حضور و غیاب')
class EmployeeArrivalUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeArrivalCreateSerializer
    queryset = EmployeeArrival.objects.filter(is_deleted=False)
    http_method_names = ['patch']


@extend_schema(tags=['HR — Attendance'], summary='حذف رکورد حضور و غیاب')
class EmployeeArrivalDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = EmployeeArrival.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])
