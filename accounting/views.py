from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from accounting.filters import DailyTransactionFilter, DailyInvoiceFilter, IncomeInvoiceFilter, ExpenseInvoiceFilter, \
    PayrollInvoiceFilter
from accounting.helper import (
    parse_date_range,
    RepairOrderReportHelper,
    ProductOrderReportHelper,
    SonyAccountOrderReportHelper,
    InvoiceDropdownHelper,
    FinancialReportHelper,
)
from accounting.models import Transaction, Invoice, InvoiceCategory
from accounting.serializers import (
    DirectionSummarySerializer,
    NetFinancialSerializer,
    RepairOrderSummarySerializer,
    WeeklyDaySerializer,
    ProductOrderSummarySerializer,
    ProductOrderByCategorySerializer,
    SonyAccountOrderFullReportSerializer, TransactionListSerializer, TransactionDetailSerializer, InvoiceListSerializer,
    InvoiceDetailSerializer, InvoiceWriteSerializer, PayrollInvoiceListSerializer, PayrollInvoiceDetailSerializer,
    PayrollInvoiceWriteSerializer,
)

DATE_RANGE_PARAMS = [
    OpenApiParameter(
        'start_date',
        OpenApiTypes.DATE,
        location='query',
        required=False,
        description='پیش‌فرض: اول ماه جاری — فرمت: YYYY-MM-DD',
    ),
    OpenApiParameter(
        'end_date',
        OpenApiTypes.DATE,
        location='query',
        required=False,
        description='پیش‌فرض: بدون محدودیت — فرمت: YYYY-MM-DD',
    ),
]


# ── Dropdown Choices ──────────────────────────────────────────────────────────────────
@extend_schema(
    tags=['حسابداری - چویسس'],
    summary='چویسس برای بخش حسابداری',
)
class InvoiceDropdownView(generics.ListAPIView):
    """
    GET /api/accounting/invoice/dropdown/?type=account_side
    GET /api/accounting/invoice/dropdown/?type=category
    GET /api/accounting/invoice/dropdown/?type=status
    GET /api/accounting/invoice/dropdown/?type=payment_status
    """

    serializer_class = None  # ← به جای override کردن get_serializer_class

    HANDLERS = {
        'account_side',
        'category',
        'status',
        'payment_status',
    }

    def list(self, request, *args, **kwargs):
        t = request.query_params.get('type')

        if not t:
            raise ValidationError({'type': 'این پارامتر الزامیه.'})

        if t not in self.HANDLERS:
            raise ValidationError(
                {'type': f'مقدار نامعتبر. گزینه‌های مجاز: {", ".join(self.HANDLERS)}'}
            )

        handler = getattr(InvoiceDropdownHelper, f'get_{t}')
        return Response(handler())


# ── Repair Order ──────────────────────────────────────────────────────────────
@extend_schema(
    tags=[' حسابداری - گزارش — تعمیرات'],
    parameters=DATE_RANGE_PARAMS,
    responses=RepairOrderSummarySerializer,
    summary='گزارش کلی سفارشات تعمیر',
)
class RepairOrderReportView(generics.GenericAPIView):
    serializer_class = RepairOrderSummarySerializer

    @staticmethod
    def get(request, *args, **kwargs):
        start, end = parse_date_range(request)
        return Response(RepairOrderReportHelper.get_summary(start, end))


@extend_schema(
    tags=[' حسابداری - گزارش — تعمیرات'],
    responses=WeeklyDaySerializer(many=True),
    summary='گزارش هفتگی سفارشات تعمیر (شنبه تا جمعه)',
)
class RepairOrderWeeklyReportView(generics.GenericAPIView):
    serializer_class = WeeklyDaySerializer

    @staticmethod
    def get(request, *args, **kwargs):
        return Response(RepairOrderReportHelper.get_weekly_breakdown())


# ── Product Order ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=[' حسابداری - گزارش — سفارش کالا'],
    parameters=DATE_RANGE_PARAMS,
    responses=ProductOrderSummarySerializer,
    summary='گزارش کلی سفارشات کالا',
)
class ProductOrderReportView(generics.GenericAPIView):
    serializer_class = ProductOrderSummarySerializer

    @staticmethod
    def get(request, *args, **kwargs):
        start, end = parse_date_range(request)
        return Response(ProductOrderReportHelper.get_summary(start, end))


@extend_schema(
    tags=[' حسابداری - گزارش — سفارش کالا'],
    responses=WeeklyDaySerializer(many=True),
    summary='گزارش هفتگی سفارشات کالا (شنبه تا جمعه)',
)
class ProductOrderWeeklyReportView(generics.GenericAPIView):
    serializer_class = WeeklyDaySerializer

    @staticmethod
    def get(request, *args, **kwargs):
        return Response(ProductOrderReportHelper.get_weekly_breakdown())


@extend_schema(
    tags=[' حسابداری - گزارش — سفارش کالا'],
    parameters=DATE_RANGE_PARAMS,
    responses=ProductOrderByCategorySerializer(many=True),
    summary='گزارش سفارشات کالا به تفکیک دسته‌بندی',
)
class ProductOrderByCategoryReportView(generics.GenericAPIView):
    serializer_class = ProductOrderByCategorySerializer

    @staticmethod
    def get(request, *args, **kwargs):
        start, end = parse_date_range(request)
        return Response(ProductOrderReportHelper.get_by_category(start, end))


# ── Sony Account Order ────────────────────────────────────────────────────────
@extend_schema(
    tags=[' حسابداری - گزارش — اکانت سونی'],
    parameters=DATE_RANGE_PARAMS,
    responses=SonyAccountOrderFullReportSerializer,
    summary='گزارش کامل سفارشات اکانت سونی (summary + تفکیک همه فیلدها)',
)
class SonyAccountOrderReportView(generics.GenericAPIView):
    serializer_class = SonyAccountOrderFullReportSerializer

    @staticmethod
    def get(request, *args, **kwargs):
        start, end = parse_date_range(request)
        return Response({
            'summary': SonyAccountOrderReportHelper.get_summary(start, end),
            'by_source': SonyAccountOrderReportHelper.get_by_source(start, end),
            'by_type': SonyAccountOrderReportHelper.get_by_type(start, end),
            'by_category': SonyAccountOrderReportHelper.get_by_category(start, end),
            'by_stage': SonyAccountOrderReportHelper.get_by_stage(start, end),
        })


@extend_schema(
    tags=[' حسابداری - گزارش — اکانت سونی'],
    responses=WeeklyDaySerializer(many=True),
    summary='گزارش هفتگی سفارشات اکانت سونی (شنبه تا جمعه)',
)
class SonyAccountOrderWeeklyReportView(generics.GenericAPIView):
    serializer_class = WeeklyDaySerializer

    @staticmethod
    def get(request, *args, **kwargs):
        return Response(SonyAccountOrderReportHelper.get_weekly_breakdown())


# ── Financial ─────────────────────────────────────────────────────────────────
@extend_schema(
    tags=[' حسابداری - گزارش — مالی'],
    parameters=DATE_RANGE_PARAMS,
    responses=DirectionSummarySerializer,
    summary='گزارش درآمدها (تراکنش‌های دریافتی)',
)
class IncomeReportView(generics.GenericAPIView):
    serializer_class = DirectionSummarySerializer

    @staticmethod
    def get(request, *args, **kwargs):
        start, end = parse_date_range(request)
        return Response(FinancialReportHelper.get_income_summary(start, end))


@extend_schema(
    tags=[' حسابداری - گزارش — مالی'],
    parameters=DATE_RANGE_PARAMS,
    responses=DirectionSummarySerializer,
    summary='گزارش هزینه‌ها (تراکنش‌های پرداختی)',
)
class ExpenseReportView(generics.GenericAPIView):
    serializer_class = DirectionSummarySerializer

    @staticmethod
    def get(request, *args, **kwargs):
        start, end = parse_date_range(request)
        return Response(FinancialReportHelper.get_expense_summary(start, end))


@extend_schema(
    tags=[' حسابداری - گزارش — مالی'],
    parameters=DATE_RANGE_PARAMS,
    responses=NetFinancialSerializer,
    summary='گزارش خالص مالی (درآمد − هزینه)',
)
class NetFinancialReportView(generics.GenericAPIView):
    serializer_class = NetFinancialSerializer

    @staticmethod
    def get(request, *args, **kwargs):
        start, end = parse_date_range(request)
        return Response(FinancialReportHelper.get_net_summary(start, end))


@extend_schema(
    tags=[' حسابداری - گزارش — مالی'],
    responses=WeeklyDaySerializer(many=True),
    summary='گزارش هفتگی درآمدها (شنبه تا جمعه)',
)
class IncomeWeeklyReportView(generics.GenericAPIView):
    serializer_class = WeeklyDaySerializer

    @staticmethod
    def get(request, *args, **kwargs):
        return Response(FinancialReportHelper.get_weekly_breakdown('in'))


@extend_schema(
    tags=[' حسابداری - گزارش — مالی'],
    responses=WeeklyDaySerializer(many=True),
    summary='گزارش هفتگی هزینه‌ها (شنبه تا جمعه)',
)
class ExpenseWeeklyReportView(generics.GenericAPIView):
    serializer_class = WeeklyDaySerializer

    @staticmethod
    def get(request, *args, **kwargs):
        return Response(FinancialReportHelper.get_weekly_breakdown('out'))


# ── Daily Transactions ────────────────────────────────────────────────────────
@extend_schema(tags=[' حسابداری - دفتر روزانه'], summary='لیست تراکنش‌های امروز')
class DailyTransactionListView(generics.ListAPIView):
    serializer_class = (
        TransactionListSerializer)
    filterset_class = DailyTransactionFilter

    def get_queryset(self):
        return Transaction.objects.filter(
            is_deleted=False,
        ).select_related('account_side', 'bank_account').order_by('-created_at')


@extend_schema(tags=[' حسابداری - دفتر روزانه'], summary='جزئیات تراکنش')
class DailyTransactionDetailView(generics.RetrieveAPIView):
    serializer_class = TransactionDetailSerializer

    def get_queryset(self):
        return Transaction.objects.filter(is_deleted=False).select_related(
            'account_side', 'bank_account'
        )


@extend_schema(tags=[' حسابداری - دفتر روزانه'], summary='ویرایش تراکنش')
class DailyTransactionUpdateView(generics.UpdateAPIView):
    serializer_class = TransactionDetailSerializer

    def get_queryset(self):
        return Transaction.objects.filter(is_deleted=False)


@extend_schema(tags=[' حسابداری - دفتر روزانه'], summary='حذف تراکنش (soft delete)')
class DailyTransactionDeleteView(generics.DestroyAPIView):
    def get_queryset(self):
        return Transaction.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


# ── Daily Invoices ────────────────────────────────────────────────────────────

@extend_schema(tags=[' حسابداری - دفتر روزانه'], summary='لیست فاکتورهای امروز')
class DailyInvoiceListView(generics.ListAPIView):
    serializer_class = InvoiceListSerializer
    filterset_class = DailyInvoiceFilter

    def get_queryset(self):
        return Invoice.objects.filter(
            is_deleted=False,
        ).select_related('account_side', 'category').order_by('-created_at')


@extend_schema(tags=[' حسابداری - دفتر روزانه'], summary='جزئیات فاکتور')
class DailyInvoiceDetailView(generics.RetrieveAPIView):
    serializer_class = InvoiceDetailSerializer

    def get_queryset(self):
        return Invoice.objects.filter(is_deleted=False).select_related(
            'account_side', 'category'
        ).prefetch_related('items')


@extend_schema(tags=[' حسابداری - دفتر روزانه'], summary='ویرایش فاکتور')
class DailyInvoiceUpdateView(generics.UpdateAPIView):
    serializer_class = InvoiceDetailSerializer

    def get_queryset(self):
        return Invoice.objects.filter(is_deleted=False)


@extend_schema(tags=[' حسابداری - دفتر روزانه'], summary='حذف فاکتور (soft delete)')
class DailyInvoiceDeleteView(generics.DestroyAPIView):
    def get_queryset(self):
        return Invoice.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


def get_income_category():
    category, _ = InvoiceCategory.objects.get_or_create(
        direction='in',
        defaults={'title': 'درآمد'},
    )
    return category


@extend_schema(tags=['حسابداری — درآمد'], summary='لیست فاکتورهای درآمدی')
class IncomeInvoiceListView(generics.ListAPIView):
    serializer_class = InvoiceListSerializer
    filterset_class = IncomeInvoiceFilter

    def get_queryset(self):
        return Invoice.objects.filter(
            is_deleted=False,
            category__direction='in',
            is_payroll=False,
        ).select_related('account_side', 'category').order_by('-created_at')


@extend_schema(tags=['حسابداری — درآمد'], summary='جزئیات فاکتور درآمدی')
class IncomeInvoiceDetailView(generics.RetrieveAPIView):
    serializer_class = InvoiceDetailSerializer

    def get_queryset(self):
        return Invoice.objects.filter(
            is_deleted=False,
            category__direction='in',
        ).select_related('account_side', 'category').prefetch_related('items')


@extend_schema(tags=['حسابداری — درآمد'], summary='ثبت فاکتور درآمدی')
class IncomeInvoiceCreateView(generics.CreateAPIView):
    serializer_class = InvoiceWriteSerializer

    def perform_create(self, serializer):
        serializer.save(
            category=get_income_category(),
            is_payroll=False,
        )


@extend_schema(tags=['حسابداری — درآمد'], summary='ویرایش فاکتور درآمدی')
class IncomeInvoiceUpdateView(generics.UpdateAPIView):
    serializer_class = InvoiceWriteSerializer

    def get_queryset(self):
        return Invoice.objects.filter(
            is_deleted=False,
            category__direction='in',
        )


@extend_schema(tags=['حسابداری — درآمد'], summary='حذف فاکتور درآمدی (soft delete)')
class IncomeInvoiceDeleteView(generics.DestroyAPIView):
    def get_queryset(self):
        return Invoice.objects.filter(is_deleted=False, category__direction='in')

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


def get_expense_category():
    category, _ = InvoiceCategory.objects.get_or_create(
        direction='out',
        defaults={'title': 'هزینه'},
    )
    return category


@extend_schema(tags=['حسابداری — هزینه'], summary='لیست فاکتورهای هزینه‌ای')
class ExpenseInvoiceListView(generics.ListAPIView):
    serializer_class = InvoiceListSerializer
    filterset_class = ExpenseInvoiceFilter

    def get_queryset(self):
        return Invoice.objects.filter(
            is_deleted=False,
            category__direction='out',
            is_payroll=False,
        ).select_related('account_side', 'category').order_by('-created_at')


@extend_schema(tags=['حسابداری — هزینه'], summary='جزئیات فاکتور هزینه‌ای')
class ExpenseInvoiceDetailView(generics.RetrieveAPIView):
    serializer_class = InvoiceDetailSerializer

    def get_queryset(self):
        return Invoice.objects.filter(
            is_deleted=False,
            category__direction='out',
        ).select_related('account_side', 'category').prefetch_related('items')


@extend_schema(tags=['حسابداری — هزینه'], summary='ثبت فاکتور هزینه‌ای')
class ExpenseInvoiceCreateView(generics.CreateAPIView):
    serializer_class = InvoiceWriteSerializer

    def perform_create(self, serializer):
        serializer.save(
            category=get_expense_category(),
            is_payroll=False,
        )


@extend_schema(tags=['حسابداری — هزینه'], summary='ویرایش فاکتور هزینه‌ای')
class ExpenseInvoiceUpdateView(generics.UpdateAPIView):
    serializer_class = InvoiceWriteSerializer

    def get_queryset(self):
        return Invoice.objects.filter(
            is_deleted=False,
            category__direction='out',
        )


@extend_schema(tags=['حسابداری — هزینه'], summary='حذف فاکتور هزینه‌ای (soft delete)')
class ExpenseInvoiceDeleteView(generics.DestroyAPIView):
    def get_queryset(self):
        return Invoice.objects.filter(is_deleted=False, category__direction='out')

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


@extend_schema(tags=['حسابداری — فیش حقوقی'], summary='لیست فیش‌های حقوقی')
class PayrollInvoiceListView(generics.ListAPIView):
    serializer_class = PayrollInvoiceListSerializer
    filterset_class = PayrollInvoiceFilter

    def get_queryset(self):
        return Invoice.objects.filter(
            is_deleted=False,
            is_payroll=True,
        ).select_related('account_side', 'payroll_detail').order_by('-created_at')


@extend_schema(tags=['حسابداری — فیش حقوقی'], summary='جزئیات فیش حقوقی')
class PayrollInvoiceDetailView(generics.RetrieveAPIView):
    serializer_class = PayrollInvoiceDetailSerializer

    def get_queryset(self):
        return Invoice.objects.filter(
            is_deleted=False,
            is_payroll=True,
        ).select_related('account_side', 'payroll_detail')


@extend_schema(tags=['حسابداری — فیش حقوقی'], summary='ثبت فیش حقوقی')
class PayrollInvoiceCreateView(generics.CreateAPIView):
    serializer_class = PayrollInvoiceWriteSerializer


@extend_schema(tags=['حسابداری — فیش حقوقی'], summary='ویرایش فیش حقوقی')
class PayrollInvoiceUpdateView(generics.UpdateAPIView):
    serializer_class = PayrollInvoiceWriteSerializer

    def get_queryset(self):
        return Invoice.objects.filter(is_deleted=False, is_payroll=True)


@extend_schema(tags=['حسابداری — فیش حقوقی'], summary='حذف فیش حقوقی (soft delete)')
class PayrollInvoiceDeleteView(generics.DestroyAPIView):
    def get_queryset(self):
        return Invoice.objects.filter(is_deleted=False, is_payroll=True)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


def get_purchase_category():
    category, _ = InvoiceCategory.objects.get_or_create(
        title='خرید',
        defaults={'direction': 'out'},
    )
    return category


@extend_schema(tags=['حسابداری — فاکتور خرید'], summary='لیست فاکتورهای خرید')
class PurchaseInvoiceListView(generics.ListAPIView):
    serializer_class = InvoiceListSerializer
    filterset_class = ExpenseInvoiceFilter

    def get_queryset(self):
        return Invoice.objects.filter(
            is_deleted=False,
            category__title='خرید',
        ).select_related('account_side', 'category').order_by('-created_at')


@extend_schema(tags=['حسابداری — فاکتور خرید'], summary='جزئیات فاکتور خرید')
class PurchaseInvoiceDetailView(generics.RetrieveAPIView):
    serializer_class = InvoiceDetailSerializer

    def get_queryset(self):
        return Invoice.objects.filter(
            is_deleted=False,
            category__title='خرید',
        ).select_related('account_side', 'category').prefetch_related('items')


@extend_schema(tags=['حسابداری — فاکتور خرید'], summary='ثبت فاکتور خرید')
class PurchaseInvoiceCreateView(generics.CreateAPIView):
    serializer_class = InvoiceWriteSerializer

    def perform_create(self, serializer):
        serializer.save(
            category=get_purchase_category(),
            is_payroll=False,
        )


@extend_schema(tags=['حسابداری — فاکتور خرید'], summary='ویرایش فاکتور خرید')
class PurchaseInvoiceUpdateView(generics.UpdateAPIView):
    serializer_class = InvoiceWriteSerializer

    def get_queryset(self):
        return Invoice.objects.filter(is_deleted=False, category__title='خرید')


@extend_schema(tags=['حسابداری — فاکتور خرید'], summary='حذف فاکتور خرید (soft delete)')
class PurchaseInvoiceDeleteView(generics.DestroyAPIView):
    def get_queryset(self):
        return Invoice.objects.filter(is_deleted=False, category__title='خرید')

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


def get_sales_category():
    category, _ = InvoiceCategory.objects.get_or_create(
        title='فروش',
        defaults={'direction': 'in'},
    )
    return category


@extend_schema(tags=['حسابداری — فاکتور فروش'], summary='لیست فاکتورهای فروش')
class SalesInvoiceListView(generics.ListAPIView):
    serializer_class = InvoiceListSerializer
    filterset_class = IncomeInvoiceFilter

    def get_queryset(self):
        return Invoice.objects.filter(
            is_deleted=False,
            category__title='فروش',
        ).select_related('account_side', 'category').order_by('-created_at')


@extend_schema(tags=['حسابداری — فاکتور فروش'], summary='جزئیات فاکتور فروش')
class SalesInvoiceDetailView(generics.RetrieveAPIView):
    serializer_class = InvoiceDetailSerializer

    def get_queryset(self):
        return Invoice.objects.filter(
            is_deleted=False,
            category__title='فروش',
        ).select_related('account_side', 'category').prefetch_related('items')


@extend_schema(tags=['حسابداری — فاکتور فروش'], summary='ثبت فاکتور فروش')
class SalesInvoiceCreateView(generics.CreateAPIView):
    serializer_class = InvoiceWriteSerializer

    def perform_create(self, serializer):
        serializer.save(
            category=get_sales_category(),
            is_payroll=False,
        )


@extend_schema(tags=['حسابداری — فاکتور فروش'], summary='ویرایش فاکتور فروش')
class SalesInvoiceUpdateView(generics.UpdateAPIView):
    serializer_class = InvoiceWriteSerializer

    def get_queryset(self):
        return Invoice.objects.filter(is_deleted=False, category__title='فروش')


@extend_schema(tags=['حسابداری — فاکتور فروش'], summary='حذف فاکتور فروش (soft delete)')
class SalesInvoiceDeleteView(generics.DestroyAPIView):
    def get_queryset(self):
        return Invoice.objects.filter(is_deleted=False, category__title='فروش')

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])
