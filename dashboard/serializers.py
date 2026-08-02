from django.db.models import Sum
from django.utils.dateparse import parse_date
from rest_framework import serializers

from accounting.models import GameOrderItem, Transaction, GameOrder, Order, RepairOrder
from crm.models import Customer
from hr.models import Employee


class GameAndRepairOrderStatsSerializer(serializers.Serializer):
    by_order_type = serializers.DictField(
        child=serializers.IntegerField(), read_only=True
    )
    unpaid = serializers.IntegerField(read_only=True)
    delivered_to_customer = serializers.IntegerField(read_only=True)
    in_progress = serializers.IntegerField(read_only=True)


class OrderStatsSerializer(serializers.Serializer):
    employee = serializers.CharField(read_only=True)
    in_progress_orders = serializers.IntegerField(
        read_only=True, help_text="Number of orders in progress"
    )
    set_up_accounts = serializers.IntegerField(
        read_only=True, help_text="Number of items handled by account_setter"
    )
    uploaded_data = serializers.IntegerField(
        read_only=True, help_text="Number of items handled by data_uploader"
    )
    as_receptionist = serializers.IntegerField(
        read_only=True, help_text="Number of orders handled as reception"
    )


class ProductOrderStatsSerializer(serializers.Serializer):
    by_order_type = serializers.DictField(
        child=serializers.IntegerField(), read_only=True
    )
    unpaid = serializers.IntegerField(read_only=True)
    paid = serializers.IntegerField(read_only=True)


class FinanceSummarySerializer(serializers.Serializer):
    total_employee_debt = serializers.IntegerField(help_text="Amount receivable from employees")
    total_employee_credit = serializers.IntegerField(help_text="Amount payable to employees")
    total_customer_debt = serializers.IntegerField(help_text="Amount receivable from customers")
    total_customer_credit = serializers.IntegerField(help_text="Amount payable to customers")
    total_payment_method_balance = serializers.IntegerField(help_text="Total balance")
    net_balance = serializers.IntegerField(help_text="Net balance")


class EmployeeStatsSerializer(serializers.Serializer):
    account_setters = serializers.IntegerField()
    data_uploaders = serializers.IntegerField()
    recipients = serializers.IntegerField()
    mangers = serializers.IntegerField()
    all_employees = serializers.IntegerField()


class CustomerStatsSerializer(serializers.Serializer):
    business_customers = serializers.IntegerField()
    user_customers = serializers.IntegerField()
    customers = serializers.IntegerField()


class ProductStatsSerializer(serializers.Serializer):
    total_value = serializers.DecimalField(max_digits=25, decimal_places=5)
    total_count = serializers.IntegerField(read_only=True)


class RealAssetStatsSerializer(serializers.Serializer):
    value_sum = serializers.IntegerField()


class SellReportSerializer(serializers.Serializer):
    game_income = serializers.IntegerField()
    game_count = serializers.IntegerField()
    repair_income = serializers.IntegerField()
    repair_count = serializers.IntegerField()
    product_income = serializers.IntegerField()
    product_count = serializers.IntegerField()
    course_income = serializers.IntegerField()
    course_count = serializers.IntegerField()
    telegram_income = serializers.IntegerField()
    telegram_count = serializers.IntegerField()


class PaymentMethodReportSerializer(serializers.Serializer):
    title = serializers.CharField()
    balance = serializers.IntegerField()


class FinanceReportSerializer(serializers.Serializer):
    income_amount = serializers.IntegerField()
    outcome_amount = serializers.IntegerField()
    net_balance = serializers.IntegerField()
    balance = serializers.IntegerField()
    payment_methods = PaymentMethodReportSerializer(many=True)


class PerformanceReportSerializer(serializers.ModelSerializer):
    game_order_item_count_account = serializers.SerializerMethodField()
    game_order_item_count_data = serializers.SerializerMethodField()
    game_order_item_amount_sum = serializers.SerializerMethodField()
    employee_income_amount = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            "full_name",
            "game_order_item_count_account",
            "game_order_item_count_data",
            "game_order_item_amount_sum",
            "employee_income_amount",
        ]
        read_only_fields = fields

    def get_date_filters(self):
        """Helper method to get start-date and end-date from the context"""
        request = self.context.get("request")
        start_date_str = request.GET.get("start-date")
        end_date_str = request.GET.get("end-date")
        start_date = parse_date(start_date_str) if start_date_str else None
        end_date = parse_date(end_date_str) if end_date_str else None
        filters = {}
        if start_date:
            filters["created_at__date__gte"] = start_date
        if end_date:
            filters["created_at__date__lte"] = end_date
        return filters

    def get_game_order_item_count_account(self, obj):
        filters = self.get_date_filters()
        return GameOrderItem.objects.filter(account_setter=obj, **filters).count()

    def get_game_order_item_count_data(self, obj):
        filters = self.get_date_filters()
        return GameOrderItem.objects.filter(data_uploader=obj, **filters).count()

    def get_game_order_item_amount_sum(self, obj):
        filters = self.get_date_filters()
        return (
            GameOrderItem.objects.filter(account_setter=obj, **filters).aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

    def get_employee_income_amount(self, obj):
        filters = self.get_date_filters()
        return (
            Transaction.objects.filter(
                receiver=obj.user, in_out=False, **filters
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

    def get_full_name(self, obj):
        return str(obj)


class CustomerReportSerializer(serializers.ModelSerializer):
    game_order_count = serializers.SerializerMethodField()
    product_order_count = serializers.SerializerMethodField()
    repair_order_count = serializers.SerializerMethodField()
    customer_profit = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            "full_name",
            "game_order_count",
            "product_order_count",
            "repair_order_count",
            "customer_profit",
        ]

    def get_date_filters(self):
        """Helper for filtering by start-date and end-date"""
        request = self.context.get("request")
        start_date_str = request.GET.get("start-date")
        end_date_str = request.GET.get("end-date")
        start_date = parse_date(start_date_str) if start_date_str else None
        end_date = parse_date(end_date_str) if end_date_str else None
        filters = {}
        if start_date:
            filters["created_at__date__gte"] = start_date
        if end_date:
            filters["created_at__date__lte"] = end_date
        return filters

    def get_game_order_count(self, obj):
        filters = self.get_date_filters()
        return GameOrder.objects.filter(
            customer=obj, is_deleted=False, payment_status="paid", **filters
        ).count()

    def get_product_order_count(self, obj):
        filters = self.get_date_filters()
        return Order.objects.filter(
            customer=obj, is_deleted=False, payment_status="paid", **filters
        ).count()

    def get_repair_order_count(self, obj):
        filters = self.get_date_filters()
        return RepairOrder.objects.filter(
            customer=obj, is_deleted=False, payment_status="paid", **filters
        ).count()

    def get_customer_profit(self, obj):
        filters = self.get_date_filters()
        return (
            Transaction.objects.filter(
                payer=obj.user, in_out=True, is_deleted=False, status="paid", **filters
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )
