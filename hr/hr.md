# HR App — Endpoints Implementation

## معماری کلی

- تمام view ها از `rest_framework.generics` استفاده می‌کنند
- تمام serializer ها `ModelSerializer` استاندارد هستند
- تمام view ها `@extend_schema` فقط با دو فیلد `tags` و `summary` دارند
- فعلاً هیچ permission خاصی اعمال نمی‌شود — فقط `IsAuthenticated`
- تمام delete ها soft delete هستند (`is_deleted=True`)
- فیلترینگ با `django-filters`
- هر FK هم `{field}_id` و هم `{field}_detail` در serializer دارد (detail فیلد read_only است)

---

## مدل جدید — EmployeeOvertime

قبل از پیاده‌سازی endpoint ها این مدل را به `hr/models/employee_overtime.py` اضافه کن:

```python
from django.db import models
from .employee import Employee


class EmployeeOvertime(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name='overtimes'
    )
    date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=1)
    description = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_overtimes'
    )
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'اضافه‌کاری'
        verbose_name_plural = 'اضافه‌کاری‌ها'
        ordering = ['-date']

    def __str__(self):
        return f'{self.employee} — {self.date} — {self.hours}h'
```

`hr/models/__init__.py` را آپدیت کن:
```python
from .employee_overtime import EmployeeOvertime
```

---

## بخش ۱ — پرونده کارمندان

### Serializers

```python
# hr/serializers.py

# -----------------------------------------------------------
# Employee List — سبک، فقط اطلاعات پایه
# -----------------------------------------------------------
class EmployeeListSerializer(serializers.ModelSerializer):
    roles_detail = EmployeeRoleListSerializer(source='roles', many=True, read_only=True)
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'

    class Meta:
        model = Employee
        fields = [
            'id',
            'full_name',
            'first_name',
            'last_name',
            'employee_id',
            'profile_picture',
            'roles',        # write — list of IDs
            'roles_detail', # read
            'is_deleted',
            'created_at',
        ]


# -----------------------------------------------------------
# Employee Detail — کامل با آمار خلاصه
# -----------------------------------------------------------
class EmployeeDetailSerializer(serializers.ModelSerializer):
    roles_detail = EmployeeRoleListSerializer(source='roles', many=True, read_only=True)
    full_name = serializers.SerializerMethodField()
    wallet_balance = serializers.SerializerMethodField()
    last_arrival = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'

    def get_wallet_balance(self, obj):
        # از طریق obj.user به Wallet وصل میشه
        wallet = getattr(obj.user, 'wallet', None)
        return wallet.balance if wallet else 0

    def get_last_arrival(self, obj):
        arrival = obj.arrivals.filter(is_deleted=False).order_by('-check_in').first()
        if not arrival:
            return None
        return {
            'check_in': arrival.check_in,
            'check_out': arrival.check_out,
        }

    def get_stats(self, obj):
        return {
            'total_requests': obj.requests.filter(is_deleted=False).count(),
            'pending_requests': obj.requests.filter(status='waiting', is_deleted=False).count(),
            'total_files': obj.files.filter(is_deleted=False).count(),
            'total_overtimes': obj.overtimes.filter(is_deleted=False).count(),
            'pending_overtimes': obj.overtimes.filter(is_approved=False, is_deleted=False).count(),
        }

    class Meta:
        model = Employee
        fields = [
            'id',
            'full_name',
            'first_name',
            'last_name',
            'national_code',
            'birth_date',
            'employee_id',
            'profile_picture',
            'has_commission',
            'commission_amount',
            'roles',
            'roles_detail',
            'wallet_balance',
            'last_arrival',
            'stats',
            'is_deleted',
            'created_at',
            'updated_at',
        ]


# -----------------------------------------------------------
# Employee Create / Update
# -----------------------------------------------------------
class EmployeeCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            'user',
            'first_name',
            'last_name',
            'national_code',
            'birth_date',
            'employee_id',
            'profile_picture',
            'has_commission',
            'commission_amount',
            'roles',
        ]


# -----------------------------------------------------------
# EmployeeFile
# -----------------------------------------------------------
class EmployeeFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeFile
        fields = ['id', 'employee', 'title', 'file', 'created_at', 'updated_at']


# -----------------------------------------------------------
# EmployeeOvertime
# -----------------------------------------------------------
class EmployeeOvertimeSerializer(serializers.ModelSerializer):
    approved_by_detail = EmployeeListSerializer(source='approved_by', read_only=True)

    class Meta:
        model = EmployeeOvertime
        fields = [
            'id',
            'employee',
            'date',
            'hours',
            'description',
            'is_approved',
            'approved_by',
            'approved_by_detail',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['is_approved', 'approved_by']
```

### Filters

```python
# hr/filters.py
import django_filters
from .models import Employee, EmployeeOvertime, EmployeeArrival


class EmployeeFilter(django_filters.FilterSet):
    role = django_filters.NumberFilter(field_name='roles__id')
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    national_code = django_filters.CharFilter(lookup_expr='exact')
    employee_id = django_filters.CharFilter(lookup_expr='exact')

    class Meta:
        model = Employee
        fields = ['role', 'first_name', 'last_name', 'national_code', 'employee_id']


class EmployeeOvertimeFilter(django_filters.FilterSet):
    employee = django_filters.NumberFilter(field_name='employee__id')
    date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    is_approved = django_filters.BooleanFilter()

    class Meta:
        model = EmployeeOvertime
        fields = ['employee', 'date_from', 'date_to', 'is_approved']


class EmployeeArrivalFilter(django_filters.FilterSet):
    employee = django_filters.NumberFilter(field_name='employee__id')
    date_from = django_filters.DateFilter(field_name='check_in', lookup_expr='date__gte')
    date_to = django_filters.DateFilter(field_name='check_in', lookup_expr='date__lte')

    class Meta:
        model = EmployeeArrival
        fields = ['employee', 'date_from', 'date_to']
```

### Views

```python
# hr/views.py

# -----------------------------------------------------------
# Employee CRUD
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
```

### URLs

```python
# در hr/urls.py اضافه کن:

# Employees
path('employees/', EmployeeListView.as_view(), name='employee-list'),
path('employees/create/', EmployeeCreateView.as_view(), name='employee-create'),
path('employees/<int:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),
path('employees/<int:pk>/update/', EmployeeUpdateView.as_view(), name='employee-update'),
path('employees/<int:pk>/delete/', EmployeeDeleteView.as_view(), name='employee-delete'),

# Employee Files
path('employees/<int:employee_id>/files/', EmployeeFileListView.as_view(), name='employee-file-list'),
path('employees/files/create/', EmployeeFileCreateView.as_view(), name='employee-file-create'),
path('employees/files/<int:pk>/delete/', EmployeeFileDeleteView.as_view(), name='employee-file-delete'),

# Overtime
path('overtimes/', EmployeeOvertimeListView.as_view(), name='overtime-list'),
path('overtimes/create/', EmployeeOvertimeCreateView.as_view(), name='overtime-create'),
path('overtimes/<int:pk>/approve/', EmployeeOvertimeApproveView.as_view(), name='overtime-approve'),
path('overtimes/<int:pk>/delete/', EmployeeOvertimeDeleteView.as_view(), name='overtime-delete'),
```

---

## بخش ۲ — استخدام

### Serializers

```python
class EmploymentResumeSerializer(serializers.ModelSerializer):
    user_detail = serializers.SerializerMethodField()

    def get_user_detail(self, obj):
        return {
            'id': obj.user.id,
            'email': obj.user.email,
        }

    class Meta:
        model = EmploymentResume
        fields = [
            'id',
            'first_name',
            'last_name',
            'national_code',
            'birth_date',
            'phone_number',
            'description',
            'resume_file',
            'user',
            'user_detail',
            'created_at',
            'updated_at',
        ]
```

### Views

```python
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
```

### URLs

```python
path('resumes/', EmploymentResumeListView.as_view(), name='resume-list'),
path('resumes/<int:pk>/', EmploymentResumeDetailView.as_view(), name='resume-detail'),
path('resumes/create/', EmploymentResumeCreateView.as_view(), name='resume-create'),
path('resumes/<int:pk>/delete/', EmploymentResumeDeleteView.as_view(), name='resume-delete'),
```

---

## بخش ۳ — فیش حقوقی

> فیش حقوقی = یک `Invoice` با `is_payroll=True` + یک `PayrollDetail` وابسته به آن
> لیست پرداخت‌های هر فیش از مدل `Transaction` خوانده می‌شود

### Serializers

```python
class PayrollDetailSerializer(serializers.ModelSerializer):
    gross_salary = serializers.ReadOnlyField()
    total_deductions = serializers.ReadOnlyField()
    net_salary = serializers.ReadOnlyField()

    class Meta:
        model = PayrollDetail
        fields = [
            'id',
            'base_salary',
            'overtime_amount',
            'bonus',
            'housing_allowance',
            'food_allowance',
            'transportation_allowance',
            'insurance_deduction',
            'tax_deduction',
            'loan_deduction',
            'other_deductions',
            'work_days',
            'overtime_hours',
            'description',
            'gross_salary',
            'total_deductions',
            'net_salary',
        ]


class PayrollInvoiceListSerializer(serializers.ModelSerializer):
    account_side_detail = AccountSideSerializer(source='account_side', read_only=True)
    remaining_amount = serializers.ReadOnlyField()

    class Meta:
        model = Invoice
        fields = [
            'id',
            'account_side',
            'account_side_detail',
            'amount',
            'paid_amount',
            'remaining_amount',
            'payment_status',
            'status',
            'created_at',
        ]


class PayrollInvoiceDetailSerializer(serializers.ModelSerializer):
    account_side_detail = AccountSideSerializer(source='account_side', read_only=True)
    payroll_detail = PayrollDetailSerializer(read_only=True)
    remaining_amount = serializers.ReadOnlyField()

    class Meta:
        model = Invoice
        fields = [
            'id',
            'account_side',
            'account_side_detail',
            'category',
            'amount',
            'discount',
            'paid_amount',
            'remaining_amount',
            'status',
            'payment_status',
            'description',
            'payroll_detail',
            'created_at',
            'updated_at',
        ]


class PayrollCreateSerializer(serializers.Serializer):
    """
    صدور فیش حقوقی — Invoice + PayrollDetail را همزمان می‌سازد
    """
    # فیلدهای Invoice
    account_side = serializers.PrimaryKeyRelatedField(queryset=AccountSide.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=InvoiceCategory.objects.all())
    discount = serializers.IntegerField(default=0)
    description = serializers.CharField(required=False, allow_blank=True)

    # فیلدهای PayrollDetail
    base_salary = serializers.IntegerField(default=0)
    overtime_amount = serializers.IntegerField(default=0)
    bonus = serializers.IntegerField(default=0)
    housing_allowance = serializers.IntegerField(default=0)
    food_allowance = serializers.IntegerField(default=0)
    transportation_allowance = serializers.IntegerField(default=0)
    insurance_deduction = serializers.IntegerField(default=0)
    tax_deduction = serializers.IntegerField(default=0)
    loan_deduction = serializers.IntegerField(default=0)
    other_deductions = serializers.IntegerField(default=0)
    work_days = serializers.IntegerField(default=0)
    overtime_hours = serializers.IntegerField(default=0)
    payroll_description = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        from accounting.models import Invoice, PayrollDetail

        payroll_fields = [
            'base_salary', 'overtime_amount', 'bonus',
            'housing_allowance', 'food_allowance', 'transportation_allowance',
            'insurance_deduction', 'tax_deduction', 'loan_deduction',
            'other_deductions', 'work_days', 'overtime_hours', 'payroll_description'
        ]
        payroll_data = {k: validated_data.pop(k) for k in payroll_fields if k in validated_data}
        payroll_desc = payroll_data.pop('payroll_description', '')

        # محاسبه amount از net_salary
        gross = (
            payroll_data.get('base_salary', 0)
            + payroll_data.get('overtime_amount', 0)
            + payroll_data.get('bonus', 0)
            + payroll_data.get('housing_allowance', 0)
            + payroll_data.get('food_allowance', 0)
            + payroll_data.get('transportation_allowance', 0)
        )
        deductions = (
            payroll_data.get('insurance_deduction', 0)
            + payroll_data.get('tax_deduction', 0)
            + payroll_data.get('loan_deduction', 0)
            + payroll_data.get('other_deductions', 0)
        )
        net = gross - deductions

        invoice = Invoice.objects.create(
            **validated_data,
            amount=net,
            is_payroll=True,
            status='primary',
        )
        PayrollDetail.objects.create(
            invoice=invoice,
            description=payroll_desc,
            **payroll_data,
        )
        return invoice


class PayrollTransactionSerializer(serializers.ModelSerializer):
    bank_account_detail = BankAccountSerializer(source='bank_account', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id',
            'amount',
            'direction',
            'bank_account',
            'bank_account_detail',
            'description',
            'created_at',
        ]
```

### Views

```python
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
```

### URLs

```python
path('payrolls/', PayrollListView.as_view(), name='payroll-list'),
path('payrolls/create/', PayrollCreateView.as_view(), name='payroll-create'),
path('payrolls/<int:pk>/', PayrollDetailView.as_view(), name='payroll-detail'),
path('payrolls/<int:invoice_id>/transactions/', PayrollTransactionListView.as_view(), name='payroll-transactions'),
```

---

## بخش ۴ — درخواست‌ها

### Serializers

```python
class EmployeeRequestTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeRequestType
        fields = ['id', 'title', 'needs_approval', 'description']


class EmployeeRequestListSerializer(serializers.ModelSerializer):
    request_type_detail = EmployeeRequestTypeSerializer(source='request_type', read_only=True)
    employee_detail = EmployeeListSerializer(source='employee', read_only=True)

    class Meta:
        model = EmployeeRequest
        fields = [
            'id',
            'employee',
            'employee_detail',
            'title',
            'request_type',
            'request_type_detail',
            'status',
            'created_at',
        ]


class EmployeeRequestDetailSerializer(serializers.ModelSerializer):
    request_type_detail = EmployeeRequestTypeSerializer(source='request_type', read_only=True)
    employee_detail = EmployeeListSerializer(source='employee', read_only=True)

    class Meta:
        model = EmployeeRequest
        fields = [
            'id',
            'employee',
            'employee_detail',
            'title',
            'request_type',
            'request_type_detail',
            'description',
            'status',
            'created_at',
            'updated_at',
        ]


class EmployeeRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeRequest
        fields = ['employee', 'title', 'request_type', 'description']


class EmployeeRequestStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeRequest
        fields = ['status']
```

### Filters

```python
class EmployeeRequestFilter(django_filters.FilterSet):
    employee = django_filters.NumberFilter(field_name='employee__id')
    status = django_filters.ChoiceFilter(choices=EmployeeRequest._meta.get_field('status').choices)
    request_type = django_filters.NumberFilter(field_name='request_type__id')

    class Meta:
        model = EmployeeRequest
        fields = ['employee', 'status', 'request_type']
```

### Views

```python
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


# Request Types
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
```

### URLs

```python
# Request Types
path('request-types/', EmployeeRequestTypeListView.as_view(), name='request-type-list'),
path('request-types/create/', EmployeeRequestTypeCreateView.as_view(), name='request-type-create'),
path('request-types/<int:pk>/delete/', EmployeeRequestTypeDeleteView.as_view(), name='request-type-delete'),

# Requests
path('requests/', EmployeeRequestListView.as_view(), name='request-list'),
path('requests/<int:pk>/', EmployeeRequestDetailView.as_view(), name='request-detail'),
path('requests/create/', EmployeeRequestCreateView.as_view(), name='request-create'),
path('requests/<int:pk>/status/', EmployeeRequestStatusUpdateView.as_view(), name='request-status-update'),
path('requests/<int:pk>/delete/', EmployeeRequestDeleteView.as_view(), name='request-delete'),
```

---

## بخش ۵ — حضور و غیاب

### Serializers

```python
class EmployeeArrivalSerializer(serializers.ModelSerializer):
    employee_detail = EmployeeListSerializer(source='employee', read_only=True)
    duration_minutes = serializers.SerializerMethodField()

    def get_duration_minutes(self, obj):
        if obj.check_in and obj.check_out:
            delta = obj.check_out - obj.check_in
            return int(delta.total_seconds() / 60)
        return None

    class Meta:
        model = EmployeeArrival
        fields = [
            'id',
            'employee',
            'employee_detail',
            'check_in',
            'check_out',
            'duration_minutes',
            'created_at',
        ]


class EmployeeArrivalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeArrival
        fields = ['employee', 'check_in', 'check_out']
```

### Views

```python
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
```

### URLs

```python
path('arrivals/', EmployeeArrivalListView.as_view(), name='arrival-list'),
path('arrivals/create/', EmployeeArrivalCreateView.as_view(), name='arrival-create'),
path('arrivals/<int:pk>/update/', EmployeeArrivalUpdateView.as_view(), name='arrival-update'),
path('arrivals/<int:pk>/delete/', EmployeeArrivalDeleteView.as_view(), name='arrival-delete'),
```

---

## خلاصه تمام Endpoints

| Method | URL | عملکرد |
|--------|-----|---------|
| GET | `/hr/employees/` | لیست کارمندان |
| POST | `/hr/employees/create/` | ایجاد کارمند |
| GET | `/hr/employees/{id}/` | جزئیات کارمند |
| PATCH | `/hr/employees/{id}/update/` | ویرایش کارمند |
| DELETE | `/hr/employees/{id}/delete/` | حذف کارمند |
| GET | `/hr/employees/{employee_id}/files/` | فایل‌های کارمند |
| POST | `/hr/employees/files/create/` | آپلود فایل |
| DELETE | `/hr/employees/files/{id}/delete/` | حذف فایل |
| GET | `/hr/overtimes/` | لیست اضافه‌کاری‌ها |
| POST | `/hr/overtimes/create/` | ثبت اضافه‌کاری |
| PATCH | `/hr/overtimes/{id}/approve/` | تایید اضافه‌کاری |
| DELETE | `/hr/overtimes/{id}/delete/` | حذف اضافه‌کاری |
| GET | `/hr/resumes/` | لیست رزومه‌ها |
| GET | `/hr/resumes/{id}/` | جزئیات رزومه |
| POST | `/hr/resumes/create/` | ثبت رزومه |
| DELETE | `/hr/resumes/{id}/delete/` | حذف رزومه |
| GET | `/hr/payrolls/` | لیست فیش‌های حقوقی |
| GET | `/hr/payrolls/{id}/` | جزئیات فیش |
| POST | `/hr/payrolls/create/` | صدور فیش حقوقی |
| GET | `/hr/payrolls/{id}/transactions/` | پرداخت‌های یک فیش |
| GET | `/hr/request-types/` | انواع درخواست |
| POST | `/hr/request-types/create/` | ایجاد نوع درخواست |
| DELETE | `/hr/request-types/{id}/delete/` | حذف نوع درخواست |
| GET | `/hr/requests/` | لیست درخواست‌ها |
| GET | `/hr/requests/{id}/` | جزئیات درخواست |
| POST | `/hr/requests/create/` | ثبت درخواست |
| PATCH | `/hr/requests/{id}/status/` | تغییر وضعیت درخواست |
| DELETE | `/hr/requests/{id}/delete/` | حذف درخواست |
| GET | `/hr/arrivals/` | لیست حضور و غیاب |
| POST | `/hr/arrivals/create/` | ثبت حضور و غیاب |
| PATCH | `/hr/arrivals/{id}/update/` | ویرایش حضور و غیاب |
| DELETE | `/hr/arrivals/{id}/delete/` | حذف حضور و غیاب |