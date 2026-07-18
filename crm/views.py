import requests
from django.db.models import Q, Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from DrGame import settings
from accounting.models import Invoice, Transaction
from platform_settings.views import SoftDeleteViewMixin
from crm.models import Customer, B2BProfile
from crm.serializers import (
    CustomerListSerializer,
    CustomerCreateUpdateSerializer,
    B2BProfileSerializer, CustomerSummarySerializer, CustomerInvoiceListSerializer, CustomerTransactionListSerializer,
    SendSmsSerializer,
)


# ─────────────────────────────────────────
# Customer List Views
# ─────────────────────────────────────────
@extend_schema(tags=['باشگاه مشتریان - لیست مشتریان'],
               summary='لیست مشتریان عادی', )
class CustomerListView(generics.ListAPIView):
    """لیست مشتری‌های معمولی (بدون پروفایل B2B)"""
    serializer_class = CustomerListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = [
        'user__first_name',
        'user__last_name',
        'user__phone',
        'user__email',
        'address',
        'postal_code',
        'b2b_profile__business_title',
    ]

    def get_queryset(self):
        return (
            Customer.objects
            .filter(is_deleted=False)
            .exclude(b2b_profile__is_deleted=False)
            .select_related('user')
        )


@extend_schema(tags=['باشگاه مشتریان - لیست مشتریان'],
               summary='لیست مشتریان تجاری', )
class B2BCustomerListView(generics.ListAPIView):
    """لیست مشتری‌هایی که پروفایل B2B فعال دارن"""
    serializer_class = CustomerListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = [
        'user__first_name',
        'user__last_name',
        'user__phone',
        'user__email',
        'address',
        'postal_code',
        'b2b_profile__business_title',
    ]

    def get_queryset(self):
        return (
            Customer.objects
            .filter(is_deleted=False, b2b_profile__is_deleted=False)
            .select_related('user', 'b2b_profile')
        )


# ─────────────────────────────────────────
# Customer CRUD
# ─────────────────────────────────────────
@extend_schema(tags=['باشگاه مشتریان - کراد مشتریان'],
               summary='افزودن مشتریان عادی', )
class CustomerCreateView(generics.CreateAPIView):
    """ایجاد مشتری جدید"""
    serializer_class = CustomerCreateUpdateSerializer
    queryset = Customer.objects.filter(is_deleted=False)


@extend_schema(tags=['باشگاه مشتریان - کراد مشتریان'],
               summary='جزعیات، حذف و ویرایش مشتریان عادی', )
class CustomerRetrieveUpdateDestroyView(SoftDeleteViewMixin, generics.RetrieveUpdateDestroyAPIView):
    """دریافت، ویرایش و حذف نرم مشتری"""
    serializer_class = CustomerCreateUpdateSerializer

    def get_queryset(self):
        return Customer.objects.filter(is_deleted=False).select_related('user')


# ─────────────────────────────────────────
# B2B Profile CRUD
# ─────────────────────────────────────────
@extend_schema(tags=['باشگاه مشتریان - کراد پروفایل مشرتیان تجاری'],
               summary='افزودن مشتریان تجاری', )
class B2BProfileCreateView(generics.CreateAPIView):
    """ایجاد پروفایل B2B برای مشتری"""
    serializer_class = B2BProfileSerializer

    def perform_create(self, serializer):
        customer = get_object_or_404(Customer, pk=self.kwargs['customer_id'], is_deleted=False)
        serializer.save(customer=customer)


@extend_schema(tags=['باشگاه مشتریان - کراد پروفایل مشتریان تجاری'],
               summary='جزعیات، حذف و ویرایش مشتریان تجاری', )
class B2BProfileRetrieveUpdateDestroyView(SoftDeleteViewMixin, generics.RetrieveUpdateDestroyAPIView):
    """دریافت، ویرایش و حذف نرم پروفایل B2B — با customer_id"""
    serializer_class = B2BProfileSerializer

    def get_object(self):
        return get_object_or_404(
            B2BProfile,
            customer_id=self.kwargs['customer_id'],
            is_deleted=False
        )


# ─────────────────────────────────────────
# Customer Report Stats
# ─────────────────────────────────────────
@extend_schema(tags=['باشگاه مشتریان - جزعیات'],
               summary='لیست تراکنش‌های مشتری', )
class CustomerTransactionListView(generics.ListAPIView):
    serializer_class = CustomerTransactionListSerializer

    def get_queryset(self):
        customer = get_object_or_404(Customer, pk=self.kwargs['customer_id'], is_deleted=False)
        return (
            Transaction.objects
            .filter(
                account_side__object_id=customer.id,
                account_side__content_type__model='customer',
                is_deleted=False,
            )
            .select_related('bank_account', 'invoice', 'account_side')
            .order_by('-created_at')
        )


@extend_schema(tags=['باشگاه مشتریان - جزعیات'],
               summary='لیست فاکتورهای مشتری', )
class CustomerInvoiceListView(generics.ListAPIView):
    serializer_class = CustomerInvoiceListSerializer

    def get_queryset(self):
        customer = get_object_or_404(Customer, pk=self.kwargs['customer_id'], is_deleted=False)
        return (
            Invoice.objects
            .filter(
                Q(product_orders__customer=customer, product_orders__is_deleted=False) |
                Q(repair_orders__customer=customer, repair_orders__is_deleted=False) |
                Q(sony_account_orders__customer=customer, sony_account_orders__is_deleted=False),
                is_deleted=False,
            )
            .distinct()
            .prefetch_related('items', 'transactions')
            .order_by('-created_at')
        )


@extend_schema(tags=['باشگاه مشتریان - جزعیات'],
               summary='خلاصه سفارشات و مالی مشتری', )
class CustomerSummaryView(generics.GenericAPIView):
    serializer_class = CustomerSummarySerializer

    def get(self, request, customer_id):
        customer = get_object_or_404(Customer, pk=customer_id, is_deleted=False)

        product_orders_count = customer.product_orders.filter(is_deleted=False).count()
        repair_orders_count = customer.repair_orders.filter(is_deleted=False).count()
        sony_account_orders_count = customer.sony_account_orders.filter(is_deleted=False).count()

        total_transactions_amount = (
                Transaction.objects
                .filter(
                    account_side__object_id=customer.id,
                    account_side__content_type__model='customer',
                    is_deleted=False,
                    direction='in',
                )
                .aggregate(total=Sum('amount'))['total'] or 0
        )

        invoices = Invoice.objects.filter(
            Q(product_orders__customer=customer, product_orders__is_deleted=False) |
            Q(repair_orders__customer=customer, repair_orders__is_deleted=False) |
            Q(sony_account_orders__customer=customer, sony_account_orders__is_deleted=False),
            is_deleted=False,
        ).distinct().prefetch_related('items')

        total_invoices_amount = sum(
            sum(item.total_price for item in inv.items.filter(is_deleted=False))
            for inv in invoices
        )

        data = {
            'customer_id': customer.id,
            'full_name': customer.user.full_name(),
            'product_orders_count': product_orders_count,
            'repair_orders_count': repair_orders_count,
            'sony_account_orders_count': sony_account_orders_count,
            'total_orders_count': product_orders_count + repair_orders_count + sony_account_orders_count,
            'total_transactions_amount': total_transactions_amount,
            'total_invoices_amount': total_invoices_amount,
        }

        serializer = self.get_serializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ─────────────────────────────────────────
# SMS Services
# ─────────────────────────────────────────
@extend_schema(tags=['باشگاه مشتریان - سرویس SMS'],
               summary='ارسال اس ام اس', )
class CustomerSendSmsService(generics.GenericAPIView):
    serializer_class = SendSmsSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        message = data['message']
        customer_ids = data['customer_ids']
        send_time = data.get('send_time')

        # گرفتن شماره‌ها از مشتریان
        recipients = []
        customers = Customer.objects.filter(id__in=customer_ids).select_related('user')
        for customer in customers:
            if customer.user and customer.user.phone:
                recipients.append(customer.user.phone)

        if not recipients:
            return Response({"detail": "هیچ شماره‌ای برای ارسال یافت نشد."},
                            status=status.HTTP_400_BAD_REQUEST)

        # ساخت بادی برای IPPanel
        body = {
            "sending_type": "webservice",
            "from_number": "+983000505",  # شماره فرستنده
            "message": message,
            "params": {
                "recipients": recipients
            }
        }
        if send_time:
            body["send_time"] = send_time.strftime("%Y-%m-%d %H:%M:%S")

        # ارسال درخواست به IPPanel
        headers = {
            "Authorization": f"{settings.FARAZ_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post("https://edge.ippanel.com/v1/api/send",
                                 json=body, headers=headers)

        if response.status_code == 200:
            return Response(response.json(), status=status.HTTP_200_OK)
        return Response({"detail": "خطا در ارسال پیامک", "response": response.text},
                        status=response.status_code)
