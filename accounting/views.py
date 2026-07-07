from django.contrib.contenttypes.models import ContentType
from django.db.models import Prefetch
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounting.filters import (
    DailyInvoiceFilter, DailyTransactionFilter,
    InvoiceFilter, TransactionFilter, PayableReceivableFilter,
)
from accounting.models import (
    BankAccount, AccountSide, InvoiceCategory, Invoice,
    InvoiceItem, Transaction,
)
from accounting.serializers import (
    InvoiceSerializer, TransactionSerializer,
    IssueCustomerInvoiceSerializer, IssueSupplierInvoiceSerializer,
    PayCustomerTransactionSerializer, PaySupplierTransactionSerializer,
    InvoiceCategoryChoiceSerializer, BankAccountChoiceSerializer,
    AccountSideChoiceSerializer,
)


def _invoice_queryset():
    return Invoice.objects.filter(is_deleted=False).select_related(
        'account_side', 'category',
    ).prefetch_related(
        Prefetch('items', queryset=InvoiceItem.objects.filter(is_deleted=False)),
    ).order_by('-created_at')


def _transaction_queryset():
    return Transaction.objects.filter(is_deleted=False).select_related(
        'invoice', 'account_side', 'bank_account',
    ).order_by('-created_at')


# ─── 1. Daily Ledger ────────────────────────────────────────────────────────

@extend_schema(
    tags=["Accounting"],
    summary="دفتر روزانه — فاکتورها",
    description="لیست فاکتورهای امروز. برای تغییر تاریخ از پارامتر date استفاده کنید.",
    parameters=[
        OpenApiParameter("date", OpenApiTypes.DATE, description="تاریخ (پیش‌فرض: امروز)"),
        OpenApiParameter("search", OpenApiTypes.STR, description="جستجو در توضیحات"),
    ],
)
class DailyInvoiceListView(generics.ListAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = DailyInvoiceFilter
    search_fields = ['description', 'account_side__name']

    def get_queryset(self):
        qs = _invoice_queryset()
        if 'date' not in self.request.query_params:
            qs = qs.filter(created_at__date=timezone.localdate())
        return qs


@extend_schema(
    tags=["Accounting"],
    summary="دفتر روزانه — تراکنش‌ها",
    description="لیست تراکنش‌های امروز. برای تغییر تاریخ از پارامتر date استفاده کنید.",
    parameters=[
        OpenApiParameter("date", OpenApiTypes.DATE, description="تاریخ (پیش‌فرض: امروز)"),
        OpenApiParameter("search", OpenApiTypes.STR, description="جستجو در توضیحات"),
    ],
)
class DailyTransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = DailyTransactionFilter
    search_fields = ['description', 'account_side__name']

    def get_queryset(self):
        qs = _transaction_queryset()
        if 'date' not in self.request.query_params:
            qs = qs.filter(created_at__date=timezone.localdate())
        return qs


# ─── 2 & 3. Payments / Receipts ─────────────────────────────────────────────

@extend_schema(
    tags=["Accounting"],
    summary="لیست پرداخت‌ها",
    description="تراکنش‌هایی با جهت خروجی (direction=out).",
    parameters=[
        OpenApiParameter("date_from", OpenApiTypes.DATE, description="از تاریخ"),
        OpenApiParameter("date_to", OpenApiTypes.DATE, description="تا تاریخ"),
        OpenApiParameter("account_side", OpenApiTypes.INT, description="شناسه طرف حساب"),
        OpenApiParameter("bank_account", OpenApiTypes.INT, description="شناسه حساب بانکی"),
        OpenApiParameter("invoice", OpenApiTypes.INT, description="شناسه فاکتور"),
        OpenApiParameter("amount_min", OpenApiTypes.INT, description="حداقل مبلغ"),
        OpenApiParameter("amount_max", OpenApiTypes.INT, description="حداکثر مبلغ"),
        OpenApiParameter("search", OpenApiTypes.STR, description="جستجو در توضیحات"),
    ],
)
class PaymentListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = TransactionFilter
    search_fields = ['description', 'account_side__name']

    def get_queryset(self):
        return _transaction_queryset().filter(direction='out')


@extend_schema(
    tags=["Accounting"],
    summary="لیست دریافت‌ها",
    description="تراکنش‌هایی با جهت ورودی (direction=in).",
    parameters=[
        OpenApiParameter("date_from", OpenApiTypes.DATE, description="از تاریخ"),
        OpenApiParameter("date_to", OpenApiTypes.DATE, description="تا تاریخ"),
        OpenApiParameter("account_side", OpenApiTypes.INT, description="شناسه طرف حساب"),
        OpenApiParameter("bank_account", OpenApiTypes.INT, description="شناسه حساب بانکی"),
        OpenApiParameter("invoice", OpenApiTypes.INT, description="شناسه فاکتور"),
        OpenApiParameter("amount_min", OpenApiTypes.INT, description="حداقل مبلغ"),
        OpenApiParameter("amount_max", OpenApiTypes.INT, description="حداکثر مبلغ"),
        OpenApiParameter("search", OpenApiTypes.STR, description="جستجو در توضیحات"),
    ],
)
class ReceiptListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = TransactionFilter
    search_fields = ['description', 'account_side__name']

    def get_queryset(self):
        return _transaction_queryset().filter(direction='in')


# ─── 4 & 5. Payable / Receivable ────────────────────────────────────────────

@extend_schema(
    tags=["Accounting"],
    summary="حساب‌های پرداختنی",
    description="فاکتورهای خروجی که هنوز کامل پرداخت نشده‌اند.",
    parameters=[
        OpenApiParameter("date_from", OpenApiTypes.DATE, description="از تاریخ"),
        OpenApiParameter("date_to", OpenApiTypes.DATE, description="تا تاریخ"),
        OpenApiParameter("account_side", OpenApiTypes.INT, description="شناسه طرف حساب"),
        OpenApiParameter("category", OpenApiTypes.INT, description="شناسه دسته‌بندی"),
        OpenApiParameter("payment_status", OpenApiTypes.STR, description="وضعیت پرداخت: unpaid | partial"),
        OpenApiParameter("search", OpenApiTypes.STR, description="جستجو در توضیحات"),
    ],
)
class PayableListView(generics.ListAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = PayableReceivableFilter
    search_fields = ['description', 'account_side__name']

    def get_queryset(self):
        return _invoice_queryset().filter(
            category__direction='out',
            payment_status__in=['unpaid', 'partial'],
        )


@extend_schema(
    tags=["Accounting"],
    summary="حساب‌های دریافتنی",
    description="فاکتورهای ورودی که هنوز کامل دریافت نشده‌اند.",
    parameters=[
        OpenApiParameter("date_from", OpenApiTypes.DATE, description="از تاریخ"),
        OpenApiParameter("date_to", OpenApiTypes.DATE, description="تا تاریخ"),
        OpenApiParameter("account_side", OpenApiTypes.INT, description="شناسه طرف حساب"),
        OpenApiParameter("category", OpenApiTypes.INT, description="شناسه دسته‌بندی"),
        OpenApiParameter("payment_status", OpenApiTypes.STR, description="وضعیت پرداخت: unpaid | partial"),
        OpenApiParameter("search", OpenApiTypes.STR, description="جستجو در توضیحات"),
    ],
)
class ReceivableListView(generics.ListAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = PayableReceivableFilter
    search_fields = ['description', 'account_side__name']

    def get_queryset(self):
        return _invoice_queryset().filter(
            category__direction='in',
            payment_status__in=['unpaid', 'partial'],
        )


# ─── 6. Invoice CRUD ────────────────────────────────────────────────────────

@extend_schema(
    tags=["Accounting"],
    summary="لیست و ایجاد فاکتور",
    description="لیست تمام فاکتورها با امکان فیلتر و جستجو. POST برای ایجاد فاکتور جدید.",
    parameters=[
        OpenApiParameter("date_from", OpenApiTypes.DATE, description="از تاریخ"),
        OpenApiParameter("date_to", OpenApiTypes.DATE, description="تا تاریخ"),
        OpenApiParameter("status", OpenApiTypes.STR, description="وضعیت: draft | primary | finalize"),
        OpenApiParameter("payment_status", OpenApiTypes.STR, description="وضعیت پرداخت: unpaid | partial | paid"),
        OpenApiParameter("is_payroll", OpenApiTypes.BOOL, description="فیش حقوقی؟"),
        OpenApiParameter("category", OpenApiTypes.INT, description="شناسه دسته‌بندی"),
        OpenApiParameter("account_side", OpenApiTypes.INT, description="شناسه طرف حساب"),
        OpenApiParameter("direction", OpenApiTypes.STR, description="جهت دسته‌بندی: in | out"),
        OpenApiParameter("amount_min", OpenApiTypes.INT, description="حداقل مبلغ"),
        OpenApiParameter("amount_max", OpenApiTypes.INT, description="حداکثر مبلغ"),
        OpenApiParameter("search", OpenApiTypes.STR, description="جستجو در توضیحات"),
    ],
)
class InvoiceListCreateView(generics.ListCreateAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = InvoiceFilter
    search_fields = ['description', 'account_side__name']

    def get_queryset(self):
        return _invoice_queryset()


@extend_schema(
    tags=["Accounting"],
    summary="جزئیات، ویرایش و حذف فاکتور",
    description="GET: جزئیات فاکتور. PUT/PATCH: ویرایش. DELETE: حذف نرم.",
)
class InvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return _invoice_queryset()

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


# ─── 7. Transaction CRUD ────────────────────────────────────────────────────

@extend_schema(
    tags=["Accounting"],
    summary="لیست و ایجاد تراکنش",
    description="لیست تمام تراکنش‌ها با امکان فیلتر و جستجو. POST برای ایجاد تراکنش جدید.",
    parameters=[
        OpenApiParameter("date_from", OpenApiTypes.DATE, description="از تاریخ"),
        OpenApiParameter("date_to", OpenApiTypes.DATE, description="تا تاریخ"),
        OpenApiParameter("account_side", OpenApiTypes.INT, description="شناسه طرف حساب"),
        OpenApiParameter("bank_account", OpenApiTypes.INT, description="شناسه حساب بانکی"),
        OpenApiParameter("invoice", OpenApiTypes.INT, description="شناسه فاکتور"),
        OpenApiParameter("amount_min", OpenApiTypes.INT, description="حداقل مبلغ"),
        OpenApiParameter("amount_max", OpenApiTypes.INT, description="حداکثر مبلغ"),
        OpenApiParameter("search", OpenApiTypes.STR, description="جستجو در توضیحات"),
    ],
)
class TransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = TransactionFilter
    search_fields = ['description', 'account_side__name']

    def get_queryset(self):
        return _transaction_queryset()


@extend_schema(
    tags=["Accounting"],
    summary="جزئیات، ویرایش و حذف تراکنش",
    description="GET: جزئیات تراکنش. PUT/PATCH: ویرایش. DELETE: حذف نرم.",
)
class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return _transaction_queryset()

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


# ─── 8. Issue Customer Invoice ──────────────────────────────────────────────

@extend_schema(
    tags=["Accounting"],
    summary="صدور فاکتور برای مشتری",
    description=(
            "فاکتور خروجی با آیتم‌ها ایجاد می‌کند. "
            "دسته‌بندی باید direction=out باشد."
    ),
    request=IssueCustomerInvoiceSerializer,
    responses={201: InvoiceSerializer},
)
class IssueCustomerInvoiceView(generics.CreateAPIView):
    serializer_class = IssueCustomerInvoiceSerializer
    permission_classes = [IsAuthenticated]


# ─── 9. Issue Supplier Invoice ──────────────────────────────────────────────

@extend_schema(
    tags=["Accounting"],
    summary="صدور فاکتور خرید از تامین‌کننده",
    description=(
            "فاکتور ورودی با آیتم‌ها ایجاد می‌کند. "
            "دسته‌بندی باید direction=in و طرف حساب باید supplier باشد."
    ),
    request=IssueSupplierInvoiceSerializer,
    responses={201: InvoiceSerializer},
)
class IssueSupplierInvoiceView(generics.CreateAPIView):
    serializer_class = IssueSupplierInvoiceSerializer
    permission_classes = [IsAuthenticated]


# ─── 10. Pay Customer ───────────────────────────────────────────────────────

@extend_schema(
    tags=["Accounting"],
    summary="صدور پرداخت به مشتری",
    description=(
            "تراکنش خروجی برای مشتری ایجاد می‌کند. "
            "طرف حساب باید type=customer باشد."
    ),
    request=PayCustomerTransactionSerializer,
    responses={201: TransactionSerializer},
)
class PayCustomerView(generics.CreateAPIView):
    serializer_class = PayCustomerTransactionSerializer
    permission_classes = [IsAuthenticated]


# ─── 11. Pay Supplier ───────────────────────────────────────────────────────

@extend_schema(
    tags=["Accounting"],
    summary="صدور پرداخت به تامین‌کننده",
    description=(
            "تراکنش خروجی برای تامین‌کننده ایجاد می‌کند. "
            "طرف حساب باید type=supplier باشد."
    ),
    request=PaySupplierTransactionSerializer,
    responses={201: TransactionSerializer},
)
class PaySupplierView(generics.CreateAPIView):
    serializer_class = PaySupplierTransactionSerializer
    permission_classes = [IsAuthenticated]


# ─── 12. Choices Endpoints ──────────────────────────────────────────────────

@extend_schema(
    tags=["Accounting"],
    summary="لیست دسته‌بندی فاکتورها",
    description="برای dropdown فرانت‌اند.",
    responses={200: InvoiceCategoryChoiceSerializer(many=True)},
)
class InvoiceCategoryChoicesView(generics.ListAPIView):
    serializer_class = InvoiceCategoryChoiceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return InvoiceCategory.objects.filter(is_deleted=False)


@extend_schema(
    tags=["Accounting"],
    summary="لیست حساب‌های بانکی",
    description="برای dropdown فرانت‌اند.",
    responses={200: BankAccountChoiceSerializer(many=True)},
)
class BankAccountChoicesView(generics.ListAPIView):
    serializer_class = BankAccountChoiceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return BankAccount.objects.filter(is_deleted=False)


@extend_schema(
    tags=["Accounting"],
    summary="لیست طرف حساب‌ها",
    description="برای dropdown فرانت‌اند.",
    responses={200: AccountSideChoiceSerializer(many=True)},
)
class AccountSideChoicesView(generics.ListAPIView):
    serializer_class = AccountSideChoiceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return AccountSide.objects.filter(is_deleted=False)


@extend_schema(
    tags=["Accounting"],
    summary="وضعیت‌های فاکتور",
    description="لیست ثابت وضعیت‌های فاکتور.",
)
class InvoiceStatusChoicesView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        choices = [{'value': k, 'label': v} for k, v in Invoice.STATUS_CHOICES]
        return Response(choices)


@extend_schema(
    tags=["Accounting"],
    summary="وضعیت‌های پرداخت",
    description="لیست ثابت وضعیت‌های پرداخت فاکتور.",
)
class PaymentStatusChoicesView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        choices = [{'value': k, 'label': v} for k, v in Invoice.PAYMENT_STATUS_CHOICES]
        return Response(choices)


@extend_schema(
    tags=["Accounting"],
    summary="جهت تراکنش‌ها",
    description="لیست ثابت جهت تراکنش‌ها.",
)
class TransactionDirectionChoicesView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        choices = [{'value': k, 'label': v} for k, v in Transaction.DIRECTION_CHOICES]
        return Response(choices)


@extend_schema(
    tags=["Accounting"],
    summary="انواع محتوا برای آیتم فاکتور",
    description="لیست content type هایی که می‌توانند به آیتم فاکتور وصل شوند.",
)
class ContentTypeChoicesView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        linkable_models = [
            ('orders', 'sonyaccountorder'),
            ('orders', 'repairorder'),
            ('orders', 'productorder'),
        ]
        result = []
        for app_label, model in linkable_models:
            try:
                ct = ContentType.objects.get(app_label=app_label, model=model)
                result.append({'id': ct.id, 'app_label': ct.app_label, 'model': ct.model})
            except ContentType.DoesNotExist:
                pass
        return Response(result)
