from rest_framework import serializers

from accounting.models import (
    Transaction, Invoice, InvoiceItem,
    PayrollDetail, BankAccount, AccountSide, InvoiceCategory
)


class KeyValueSerializer(serializers.Serializer):
    key = serializers.IntegerField()
    value = serializers.CharField()


class ChoiceKeyValueSerializer(serializers.Serializer):
    key = serializers.CharField()
    value = serializers.CharField()


# ── Shared ───────────────────────────────────────────────────────────────────

class WeeklyDaySerializer(serializers.Serializer):
    date = serializers.DateField()
    weekday = serializers.CharField()
    count = serializers.IntegerField()
    total_amount = serializers.IntegerField()


# ── Repair Order ─────────────────────────────────────────────────────────────

class RepairOrderSummarySerializer(serializers.Serializer):
    count = serializers.IntegerField()
    total_amount = serializers.IntegerField()


# ── Product Order ─────────────────────────────────────────────────────────────

class ProductOrderSummarySerializer(serializers.Serializer):
    count = serializers.IntegerField()
    total_amount = serializers.IntegerField()


class ProductOrderByCategorySerializer(serializers.Serializer):
    category = serializers.CharField()
    count = serializers.IntegerField()
    total_amount = serializers.IntegerField()


# ── Sony Account Order ────────────────────────────────────────────────────────

class SonyBySourceSerializer(serializers.Serializer):
    source = serializers.CharField()
    source_display = serializers.CharField()
    count = serializers.IntegerField()
    total_amount = serializers.IntegerField()


class SonyByTypeSerializer(serializers.Serializer):
    type = serializers.CharField()
    type_display = serializers.CharField()
    count = serializers.IntegerField()
    total_amount = serializers.IntegerField()


class SonyByCategorySerializer(serializers.Serializer):
    category_id = serializers.IntegerField(allow_null=True)
    category_title = serializers.CharField()
    category_type = serializers.CharField()
    count = serializers.IntegerField()
    total_amount = serializers.IntegerField()


class SonyByStageSerializer(serializers.Serializer):
    stage_id = serializers.IntegerField(allow_null=True)
    stage_title = serializers.CharField()
    count = serializers.IntegerField()
    total_amount = serializers.IntegerField()


class SonySummarySerializer(serializers.Serializer):
    count = serializers.IntegerField()
    total_amount = serializers.IntegerField()


class SonyAccountOrderFullReportSerializer(serializers.Serializer):
    summary = SonySummarySerializer()
    by_source = SonyBySourceSerializer(many=True)
    by_type = SonyByTypeSerializer(many=True)
    by_category = SonyByCategorySerializer(many=True)
    by_stage = SonyByStageSerializer(many=True)


# ── Financial ─────────────────────────────────────────────────────────────────

class DirectionSummarySerializer(serializers.Serializer):
    direction = serializers.CharField()
    direction_display = serializers.CharField()
    count = serializers.IntegerField()
    total_amount = serializers.IntegerField()


class NetFinancialSerializer(serializers.Serializer):
    income = DirectionSummarySerializer()
    expense = DirectionSummarySerializer()
    net = serializers.IntegerField()


# ── Shared Nested ─────────────────────────────────────────────────────────────

class BankAccountNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ['id', 'title', 'account_number']


class AccountSideNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountSide
        fields = ['id', 'name', 'type']


class InvoiceCategoryNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceCategory
        fields = ['id', 'title', 'direction']


# ── Transaction ───────────────────────────────────────────────────────────────

class TransactionListSerializer(serializers.ModelSerializer):
    account_side = AccountSideNestedSerializer(read_only=True)
    bank_account = BankAccountNestedSerializer(read_only=True)
    direction_display = serializers.CharField(source='get_direction_display', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'direction', 'direction_display', 'amount',
            'account_side', 'bank_account', 'description', 'created_at',
        ]


class TransactionDetailSerializer(serializers.ModelSerializer):
    account_side = AccountSideNestedSerializer(read_only=True)
    bank_account = BankAccountNestedSerializer(read_only=True)
    direction_display = serializers.CharField(source='get_direction_display', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'direction', 'direction_display', 'amount',
            'account_side', 'bank_account', 'invoice',
            'description', 'created_at', 'updated_at',
        ]


class TransactionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'invoice', 'account_side', 'bank_account',
            'amount', 'direction', 'description',
        ]


# ── Invoice Item ──────────────────────────────────────────────────────────────

class InvoiceItemSerializer(serializers.ModelSerializer):
    total_price = serializers.IntegerField(read_only=True)

    class Meta:
        model = InvoiceItem
        fields = [
            'id', 'title', 'quantity', 'unit_price',
            'discount', 'total_price',
        ]


# ── Invoice (shared base) ─────────────────────────────────────────────────────

class InvoiceListSerializer(serializers.ModelSerializer):
    account_side = AccountSideNestedSerializer(read_only=True)
    category = InvoiceCategoryNestedSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    remaining_amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'account_side', 'category',
            'amount', 'discount', 'paid_amount', 'remaining_amount',
            'status', 'status_display', 'payment_status', 'payment_status_display',
            'is_payroll', 'created_at',
        ]


class InvoiceDetailSerializer(serializers.ModelSerializer):
    account_side = AccountSideNestedSerializer(read_only=True)
    category = InvoiceCategoryNestedSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    remaining_amount = serializers.IntegerField(read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'account_side', 'category',
            'amount', 'discount', 'paid_amount', 'remaining_amount',
            'status', 'status_display', 'payment_status', 'payment_status_display',
            'is_payroll', 'description', 'items', 'created_at', 'updated_at',
        ]


class InvoiceWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            'account_side', 'category', 'amount',
            'discount', 'status', 'description',
        ]


# ── Payroll ───────────────────────────────────────────────────────────────────

class PayrollDetailNestedSerializer(serializers.ModelSerializer):
    gross_salary = serializers.IntegerField(read_only=True)
    total_deductions = serializers.IntegerField(read_only=True)
    net_salary = serializers.IntegerField(read_only=True)

    class Meta:
        model = PayrollDetail
        fields = [
            'base_salary', 'overtime_amount', 'bonus',
            'housing_allowance', 'food_allowance', 'transportation_allowance',
            'insurance_deduction', 'tax_deduction', 'loan_deduction', 'other_deductions',
            'work_days', 'overtime_hours', 'description',
            'gross_salary', 'total_deductions', 'net_salary',
        ]


class PayrollInvoiceListSerializer(serializers.ModelSerializer):
    account_side = AccountSideNestedSerializer(read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    remaining_amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'account_side', 'amount', 'paid_amount',
            'remaining_amount', 'payment_status', 'payment_status_display',
            'created_at',
        ]


class PayrollInvoiceDetailSerializer(serializers.ModelSerializer):
    account_side = AccountSideNestedSerializer(read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    remaining_amount = serializers.IntegerField(read_only=True)
    payroll_detail = PayrollDetailNestedSerializer(read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'account_side', 'amount', 'paid_amount',
            'remaining_amount', 'payment_status', 'payment_status_display',
            'description', 'payroll_detail', 'created_at', 'updated_at',
        ]


class PayrollInvoiceWriteSerializer(serializers.ModelSerializer):
    """
    account_side و category و is_payroll اتو ست میشن —
    کاربر فقط مبلغ و جزئیات حقوق رو میده
    """
    payroll_detail = PayrollDetailNestedSerializer()

    class Meta:
        model = Invoice
        fields = [
            'account_side', 'amount', 'discount',
            'status', 'description', 'payroll_detail',
        ]

    def create(self, validated_data):
        from accounting.models import InvoiceCategory
        payroll_data = validated_data.pop('payroll_detail')

        # category حقوقی رو اتو پیدا میکنه یا میسازه
        category, _ = InvoiceCategory.objects.get_or_create(
            title='حقوق و دستمزد',
            defaults={'direction': 'out'},
        )
        invoice = Invoice.objects.create(
            **validated_data,
            category=category,
            is_payroll=True,
        )
        PayrollDetail.objects.create(invoice=invoice, **payroll_data)
        return invoice

    def update(self, instance, validated_data):
        payroll_data = validated_data.pop('payroll_detail', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if payroll_data and hasattr(instance, 'payroll_detail'):
            for attr, value in payroll_data.items():
                setattr(instance.payroll_detail, attr, value)
            instance.payroll_detail.save()
        return instance
