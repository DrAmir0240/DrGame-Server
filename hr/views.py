import requests
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from DrGame import settings
from accounting.models import GameOrder, Transaction, RepairOrder, PaymentMethod, TelegramOrder, RepairOrderType
from accounting.serializers import TransactionSerializer, EmployeeDepositSerializer, RepairmanDepositSerializer
from crm.models import Customer
from hr.filters import GameOrderFilter, RepairOrderFilter, \
    EmployeeRequestFilter
from hr.models import Employee, Repairman, EmployeeRequest, EmployeeHire
from hr.serializers import EmployeeRequestSerializer, EmployeeSerializer, SendSmsToEmployeeSerializer, \
    EmployeeHireSerializer, RepairmanSerializer, RepairManRepairOrderSerializer, RepairManTransactionSerializer
from orders.serializers import EmployeeGameOrderSerializer, EmployeeTelegramOrderSerializer, RepairOrderTypeSerializer
from platform_settings.serializers import EmployeeStatusChoicesSerializer
from users.auth import CustomJWTAuthentication
from users.models import CustomUser
from users.permissions import IsEmployee, IsMainManager, IsRepairman
from users.serializers import CustomUserSerializer


# Create your views here.
class EmployeeOrganizeTaskPagination(LimitOffsetPagination):
    default_limit = 3  # تعداد آیتم‌ها در هر صفحه


class EmployeeGameOrderPagination(LimitOffsetPagination):
    default_limit = 12  # تعداد آیتم‌ها در هر صفحه



# ==================== Personal Views ====================
# -------------------- requests --------------------
class EmployeePanelPersonalRequests(generics.ListCreateAPIView):
    serializer_class = EmployeeRequestSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EmployeeRequestFilter
    search_fields = ['title', 'request_type', 'description']
    ordering_fields = ['-created_at']

    def get_queryset(self):
        employee = self.request.user.employee
        return EmployeeRequest.objects.filter(employee=employee)

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user.employee)


class EmployeePanelPersonalRequestsDetail(generics.RetrieveAPIView):
    serializer_class = EmployeeRequestSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        employee = self.request.user.employee
        return EmployeeRequest.objects.filter(employee=employee)


class EmployeePanelRequestChoices(generics.ListAPIView):
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def list(self, request, *args, **kwargs):
        request_type = [
            {'value': value, 'label': label} for value, label in EmployeeRequest._meta.get_field('request_type').choices
        ]
        status = [
            {'value': value, 'label': label} for value, label in EmployeeRequest._meta.get_field('status').choices
        ]
        employees = Employee.objects.filter(is_deleted=False)
        data = {
            'request_type': EmployeeStatusChoicesSerializer(request_type, many=True).data,
            'status': EmployeeStatusChoicesSerializer(status, many=True).data,
            'hr': EmployeeSerializer(employees, many=True).data,
        }

        return Response(data)



# -------------------- orders --------------------
class EmployeePanelOwnedGameOrderList(generics.ListCreateAPIView):
    serializer_class = EmployeeGameOrderSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    pagination_class = EmployeeGameOrderPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = GameOrderFilter
    search_fields = ['order_type', 'order_console_type', 'status', 'payment_status']
    ordering_fields = ['created_at', 'amount']

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        user = self.request.user
        try:
            employee = user.employee
        except AttributeError:
            # اگر کاربر employee نداشت، دسترسی نداره
            raise PermissionDenied("You don't have permission to view these orders.")

        if employee.role == 'account_setter':
            return GameOrder.objects.filter(
                Q(status='delivered_to_drgame_and_in_waiting_queue') | Q(employee_id=employee.id),
                is_deleted=False
            ).order_by('-created_at').select_related('customer').prefetch_related('games')

        elif employee.role == 'data_uploader':
            return GameOrder.objects.filter(
                Q(status='in_data_uploading_queue') | Q(employee_id=employee.id)
            ).order_by('-created_at').select_related('customer').prefetch_related('games')

        return GameOrder.objects.none()


class EmployeePanelOwnedGameOrderDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeGameOrderSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        try:
            employee = user.employee
        except AttributeError:
            # اگر کاربر employee نداشت، دسترسی نداره
            raise PermissionDenied("You don't have permission to view these orders.")

        if employee.role == 'account_setter':
            return GameOrder.objects.filter(
                Q(status='delivered_to_drgame_and_in_waiting_queue') | Q(employee_id=employee.id)
            ).order_by('-created_at').select_related('customer').prefetch_related('games')

        elif employee.role == 'data_uploader':
            return GameOrder.objects.filter(
                Q(status='in_data_uploading_queue') | Q(employee_id=employee.id)
            ).order_by('-created_at').select_related('customer').prefetch_related('games')

        return GameOrder.objects.none()


class EmployeePanelPersonalTelegramOrderList(generics.ListAPIView):
    serializer_class = EmployeeTelegramOrderSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        if hasattr(self.request.user, 'employee'):
            return TelegramOrder.objects.filter(employee=self.request.user.employee)
        return TelegramOrder.objects.none()



# ==================== Employees Views ====================
class UserCreat(generics.CreateAPIView):
    queryset = CustomUser.objects.filter(is_deleted=False)
    serializer_class = CustomUserSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class EmployeeListAdd(generics.ListCreateAPIView):
    queryset = Employee.objects.filter(is_deleted=False)
    serializer_class = EmployeeSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class EmployeeDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class EmployeeDeposit(generics.GenericAPIView):
    """
    ایدیدر یو ار ال ایدی کارمند است
    """
    serializer_class = EmployeeDepositSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        employee_id = self.kwargs.get('pk')
        payment_method_id = serializer.validated_data['payment_method_id']
        amount = serializer.validated_data['amount']
        description = serializer.validated_data.get('description', '')

        try:
            payment_method = PaymentMethod.objects.get(id=payment_method_id)
            employee = Employee.objects.get(id=employee_id)
        except PaymentMethod.DoesNotExist:
            return Response({"error": "Payment method not found."}, status=404)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found."}, status=404)

        transaction = Transaction.objects.create(
            payer_str='دکترگیم',
            receiver=employee.user,
            amount=amount,
            payment_method=payment_method,
            in_out=False,
            description=description
        )

        employee.balance -= amount
        employee.save()
        payment_method.balance -= amount
        payment_method.save()

        transaction_serializer = TransactionSerializer(transaction)
        return Response(transaction_serializer.data, status=201)


class EmployeeSendSmsService(generics.GenericAPIView):
    serializer_class = SendSmsToEmployeeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        message = data['message']
        employee_ids = data['employee_ids']
        send_time = data.get('send_time')

        # گرفتن شماره‌ها از امپلویی‌ها
        recipients = []
        employees = Employee.objects.filter(id__in=employee_ids).select_related('user')
        for employee in employees:
            if employee.user and employee.user.phone:
                recipients.append(employee.user.phone)

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


class EmployeeResumeList(generics.ListAPIView):
    queryset = EmployeeHire.objects.all().order_by("-created_at")
    serializer_class = EmployeeHireSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class EmployeeResumeDelete(generics.DestroyAPIView):
    queryset = EmployeeHire.objects.all().order_by("-created_at")
    serializer_class = EmployeeHireSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]



# ==================== RepairMan Views ====================
class RepairManList(generics.ListCreateAPIView):
    queryset = Repairman.objects.filter(is_deleted=False)
    serializer_class = RepairmanSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class RepairmanDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Repairman.objects.filter(is_deleted=False)
    serializer_class = RepairmanSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    lockup_field = 'id'


class RepairmanDeposit(generics.GenericAPIView):
    """
    ایدی در یو ار ال ایدی تعمیرکار است
    """
    serializer_class = RepairmanDepositSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        repairman_id = self.kwargs.get('pk')
        payment_method_id = serializer.validated_data['payment_method_id']
        amount = serializer.validated_data['amount']
        description = serializer.validated_data.get('description', '')

        try:
            payment_method = PaymentMethod.objects.get(id=payment_method_id)
            repairman = Repairman.objects.get(id=repairman_id)
        except PaymentMethod.DoesNotExist:
            return Response({"error": "Payment method not found."}, status=404)
        except Customer.DoesNotExist:
            return Response({"error": "Repairman not found."}, status=404)

        # ایجاد تراکنش
        transaction = Transaction.objects.create(
            payer=repairman.user,
            receiver_str='دکترگیم',
            amount=amount,
            payment_method=payment_method,
            in_out=False,
            description=description
        )

        # بروزرسانی موجودی‌ها
        repairman.balance -= amount
        repairman.save()
        payment_method.balance -= amount
        payment_method.save()

        # بازگرداندن تراکنش
        transaction_serializer = TransactionSerializer(transaction)
        return Response(transaction_serializer.data, status=201)


# ==================== RepairManPanel Views ====================
class RepairManRepairOrderList(generics.ListAPIView):
    serializer_class = RepairManRepairOrderSerializer
    permission_classes = [IsRepairman]
    authentication_classes = [CustomJWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RepairOrderFilter
    search_fields = ['order_type', 'status']
    ordering_fields = ['-created_at', 'amount']

    def get_queryset(self):
        repairman = self.request.user.repairman
        repair_orders = RepairOrder.objects.filter(Q(repair_man=repairman) | Q(status='in_accepting_queue'),
                                                   is_deleted=False)
        return repair_orders


class RepairManPanelRepairOrderDetail(generics.RetrieveUpdateAPIView):
    serializer_class = RepairManRepairOrderSerializer
    permission_classes = [IsRepairman]
    authentication_classes = [CustomJWTAuthentication]
    lookup_field = 'pk'

    def get_queryset(self):
        repairman = self.request.user.repairman
        repair_orders = RepairOrder.objects.filter(Q(repair_man=repairman) | Q(status='in_accepting_queue'),
                                                   is_deleted=False)
        return repair_orders


class RepairManPanelStatusChoices(generics.ListAPIView):
    permission_classes = [IsRepairman]
    authentication_classes = [CustomJWTAuthentication]

    def list(self, request, *args, **kwargs):
        repair_order_types = RepairOrderType.objects.all()
        repair_order_status = [
            {'value': value, 'label': label} for value, label in RepairOrder._meta.get_field('status').choices
        ]
        response_data = {
            'status': EmployeeStatusChoicesSerializer(repair_order_status, many=True).data,
            'repair_order_types': RepairOrderTypeSerializer(repair_order_types, many=True).data,
        }
        return Response(response_data)


class RepairManPanelInTransactionList(generics.ListAPIView):
    serializer_class = RepairManRepairOrderSerializer
    permission_classes = [IsRepairman]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        return RepairOrder.objects.filter(repair_man=self.request.user.repairman)


class RepairManPanelOutTransactionList(generics.ListAPIView):
    serializer_class = RepairManTransactionSerializer
    permission_classes = [IsRepairman]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        return Transaction.objects.filter(receiver=self.request.user)


class EmployeePanelRequests(generics.ListAPIView):
    queryset = EmployeeRequest.objects.filter(is_deleted=False)
    serializer_class = EmployeeRequestSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EmployeeRequestFilter
    search_fields = ['title', 'request_type', 'description']
    ordering_fields = ['-created_at']


class EmployeePanelRequestsDetail(generics.RetrieveUpdateAPIView):
    queryset = EmployeeRequest.objects.filter(is_deleted=False)
    serializer_class = EmployeeRequestSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
