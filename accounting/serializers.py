from django.contrib.contenttypes.models import ContentType
from django.db import transaction as db_transaction
from rest_framework import serializers

from accounting.models import (
    BankAccount, AccountSide, InvoiceCategory, Invoice,
    InvoiceItem, PayrollDetail, Transaction,
)


class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ['id', 'app_label', 'model']


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = [
            'id', 'title', 'account_number', 'sheba',
            'description', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AccountSideSerializer(serializers.ModelSerializer):
    content_type_detail = ContentTypeSerializer(source='content_type', read_only=True)
    display_name = serializers.CharField(source='__str__', read_only=True)

    class Meta:
        model = AccountSide
        fields = [
            'id', 'name', 'type',
            'content_type', 'object_id',
            'content_type_detail', 'display_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InvoiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceCategory
        fields = ['id', 'title', 'direction', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class InvoiceItemSerializer(serializers.ModelSerializer):
    content_type_id = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all(),
        source='content_type',
        required=False,
        allow_null=True,
    )
    content_type_detail = ContentTypeSerializer(source='content_type', read_only=True)
    total_price = serializers.IntegerField(read_only=True)

    class Meta:
        model = InvoiceItem
        fields = [
            'id', 'title', 'quantity', 'unit_price', 'discount',
            'content_type_id', 'content_type_detail', 'object_id',
            'total_price', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PayrollDetailSerializer(serializers.ModelSerializer):
    gross_salary = serializers.SerializerMethodField()
    total_deductions = serializers.SerializerMethodField()
    net_salary = serializers.SerializerMethodField()

    class Meta:
        model = PayrollDetail
        fields = [
            'id',
            'base_salary', 'overtime_amount', 'bonus',
            'housing_allowance', 'food_allowance', 'transportation_allowance',
            'insurance_deduction', 'tax_deduction', 'loan_deduction', 'other_deductions',
            'work_days', 'overtime_hours', 'description',
            'gross_salary', 'total_deductions', 'net_salary',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_gross_salary(self, obj):
        return obj.gross_salary

    def get_total_deductions(self, obj):
        return obj.total_deductions

    def get_net_salary(self, obj):
        return obj.net_salary


class InvoiceMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'amount', 'status', 'payment_status', 'created_at']


class InvoiceSerializer(serializers.ModelSerializer):
    account_side_id = serializers.PrimaryKeyRelatedField(
        queryset=AccountSide.objects.filter(is_deleted=False),
        source='account_side',
    )
    account_side_detail = AccountSideSerializer(source='account_side', read_only=True)

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=InvoiceCategory.objects.filter(is_deleted=False),
        source='category',
    )
    category_detail = InvoiceCategorySerializer(source='category', read_only=True)

    items = InvoiceItemSerializer(many=True, read_only=True)
    remaining_amount = serializers.IntegerField(read_only=True)
    payroll_detail = PayrollDetailSerializer(read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id',
            'account_side_id', 'account_side_detail',
            'category_id', 'category_detail',
            'discount', 'amount', 'paid_amount',
            'status', 'payment_status', 'is_payroll',
            'description', 'remaining_amount',
            'items', 'payroll_detail',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'paid_amount', 'created_at', 'updated_at']


class TransactionSerializer(serializers.ModelSerializer):
    invoice_id = serializers.PrimaryKeyRelatedField(
        queryset=Invoice.objects.filter(is_deleted=False),
        source='invoice',
        required=False,
        allow_null=True,
    )
    invoice_detail = InvoiceMinimalSerializer(source='invoice', read_only=True)

    account_side_id = serializers.PrimaryKeyRelatedField(
        queryset=AccountSide.objects.filter(is_deleted=False),
        source='account_side',
    )
    account_side_detail = AccountSideSerializer(source='account_side', read_only=True)

    bank_account_id = serializers.PrimaryKeyRelatedField(
        queryset=BankAccount.objects.filter(is_deleted=False),
        source='bank_account',
    )
    bank_account_detail = BankAccountSerializer(source='bank_account', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id',
            'invoice_id', 'invoice_detail',
            'account_side_id', 'account_side_detail',
            'bank_account_id', 'bank_account_detail',
            'amount', 'direction', 'description',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ─── Issue Invoice Serializers ───────────────────────────────────────────────

class InvoiceItemCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    quantity = serializers.IntegerField(default=1)
    unit_price = serializers.IntegerField()
    discount = serializers.IntegerField(default=0)
    content_type_id = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all(),
        required=False,
        allow_null=True,
    )
    object_id = serializers.IntegerField(required=False, allow_null=True)


class IssueCustomerInvoiceSerializer(serializers.Serializer):
    account_side_id = serializers.PrimaryKeyRelatedField(
        queryset=AccountSide.objects.filter(is_deleted=False),
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=InvoiceCategory.objects.filter(is_deleted=False),
    )
    amount = serializers.IntegerField()
    discount = serializers.IntegerField(default=0)
    description = serializers.CharField(required=False, allow_blank=True, default='')
    items = InvoiceItemCreateSerializer(many=True)

    def validate_category_id(self, value):
        if value.direction != 'out':
            raise serializers.ValidationError(
                "دسته‌بندی فاکتور باید از نوع خروجی (out) باشد."
            )
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        with db_transaction.atomic():
            invoice = Invoice.objects.create(
                account_side=validated_data['account_side_id'],
                category=validated_data['category_id'],
                amount=validated_data['amount'],
                discount=validated_data.get('discount', 0),
                description=validated_data.get('description', ''),
                status='primary',
            )
            for item_data in items_data:
                InvoiceItem.objects.create(
                    invoice=invoice,
                    title=item_data['title'],
                    quantity=item_data.get('quantity', 1),
                    unit_price=item_data['unit_price'],
                    discount=item_data.get('discount', 0),
                    content_type=item_data.get('content_type_id'),
                    object_id=item_data.get('object_id'),
                )
        return invoice

    def to_representation(self, instance):
        return InvoiceSerializer(instance).data


class IssueSupplierInvoiceSerializer(serializers.Serializer):
    account_side_id = serializers.PrimaryKeyRelatedField(
        queryset=AccountSide.objects.filter(is_deleted=False),
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=InvoiceCategory.objects.filter(is_deleted=False),
    )
    amount = serializers.IntegerField()
    discount = serializers.IntegerField(default=0)
    description = serializers.CharField(required=False, allow_blank=True, default='')
    items = InvoiceItemCreateSerializer(many=True)

    def validate_category_id(self, value):
        if value.direction != 'in':
            raise serializers.ValidationError(
                "دسته‌بندی فاکتور خرید باید از نوع ورودی (in) باشد."
            )
        return value

    def validate_account_side_id(self, value):
        if value.type != 'supplier':
            raise serializers.ValidationError(
                "طرف حساب باید از نوع تامین‌کننده باشد."
            )
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        with db_transaction.atomic():
            invoice = Invoice.objects.create(
                account_side=validated_data['account_side_id'],
                category=validated_data['category_id'],
                amount=validated_data['amount'],
                discount=validated_data.get('discount', 0),
                description=validated_data.get('description', ''),
                status='primary',
            )
            for item_data in items_data:
                InvoiceItem.objects.create(
                    invoice=invoice,
                    title=item_data['title'],
                    quantity=item_data.get('quantity', 1),
                    unit_price=item_data['unit_price'],
                    discount=item_data.get('discount', 0),
                    content_type=item_data.get('content_type_id'),
                    object_id=item_data.get('object_id'),
                )
        return invoice

    def to_representation(self, instance):
        return InvoiceSerializer(instance).data


# ─── Pay Transaction Serializers ─────────────────────────────────────────────

class PayCustomerTransactionSerializer(serializers.Serializer):
    invoice_id = serializers.PrimaryKeyRelatedField(
        queryset=Invoice.objects.filter(is_deleted=False),
    )
    account_side_id = serializers.PrimaryKeyRelatedField(
        queryset=AccountSide.objects.filter(is_deleted=False),
    )
    bank_account_id = serializers.PrimaryKeyRelatedField(
        queryset=BankAccount.objects.filter(is_deleted=False),
    )
    amount = serializers.IntegerField()
    description = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_account_side_id(self, value):
        if value.type != 'customer':
            raise serializers.ValidationError(
                "طرف حساب باید از نوع مشتری باشد."
            )
        return value

    def create(self, validated_data):
        return Transaction.objects.create(
            invoice=validated_data['invoice_id'],
            account_side=validated_data['account_side_id'],
            bank_account=validated_data['bank_account_id'],
            amount=validated_data['amount'],
            description=validated_data.get('description', ''),
            direction='out',
        )

    def to_representation(self, instance):
        return TransactionSerializer(instance).data


class PaySupplierTransactionSerializer(serializers.Serializer):
    invoice_id = serializers.PrimaryKeyRelatedField(
        queryset=Invoice.objects.filter(is_deleted=False),
    )
    account_side_id = serializers.PrimaryKeyRelatedField(
        queryset=AccountSide.objects.filter(is_deleted=False),
    )
    bank_account_id = serializers.PrimaryKeyRelatedField(
        queryset=BankAccount.objects.filter(is_deleted=False),
    )
    amount = serializers.IntegerField()
    description = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_account_side_id(self, value):
        if value.type != 'supplier':
            raise serializers.ValidationError(
                "طرف حساب باید از نوع تامین‌کننده باشد."
            )
        return value

    def create(self, validated_data):
        return Transaction.objects.create(
            invoice=validated_data['invoice_id'],
            account_side=validated_data['account_side_id'],
            bank_account=validated_data['bank_account_id'],
            amount=validated_data['amount'],
            description=validated_data.get('description', ''),
            direction='out',
        )

    def to_representation(self, instance):
        return TransactionSerializer(instance).data


# ─── Choices Serializers ─────────────────────────────────────────────────────

class InvoiceCategoryChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceCategory
        fields = ['id', 'title', 'direction']


class BankAccountChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ['id', 'title']


class AccountSideChoiceSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source='__str__', read_only=True)

    class Meta:
        model = AccountSide
        fields = ['id', 'display_name', 'type']
