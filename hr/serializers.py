from rest_framework import serializers

from accounting.models import (
    Invoice,
    PayrollDetail,
    Transaction,
    AccountSide,
    InvoiceCategory,
)
from accounting.serializers import (
    AccountSideNestedSerializer as AccountSideSerializer,
    BankAccountNestedSerializer as BankAccountSerializer,
)
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


class PermissionSerializer(serializers.ModelSerializer):
    module_display = serializers.CharField(source='get_module_display', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = Permission
        fields = ['id', 'module', 'module_display', 'action', 'action_display', 'extra_flag']


class MyPermissionsSerializer(serializers.Serializer):
    """فرمت flat برای فرانت"""
    permissions = serializers.DictField()





class EmployeeRoleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeRole
        fields = ['id', 'role_name', 'description']


class EmployeeRoleDetailSerializer(serializers.ModelSerializer):
    permissions_detail = PermissionSerializer(source='permissions', many=True, read_only=True)
    permissions        = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(), many=True, write_only=True
    )

    class Meta:
        model = EmployeeRole
        fields = [
            'id', 'role_name', 'description',
            'permissions', 'permissions_detail',
            'created_at', 'updated_at'
        ]


# ═══════════════════════════════════════════════════════════
# بخش ۱ — پرونده کارمندان
# ═══════════════════════════════════════════════════════════

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
            'roles_detail',  # read
            'is_deleted',
            'created_at',
        ]


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


class EmployeeFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeFile
        fields = ['id', 'employee', 'title', 'file', 'created_at', 'updated_at']


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


# ═══════════════════════════════════════════════════════════
# بخش ۲ — استخدام
# ═══════════════════════════════════════════════════════════

class EmploymentResumeSerializer(serializers.ModelSerializer):
    user_detail = serializers.SerializerMethodField()

    def get_user_detail(self, obj):
        return {
            'id': obj.user.id,
            'phone': obj.user.phone,
            'full_name': obj.user.full_name(),
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


# ═══════════════════════════════════════════════════════════
# بخش ۳ — فیش حقوقی
# ═══════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════
# بخش ۴ — درخواست‌ها
# ═══════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════
# بخش ۵ — حضور و غیاب
# ═══════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════
# سازگاری با سایر اپ‌ها — task_manager به این وابسته است
# ═══════════════════════════════════════════════════════════

class EmployeeSerializer(serializers.ModelSerializer):
    """نمایش خلاصه کارمند — به‌صورت nested در task_manager استفاده می‌شود (read-only)."""
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
        ]