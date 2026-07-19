from django.urls import path
from hr import views

urlpatterns = [
    # Permissions
    path('permissions/', views.PermissionListView.as_view(), name='permission-list'),
    path('my-permissions/', views.MyPermissionsView.as_view(), name='my-permissions'),

    # Roles
    path('roles/', views.EmployeeRoleListView.as_view(), name='role-list'),
    path('roles/create/', views.EmployeeRoleCreateView.as_view(), name='role-create'),
    path('roles/<int:pk>/', views.EmployeeRoleDetailView.as_view(), name='role-detail'),
    path('roles/<int:pk>/update/', views.EmployeeRoleUpdateView.as_view(), name='role-update'),
    path('roles/<int:pk>/delete/', views.EmployeeRoleDeleteView.as_view(), name='role-delete'),

    # ── بخش ۱ — Employees ────────────────────────────────────
    path('employees/', views.EmployeeListView.as_view(), name='employee-list'),
    path('employees/create/', views.EmployeeCreateView.as_view(), name='employee-create'),
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee-detail'),
    path('employees/<int:pk>/update/', views.EmployeeUpdateView.as_view(), name='employee-update'),
    path('employees/<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee-delete'),

    # Employee Files
    path('employees/<int:employee_id>/files/', views.EmployeeFileListView.as_view(), name='employee-file-list'),
    path('employees/files/create/', views.EmployeeFileCreateView.as_view(), name='employee-file-create'),
    path('employees/files/<int:pk>/delete/', views.EmployeeFileDeleteView.as_view(), name='employee-file-delete'),

    # Overtime
    path('overtimes/', views.EmployeeOvertimeListView.as_view(), name='overtime-list'),
    path('overtimes/create/', views.EmployeeOvertimeCreateView.as_view(), name='overtime-create'),
    path('overtimes/<int:pk>/approve/', views.EmployeeOvertimeApproveView.as_view(), name='overtime-approve'),
    path('overtimes/<int:pk>/delete/', views.EmployeeOvertimeDeleteView.as_view(), name='overtime-delete'),

    # ── بخش ۲ — Recruitment ──────────────────────────────────
    path('resumes/', views.EmploymentResumeListView.as_view(), name='resume-list'),
    path('resumes/<int:pk>/', views.EmploymentResumeDetailView.as_view(), name='resume-detail'),
    path('resumes/create/', views.EmploymentResumeCreateView.as_view(), name='resume-create'),
    path('resumes/<int:pk>/delete/', views.EmploymentResumeDeleteView.as_view(), name='resume-delete'),

    # ── بخش ۳ — Payroll ──────────────────────────────────────
    path('payrolls/', views.PayrollListView.as_view(), name='payroll-list'),
    path('payrolls/create/', views.PayrollCreateView.as_view(), name='payroll-create'),
    path('payrolls/<int:pk>/', views.PayrollDetailView.as_view(), name='payroll-detail'),
    path('payrolls/<int:invoice_id>/transactions/', views.PayrollTransactionListView.as_view(),
         name='payroll-transactions'),

    # ── بخش ۴ — Requests ─────────────────────────────────────
    path('request-types/', views.EmployeeRequestTypeListView.as_view(), name='request-type-list'),
    path('request-types/create/', views.EmployeeRequestTypeCreateView.as_view(), name='request-type-create'),
    path('request-types/<int:pk>/delete/', views.EmployeeRequestTypeDeleteView.as_view(),
         name='request-type-delete'),

    path('requests/', views.EmployeeRequestListView.as_view(), name='request-list'),
    path('requests/<int:pk>/', views.EmployeeRequestDetailView.as_view(), name='request-detail'),
    path('requests/create/', views.EmployeeRequestCreateView.as_view(), name='request-create'),
    path('requests/<int:pk>/status/', views.EmployeeRequestStatusUpdateView.as_view(), name='request-status-update'),
    path('requests/<int:pk>/delete/', views.EmployeeRequestDeleteView.as_view(), name='request-delete'),

    # ── بخش ۵ — Attendance ───────────────────────────────────
    path('arrivals/', views.EmployeeArrivalListView.as_view(), name='arrival-list'),
    path('arrivals/create/', views.EmployeeArrivalCreateView.as_view(), name='arrival-create'),
    path('arrivals/<int:pk>/update/', views.EmployeeArrivalUpdateView.as_view(), name='arrival-update'),
    path('arrivals/<int:pk>/delete/', views.EmployeeArrivalDeleteView.as_view(), name='arrival-delete'),
]
