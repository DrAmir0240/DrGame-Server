import requests
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from DrGame import settings
from accounting.serializers import BalanceSerializer, CustomerDepositSerializer
from users.auth import CustomJWTAuthentication
from users.permissions import IsCustomer, IsEmployee, IsMainManager
from .models import Customer
from .serializers import (
    CustomerProfileSerializer,
    OrderSerializer,
    GameOrderSerializer,
    RepairOrderSerializer,
    TransactionSerializer, CustomerProfileCreateSerializer, CourseOrderSerializer, EmployeeCustomerSerializer,
    SendSmsSerializer
)

from accounting.models import Order, GameOrder, RepairOrder, Transaction, CourseOrder, PaymentMethod
from django.db.models import Q


class CustomerProfileCreateAPIView(generics.CreateAPIView):
    serializer_class = CustomerProfileCreateSerializer
    queryset = Customer.objects.select_related('user').filter(is_deleted=False).all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]


class CustomerProfileRetrieveAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]
    serializer_class = CustomerProfileSerializer

    def get_object(self):
        customer, created = Customer.objects.get_or_create(
            user=self.request.user,
            defaults={'full_name': ''}  # می‌تونی مقادیر اولیه هم بدی
        )
        return customer


class CustomerOrderListAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        return Order.objects.filter(customer=customer, is_deleted=False)


class CustomerOrderRetrieveAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        return Order.objects.filter(customer=customer, is_deleted=False)


class CustomerGameOrderListAPIView(generics.ListAPIView):
    serializer_class = GameOrderSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        return GameOrder.objects.filter(customer=customer, is_deleted=False)


class CustomerGameOrderRetrieveAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = GameOrderSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        return GameOrder.objects.select_related('customer').filter(customer=customer,
                                                                   is_deleted=False)


class CustomerRepairOrderListAPIView(generics.ListAPIView):
    serializer_class = RepairOrderSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        return RepairOrder.objects.select_related('customer').filter(customer=customer,
                                                                     is_deleted=False)


class CustomerRepairOrderRetrieveAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = RepairOrderSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        return RepairOrder.objects.select_related('customer').filter(customer=customer,
                                                                     is_deleted=False)


class CustomerCourseOrderListAPIView(generics.ListAPIView):
    serializer_class = CourseOrderSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        return CourseOrder.objects.select_related('customer').filter(customer=customer,
                                                                     is_deleted=False).all()


class CustomerCourseOrderRetrieveAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = CourseOrderSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        return CourseOrder.objects.select_related('customer').filter(customer=customer,
                                                                     is_deleted=False).all()


class CustomerSelfBalance(generics.GenericAPIView):
    serializer_class = BalanceSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, *args, **kwargs):
        # مقدار اولیه
        balance = 0
        # اگر کاربر دارای رابطه employee است
        if hasattr(request.user, 'customer') and request.user.customer:
            balance = request.user.customer.balance or 0
        # Serialize و برگرداندن Response
        serializer = self.get_serializer({'balance': balance})
        return Response(serializer.data)


class CustomerTransactionListAPIView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        return Transaction.objects.filter(
            (Q(payer=self.request.user) | Q(receiver=self.request.user)),
            is_deleted=False
        ).distinct()


class CustomerTransactionRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        return Transaction.objects.filter(
            (Q(payer=self.request.user) | Q(receiver=self.request.user)),
            is_deleted=False
        ).distinct()




# ==================== Customer Views ====================
class CustomerListCreate(generics.ListCreateAPIView):
    serializer_class = EmployeeCustomerSerializer
    queryset = Customer.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class CustomerDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeCustomerSerializer
    queryset = Customer.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class CustomerDeposit(generics.GenericAPIView):
    """
    ایدی در یو ار ال ایدی کاستومر است
    """
    serializer_class = CustomerDepositSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        customer_id = self.kwargs.get('pk')
        payment_method_id = serializer.validated_data['payment_method_id']
        amount = serializer.validated_data['amount']
        description = serializer.validated_data.get('description', '')

        try:
            payment_method = PaymentMethod.objects.get(id=payment_method_id)
            customer = Customer.objects.get(id=customer_id)
        except PaymentMethod.DoesNotExist:
            return Response({"error": "Payment method not found."}, status=404)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found."}, status=404)

        # ایجاد تراکنش
        transaction = Transaction.objects.create(
            payer=customer.user,
            receiver_str='دکترگیم',
            amount=amount,
            payment_method=payment_method,
            in_out=True,
            description=description
        )

        # بروزرسانی موجودی‌ها
        customer.balance += amount
        customer.save()
        payment_method.balance += amount
        payment_method.save()

        # بازگرداندن تراکنش
        transaction_serializer = TransactionSerializer(transaction)
        return Response(transaction_serializer.data, status=201)


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

