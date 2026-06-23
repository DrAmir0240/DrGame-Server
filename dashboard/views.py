from django.db.models import Q, Sum, F, DecimalField, Count
from django.utils.dateparse import parse_date
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters
from rest_framework.response import Response

from accounting.models import GameOrder, GameOrderItem, Order, PaymentMethod, RepairOrder, CourseOrder, TelegramOrder, \
    Transaction
from crm.models import Customer
from dashboard.serializers import GameAndRepairOrderStatsSerializer, OrderStatsSerializer, ProductOrderStatsSerializer, \
    FinanceSummarySerializer, CustomerStatsSerializer, ProductStatsSerializer, EmployeeStatsSerializer, \
    RealAssetStatsSerializer, SellReportSerializer, FinanceReportSerializer, PerformanceReportSerializer, \
    CustomerReportSerializer
from hr.filters import EmployeeProductFilter, RealAssetsFilter
from hr.models import Employee, Repairman
from task_manager.models import PlanedTask
from inventory.models import Product, RealAssets
from task_manager.serializers import EmployeeTaskStatsSerializer
from users.auth import CustomJWTAuthentication
from users.permissions import IsMainManager, IsEmployee


# Create your views here.

# ==================== Stats Views ====================
class TaskStatsAPIView(generics.GenericAPIView):
    serializer_class = EmployeeTaskStatsSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, *args, **kwargs):
        employee = request.user.employee

        qs = PlanedTask.objects.filter(employee=employee, is_deleted=False)

        data = {
            "planed": qs.filter(status="planed").count(),
            "in progress": qs.filter(status="in progress").count(),
            "done": qs.filter(status="done").count(),
            "all": qs.count(),
        }

        serializer = self.get_serializer(data)
        return Response(serializer.data)


class GameOrderStatsAPIView(generics.GenericAPIView):
    serializer_class = GameAndRepairOrderStatsSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, *args, **kwargs):
        qs = GameOrder.objects.filter(is_deleted=False)

        data = {
            "by_order_type": {
                "customer": qs.filter(order_type="customer").count(),
                "employee": qs.filter(order_type="employee").count(),
            },
            "unpaid": qs.filter(payment_status="unpaid").count(),
            "delivered_to_customer": qs.filter(status="delivered_to_customer").count(),
            "in_progress": qs.exclude(
                status__in=["waiting_for_delivery", "delivered_to_customer"]
            ).count(),
        }

        serializer = self.get_serializer(data)
        return Response(serializer.data)


class PersonalGameOrderStatsAPIView(generics.GenericAPIView):
    serializer_class = OrderStatsSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, *args, **kwargs):
        employee = request.user.employee  # فرض بر اینه که هر یوزر یه Employee داره

        qs_orders = GameOrder.objects.filter(employee=employee, is_deleted=False)
        qs_items = GameOrderItem.objects.filter(
            Q(account_setter=employee) | Q(data_uploader=employee),
            is_deleted=False
        )

        data = {
            "employee": str(employee),
            "in_progress_orders": qs_orders.count(),
            "set_up_accounts": qs_items.filter(account_setter=employee).count(),
            "uploaded_data": qs_items.filter(data_uploader=employee).count(),
            "as_receptionist": qs_orders.count(),

        }

        serializer = self.get_serializer(data)
        return Response(serializer.data)


class ProductOrderStatsAPIView(generics.GenericAPIView):
    serializer_class = ProductOrderStatsSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, *args, **kwargs):
        qs = (

            Order.objects.filter(is_deleted=False))

        data = {
            "by_order_type": {
                "customer": qs.filter(order_type="customer").count(),
                "employee": qs.filter(order_type="employee").count(),
            },
            "unpaid": qs.filter(payment_status="unpaid").count(),
            "paid": qs.filter(payment_status="paid").count(),
        }

        serializer = self.get_serializer(data)
        return Response(serializer.data)


class RepairOrderStatsAPIView(generics.GenericAPIView):
    serializer_class = GameAndRepairOrderStatsSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, *args, **kwargs):
        qs = RepairOrder.objects.filter(is_deleted=False)

        data = {
            "unpaid": qs.filter(payment_status="unpaid").count(),
            "delivered_to_customer": qs.filter(status="delivered_to_customer").count(),
            "in_progress": qs.exclude(
                status__in=["waiting_for_delivery_to_drgame", "delivered_to_customer"]
            ).count(),
        }

        serializer = self.get_serializer(data)
        return Response(serializer.data)


class FinanceSummaryAPIView(generics.GenericAPIView):
    serializer_class = FinanceSummarySerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, *args, **kwargs):
        employees_credit = Employee.objects.filter(is_deleted=False, balance__gt=0)
        total_employee_credit = 0
        for employee in employees_credit:
            total_employee_credit += employee.balance
        employees_debt = Employee.objects.filter(is_deleted=False, balance__lt=0)
        total_employee_debt = 0
        for employee in employees_debt:
            total_employee_debt -= employee.balance
        customer_credit = Customer.objects.filter(is_deleted=False, balance__gt=0)
        total_customer_credit = 0
        for customer in customer_credit:
            total_customer_credit += customer.balance
        customer_debt = Customer.objects.filter(is_deleted=False, balance__lt=0)
        total_customer_debt = 0
        for customer in customer_debt:
            total_customer_debt -= customer.balance
        # موجودی همه متودهای پرداخت
        total_payment_method_balance = PaymentMethod.objects.filter(
            is_deleted=False
        ).aggregate(total=Sum('balance'))['total'] or 0
        total_repairman_credit = \
            Repairman.objects.filter(is_deleted=False, balance__gt=0).aggregate(total=Sum('balance'))[
                'total'] or 0

        net_balance = total_payment_method_balance - total_employee_credit - total_customer_credit + total_customer_debt + total_employee_debt - total_repairman_credit

        data = {
            "total_employee_credit": total_employee_credit,
            "total_employee_debt": total_employee_debt,
            "total_customer_credit": total_customer_credit,
            "total_customer_debt": total_customer_debt,
            "total_repairman_credit": total_repairman_credit,
            "total_payment_method_balance": total_payment_method_balance,
            "net_balance": net_balance
        }

        serializer = self.get_serializer(data)
        return Response(serializer.data)


class EmployeeStatsAPIView(generics.GenericAPIView):
    serializer_class = EmployeeStatsSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, *args, **kwargs):
        qs = Employee.objects.filter(is_deleted=False)
        data = {
            'account_setters': qs.filter(role='account_setter').count(),
            'data_uploaders': qs.filter(role='data_uploader').count(),
            'recipients': qs.filter(role='recipient').count(),
            'mangers': qs.filter(role='manger').count(),
            'all_employees': qs.count(),
        }
        serializer = self.get_serializer(data)
        return Response(serializer.data)


class CustomerStatsAPIView(generics.GenericAPIView):
    serializer_class = CustomerStatsSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, *args, **kwargs):
        qs = Customer.objects.filter(is_deleted=False)
        data = {
            'business_customers': qs.filter(is_business=True).count(),
            'user_customers': qs.filter(is_business=False).count(),
            'crm': qs.count(),
        }
        serializer = self.get_serializer(data)
        return Response(serializer.data)


class ProductsStatsAPIView(generics.GenericAPIView):
    serializer_class = ProductStatsSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EmployeeProductFilter  # همون فیلتر لیست

    def get_queryset(self):
        return (
            Product.objects
            .filter(is_deleted=False)
            .select_related("category", "company", "color")
        )

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        aggregates = queryset.aggregate(
            total_value=Sum(
                F("price") * F("stock"),
                output_field=DecimalField(max_digits=25, decimal_places=5)
            ),
            total_count=Count("id")
        )

        serializer = self.get_serializer({
            "total_value": aggregates["total_value"] or 0,
            "total_count": aggregates["total_count"] or 0
        })

        return Response(serializer.data)


class RealAssetStatsAPIView(generics.GenericAPIView):
    serializer_class = RealAssetStatsSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RealAssetsFilter

    def get_queryset(self):
        return (
            RealAssets.objects
            .filter(is_deleted=False)
            .select_related("category", "category__category")
        )

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        total_price = queryset.aggregate(
            value_sum=Sum("price")
        )["value_sum"] or 0

        serializer = self.get_serializer({
            "value_sum": total_price
        })

        return Response(serializer.data)


# ==================== Reports Views ====================
class SellReportsAPIView(generics.GenericAPIView):
    """
    با گذاشتن
    ?start-date=2025-08-01&end-date=2025-08-15
    در انتهای یو ار ال نتایج بر حس تاریخ فیلتر میشوند
    """
    serializer_class = SellReportSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, *args, **kwargs):
        # گرفتن پارامترهای تاریخ از URL
        start_date_str = request.GET.get('start-date')
        end_date_str = request.GET.get('end-date')

        start_date = parse_date(start_date_str) if start_date_str else None
        end_date = parse_date(end_date_str) if end_date_str else None

        # فیلتر دینامیک برای هر مدل
        gqs = GameOrder.objects.filter(is_deleted=False, payment_status='paid')
        rqs = RepairOrder.objects.filter(is_deleted=False, payment_status='paid')
        pqs = Order.objects.filter(is_deleted=False, payment_status='paid')
        cqs = CourseOrder.objects.filter(is_deleted=False, payment_status='paid')
        tqs = TelegramOrder.objects.filter(is_deleted=False)

        if start_date:
            gqs = gqs.filter(created_at__date__gte=start_date)
            rqs = rqs.filter(created_at__date__gte=start_date)
            pqs = pqs.filter(created_at__date__gte=start_date)
            cqs = cqs.filter(created_at__date__gte=start_date)
            tqs = tqs.filter(created_at__date__gte=start_date)

        if end_date:
            gqs = gqs.filter(created_at__date__lte=end_date)
            rqs = rqs.filter(created_at__date__lte=end_date)
            pqs = pqs.filter(created_at__date__lte=end_date)
            cqs = cqs.filter(created_at__date__lte=end_date)
            tqs = tqs.filter(created_at__date__lte=end_date)

        data = {
            'game_income': gqs.aggregate(total=Sum('amount'))['total'] or 0,
            'game_count': gqs.count(),
            'repair_income': rqs.aggregate(total=Sum('amount'))['total'] or 0,
            'repair_count': rqs.count(),
            'product_income': pqs.aggregate(total=Sum('amount'))['total'] or 0,
            'product_count': pqs.count(),
            'course_income': cqs.aggregate(total=Sum('amount'))['total'] or 0,
            'course_count': cqs.count(),
            'telegram_income': tqs.aggregate(total=Sum('amount'))['total'] or 0,
            'telegram_count': tqs.count(),
        }

        serializer = self.get_serializer(data)
        return Response(serializer.data)


class FinanceReportsAPIView(generics.GenericAPIView):
    serializer_class = FinanceReportSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, *args, **kwargs):
        # پارامترهای تاریخ از URL
        start_date_str = request.GET.get('start-date')
        end_date_str = request.GET.get('end-date')

        start_date = parse_date(start_date_str) if start_date_str else None
        end_date = parse_date(end_date_str) if end_date_str else None

        # کوئری‌ست پایه
        qs = Transaction.objects.filter(is_deleted=False, status='paid')

        # فیلتر بر اساس created_at
        if start_date:
            qs = qs.filter(created_at__date__gte=start_date)
        if end_date:
            qs = qs.filter(created_at__date__lte=end_date)

        # محاسبه مقادیر
        income_amount = qs.filter(in_out=True).aggregate(total=Sum('amount'))['total'] or 0
        outcome_amount = qs.filter(in_out=False).aggregate(total=Sum('amount'))['total'] or 0
        net_balance = income_amount - outcome_amount
        balance = PaymentMethod.objects.filter(is_deleted=False).aggregate(total=Sum('balance'))['total'] or 0
        payment_methods_qs = PaymentMethod.objects.filter(is_deleted=False).values('title', 'balance')
        payment_methods = list(payment_methods_qs)
        data = {
            "income_amount": income_amount,
            "outcome_amount": outcome_amount,
            "balance": balance,
            "net_balance": net_balance,
            "payment_methods": payment_methods,

        }

        serializer = self.get_serializer(data)
        return Response(serializer.data)


class PerFormanceReportAPIView(generics.ListAPIView):
    """
    با گذاشتن
    ?start-date=2025-08-01&end-date=2025-08-15
    در انتهای یو ار ال نتایج بر حس تاریخ فیلتر میشوند
    """
    queryset = Employee.objects.filter(is_deleted=False)
    serializer_class = PerformanceReportSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class CustomerReportAPIView(generics.ListAPIView):
    """
    با گذاشتن
    ?start-date=2025-08-01&end-date=2025-08-15
    در انتهای یو ار ال نتایج بر حس تاریخ فیلتر میشوند
    """
    queryset = Customer.objects.filter(is_deleted=False)
    serializer_class = CustomerReportSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

