import requests
from django.db.models import Q, Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated

from users.permissions import IsCustomer
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from DrGame import settings
from accounting.models import Invoice, Transaction, Wallet, WalletTransaction
from platform_settings.views import SoftDeleteViewMixin
from crm.models import Customer, B2BProfile, CustomerWishlist
from crm.serializers import (
    CustomerListSerializer,
    CustomerCreateUpdateSerializer,
    B2BProfileSerializer,
    CustomerSummarySerializer,
    CustomerInvoiceListSerializer,
    CustomerTransactionListSerializer,
    CustomerProfileSerializer,
    CustomerProfilePicSerializer,
    CustomerWishlistSerializer,
    CustomerWishlistWriteSerializer,
    WishlistToggleSerializer,
    CustomerWalletTransactionSerializer,
    WalletChargeSerializer,
    SendSmsSerializer,
)


# ─────────────────────────────────────────
# Customer List Views
# ─────────────────────────────────────────
@extend_schema(
    summary="لیست مشتریان عادی",
)
class CustomerListView(generics.ListAPIView):
    """List regular customers (without a B2B profile)"""

    serializer_class = CustomerListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__phone",
        "user__email",
        "address",
        "postal_code",
        "b2b_profile__business_title",
    ]

    def get_queryset(self):
        return (
            Customer.objects.filter(is_deleted=False)
            .exclude(b2b_profile__is_deleted=False)
            .select_related("user")
        )


@extend_schema(
    summary="لیست مشتریان تجاری",
)
class B2BCustomerListView(generics.ListAPIView):
    """List customers with an active B2B profile"""

    serializer_class = CustomerListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__phone",
        "user__email",
        "address",
        "postal_code",
        "b2b_profile__business_title",
    ]

    def get_queryset(self):
        return Customer.objects.filter(
            is_deleted=False, b2b_profile__is_deleted=False
        ).select_related("user", "b2b_profile")


# ─────────────────────────────────────────
# Customer CRUD
# ─────────────────────────────────────────
@extend_schema(
    summary="افزودن مشتریان عادی",
)
class CustomerCreateView(generics.CreateAPIView):
    """Create a new customer"""

    serializer_class = CustomerCreateUpdateSerializer
    queryset = Customer.objects.filter(is_deleted=False)


@extend_schema(
    summary="جزعیات، حذف و ویرایش مشتریان عادی",
)
class CustomerRetrieveUpdateDestroyView(
    SoftDeleteViewMixin, generics.RetrieveUpdateDestroyAPIView
):
    """Retrieve, edit and soft-delete a customer"""

    serializer_class = CustomerCreateUpdateSerializer

    def get_queryset(self):
        return Customer.objects.filter(is_deleted=False).select_related("user")


# ─────────────────────────────────────────
# B2B Profile CRUD
# ─────────────────────────────────────────
@extend_schema(
    summary="افزودن مشتریان تجاری",
)
class B2BProfileCreateView(generics.CreateAPIView):
    """Create a B2B profile for a customer"""

    serializer_class = B2BProfileSerializer

    def perform_create(self, serializer):
        customer = get_object_or_404(
            Customer, pk=self.kwargs["customer_id"], is_deleted=False
        )
        serializer.save(customer=customer)


@extend_schema(
    summary="جزعیات، حذف و ویرایش مشتریان تجاری",
)
class B2BProfileRetrieveUpdateDestroyView(
    SoftDeleteViewMixin, generics.RetrieveUpdateDestroyAPIView
):
    """Retrieve, edit and soft-delete a B2B profile — by customer_id"""

    serializer_class = B2BProfileSerializer

    def get_object(self):
        return get_object_or_404(
            B2BProfile, customer_id=self.kwargs["customer_id"], is_deleted=False
        )


# ─────────────────────────────────────────
# Customer Report Stats
# ─────────────────────────────────────────
@extend_schema(
    summary="لیست تراکنش‌های مشتری",
)
class CustomerTransactionListView(generics.ListAPIView):
    serializer_class = CustomerTransactionListSerializer

    def get_queryset(self):
        customer = get_object_or_404(
            Customer, pk=self.kwargs["customer_id"], is_deleted=False
        )
        return (
            Transaction.objects.filter(
                account_side__object_id=customer.id,
                account_side__content_type__model="customer",
                is_deleted=False,
            )
            .select_related("bank_account", "invoice", "account_side")
            .order_by("-created_at")
        )


@extend_schema(
    summary="لیست فاکتورهای مشتری",
)
class CustomerInvoiceListView(generics.ListAPIView):
    serializer_class = CustomerInvoiceListSerializer

    def get_queryset(self):
        customer = get_object_or_404(
            Customer, pk=self.kwargs["customer_id"], is_deleted=False
        )
        return (
            Invoice.objects.filter(
                Q(product_orders__customer=customer, product_orders__is_deleted=False)
                | Q(repair_orders__customer=customer, repair_orders__is_deleted=False)
                | Q(
                    sony_account_orders__customer=customer,
                    sony_account_orders__is_deleted=False,
                ),
                is_deleted=False,
            )
            .distinct()
            .prefetch_related("items", "transactions")
            .order_by("-created_at")
        )


@extend_schema(
    summary="خلاصه سفارشات و مالی مشتری",
)
class CustomerSummaryView(generics.GenericAPIView):
    serializer_class = CustomerSummarySerializer

    def get(self, request, customer_id):
        customer = get_object_or_404(Customer, pk=customer_id, is_deleted=False)

        product_orders_count = customer.product_orders.filter(is_deleted=False).count()
        repair_orders_count = customer.repair_orders.filter(is_deleted=False).count()
        sony_account_orders_count = customer.sony_account_orders.filter(
            is_deleted=False
        ).count()

        total_transactions_amount = (
            Transaction.objects.filter(
                account_side__object_id=customer.id,
                account_side__content_type__model="customer",
                is_deleted=False,
                direction="in",
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        invoices = (
            Invoice.objects.filter(
                Q(product_orders__customer=customer, product_orders__is_deleted=False)
                | Q(repair_orders__customer=customer, repair_orders__is_deleted=False)
                | Q(
                    sony_account_orders__customer=customer,
                    sony_account_orders__is_deleted=False,
                ),
                is_deleted=False,
            )
            .distinct()
            .prefetch_related("items")
        )

        total_invoices_amount = sum(
            sum(item.total_price for item in inv.items.filter(is_deleted=False))
            for inv in invoices
        )

        data = {
            "customer_id": customer.id,
            "full_name": customer.user.full_name(),
            "product_orders_count": product_orders_count,
            "repair_orders_count": repair_orders_count,
            "sony_account_orders_count": sony_account_orders_count,
            "total_orders_count": product_orders_count
            + repair_orders_count
            + sony_account_orders_count,
            "total_transactions_amount": total_transactions_amount,
            "total_invoices_amount": total_invoices_amount,
        }

        serializer = self.get_serializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ─────────────────────────────────────────
# SMS Services
# ─────────────────────────────────────────
@extend_schema(
    summary="ارسال اس ام اس",
)
class CustomerSendSmsService(generics.GenericAPIView):
    serializer_class = SendSmsSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        message = data["message"]
        customer_ids = data["customer_ids"]
        send_time = data.get("send_time")

        # Collect phone numbers from customers
        recipients = []
        customers = Customer.objects.filter(id__in=customer_ids).select_related("user")
        for customer in customers:
            if customer.user and customer.user.phone:
                recipients.append(customer.user.phone)

        if not recipients:
            return Response(
                {"detail": "No number found to send to."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Build the body for IPPanel
        body = {
            "sending_type": "webservice",
            "from_number": "+983000505",  # sender number
            "message": message,
            "params": {"recipients": recipients},
        }
        if send_time:
            body["send_time"] = send_time.strftime("%Y-%m-%d %H:%M:%S")

        # Send request to IPPanel
        headers = {
            "Authorization": f"{settings.FARAZ_API_KEY}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            "https://edge.ippanel.com/v1/api/send", json=body, headers=headers
        )

        if response.status_code == 200:
            return Response(response.json(), status=status.HTTP_200_OK)
        return Response(
            {"detail": "Error sending SMS", "response": response.text},
            status=response.status_code,
        )


# ==================== Customer Profile ====================


class CustomerProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = CustomerProfileSerializer

    def get_object(self):
        return self.request.user.customer


class CustomerProfilePicView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = CustomerProfilePicSerializer

    def post(self, request, *args, **kwargs):
        customer = request.user.customer
        serializer = self.get_serializer(customer, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


# ==================== Wishlist ====================


class CustomerWishlistListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = CustomerWishlistSerializer

    def get_queryset(self):
        return CustomerWishlist.objects.filter(
            customer=self.request.user.customer, is_deleted=False
        ).order_by("-created_at")


class CustomerWishlistAddView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = CustomerWishlistWriteSerializer

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer)


class CustomerWishlistRemoveView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_queryset(self):
        return CustomerWishlist.objects.filter(
            customer=self.request.user.customer, is_deleted=False
        )


class CustomerWishlistToggleView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = WishlistToggleSerializer

    def post(self, request, *args, **kwargs):
        customer = request.user.customer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        from django.contrib.contenttypes.models import ContentType

        object_type = data["object_type"]
        object_id = data["object_id"]

        content_type_map = {
            "product": ContentType.objects.get(app_label="inventory", model="product"),
            "game": ContentType.objects.get(app_label="website", model="game"),
        }
        ct = content_type_map.get(object_type)
        if not ct:
            return Response(
                {"detail": "Invalid type"}, status=status.HTTP_400_BAD_REQUEST
            )

        wishlist_item, created = CustomerWishlist.objects.get_or_create(
            customer=customer,
            content_type=ct,
            object_id=object_id,
            defaults={"is_deleted": False},
        )

        if not created:
            wishlist_item.is_deleted = not wishlist_item.is_deleted
            wishlist_item.save()

        return Response(
            {"is_in_wishlist": not wishlist_item.is_deleted}, status=status.HTTP_200_OK
        )


# ==================== Customer Wallet ====================


class CustomerWalletView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def get(self, request, *args, **kwargs):
        try:
            wallet = request.user.wallet
        except Wallet.DoesNotExist:
            return Response({"balance": 0, "transactions": []})
        last_transactions = wallet.transactions.filter(
            is_deleted=False, status="success"
        ).order_by("-created_at")[:5]
        from crm.serializers import CustomerWalletTransactionSerializer

        return Response(
            {
                "balance": wallet.balance,
                "is_active": wallet.is_active,
                "transactions": CustomerWalletTransactionSerializer(
                    last_transactions, many=True
                ).data,
            }
        )


class CustomerWalletTransactionsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_serializer_class(self):
        from crm.serializers import CustomerWalletTransactionSerializer

        return CustomerWalletTransactionSerializer

    def get_queryset(self):
        try:
            wallet = self.request.user.wallet
            return wallet.transactions.filter(is_deleted=False).order_by("-created_at")
        except Wallet.DoesNotExist:
            return WalletTransaction.objects.none()


class CustomerWalletChargeView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = WalletChargeSerializer

    def post(self, request, *args, **kwargs):
        customer = request.user.customer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data["amount"]

        wallet, _ = Wallet.objects.get_or_create(user=request.user)

        from accounting.services import WalletService

        txn = WalletService.charge(
            wallet=wallet,
            amount=amount,
            type_="charge_gateway",
            description="Online top-up (simulated)",
        )

        from crm.serializers import CustomerWalletTransactionSerializer

        return Response(
            {
                "detail": "Wallet charged successfully",
                "transaction": CustomerWalletTransactionSerializer(txn).data,
            },
            status=status.HTTP_200_OK,
        )
