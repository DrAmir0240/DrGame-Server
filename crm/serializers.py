from django.db import models
from rest_framework import serializers

from accounting.models import Transaction, Invoice
from crm.models import Customer, B2BProfile


class CustomerListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    has_b2b = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ['id', 'full_name', 'phone', 'address', 'postal_code', 'profile_pic', 'has_b2b', 'created_at']

    def get_full_name(self, obj):
        return obj.user.full_name()

    def get_phone(self, obj):
        return obj.user.phone  # یا هر فیلدی که CustomUser داره

    def get_has_b2b(self, obj):
        return hasattr(obj, 'b2b_profile') and not obj.b2b_profile.is_deleted


class CustomerCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['address', 'postal_code', 'profile_pic']

    def destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=('is_deleted',))
        return instance


class B2BProfileSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(source='customer.id', read_only=True)

    class Meta:
        model = B2BProfile
        fields = [
            'id', 'customer_id', 'business_title', 'debt_amount_max',
            'uni_id', 'discount', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'customer_id', 'created_at', 'updated_at']

    def destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=('is_deleted',))
        return instance


class CustomerTransactionListSerializer(serializers.ModelSerializer):
    direction_display = serializers.CharField(source='get_direction_display', read_only=True)
    bank_account_name = serializers.CharField(source='bank_account.__str__', read_only=True)
    invoice_id = serializers.IntegerField(source='invoice.id', read_only=True, allow_null=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'amount', 'direction', 'direction_display',
            'bank_account_id', 'bank_account_name',
            'invoice_id', 'description', 'created_at',
        ]


class CustomerInvoiceListSerializer(serializers.ModelSerializer):
    total_items_price = serializers.SerializerMethodField()
    paid_amount = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            'id', 'total_items_price', 'paid_amount',
            'created_at', 'updated_at',
        ]

    def get_total_items_price(self, obj):
        return sum(
            item.total_price
            for item in obj.items.filter(is_deleted=False)
        )

    def get_paid_amount(self, obj):
        return obj.transactions.filter(
            is_deleted=False, direction='in'
        ).aggregate(total=models.Sum('amount'))['total'] or 0


class CustomerSummarySerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    full_name = serializers.CharField()

    product_orders_count = serializers.IntegerField()
    repair_orders_count = serializers.IntegerField()
    sony_account_orders_count = serializers.IntegerField()
    total_orders_count = serializers.IntegerField()

    total_transactions_amount = serializers.IntegerField()
    total_invoices_amount = serializers.IntegerField()


class SendSmsSerializer(serializers.Serializer):
    message = serializers.CharField()
    customer_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False
    )
    send_time = serializers.DateTimeField(required=False)
