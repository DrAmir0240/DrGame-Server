import requests
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Count, Sum
from django.utils.dateparse import parse_date
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, filters
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from DrGame import settings
from accounts.auth import CustomJWTAuthentication
from accounts.models import CustomUser
from accounts.permissions import IsEmployee, restrict_access, IsMainManager, IsRepairman
from customers.models import Customer
from employees.filters import EmployeeTaskFilter, TransactionFilter, GameOrderFilter, RepairOrderFilter, \
    SonyAccountFilter, SonyAccountPersonalFilter, EmployeeRequestFilter
from employees.models import EmployeeTask, Employee, Repairman, EmployeeRequest, EmployeeHire
from employees.serializers import EmployeeGameSerializer, EmployeeGameOrderSerializer, \
    EmployeeSonyAccountSerializer, EmployeeTransactionSerializer, EmployeeProductSerializer, \
    EmployeePersonalTaskSerializer, EmployeeProductOrderSerializer, EmployeeRepairOrderSerializer, \
    EmployeeProductColorSerializer, EmployeeProductCategorySerializer, EmployeeProductCompanySerializer, \
    EmployeeCustomerSerializer, EmployeeSerializer, \
    EmployeeStatusChoicesSerializer, CustomUserSerializer, EmployeeBlogSerializer, EmployeeDocsSerializer, \
    EmployeeDocCategorySerializer, EmployeeIncomingTransactionSerializer, EmployeesOutgoingTransactionSerializer, \
    EmployeePaymentMethodSerializer, RepairmanSerializer, RepairManRepairOrderSerializer, \
    RepairManTransactionSerializer, GameBulkPriceUpdateSerializer, EmployeeOrganizeTaskSerializer, \
    EmployeeRealAssetsSerializer, EmployeeRealAssetsCategorySerializer, \
    EmployeePersonalGameOrderItemSerializer, EmployeeCourseOrderSerializer, \
    CreateTransactionGenericSerializer, EmployeeTaskStatsSerializer, GameAndRepairOrderStatsSerializer, \
    OrderStatsSerializer, ProductOrderStatsSerializer, FinanceSummarySerializer, EmployeeStatsSerializer, \
    CustomerStatsSerializer, SellReportSerializer, FinanceReportSerializer, PerformanceReportSerializer, \
    CustomerReportSerializer, EmployeeDepositSerializer, CustomerDepositSerializer, SendSmsSerializer, \
    SendSmsToEmployeeSerializer, EmployeeSonyAccountStatusSerializer, EmployeeSonyAccountBankSerializer, \
    RepairOrderTypeSerializer, EmployeeRequestSerializer, EmployeeHireSerializer, RepairmanDepositSerializer
from home.models import BlogPost
from payments.models import GameOrder, Transaction, Order, RepairOrder, PaymentMethod, GameOrderItem, CourseOrder, \
    DeliveryMan, TelegramOrder, RepairOrderType
from payments.serializers import DeliveryManSerializer, TransactionSerializer
from storage.models import SonyAccount, SonyAccountGame, Product, ProductColor, ProductCategory, ProductCompany, Game, \
    Document, DocCategory, RealAssets, RealAssetsCategory, SonyAccountStatus, SonyAccountBank


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
        employees = Employee.objects.filter(is_deleted=False)
        data = {
            'request_type': EmployeeStatusChoicesSerializer(request_type, many=True).data,
            'employees': EmployeeSerializer(employees, many=True).data,
        }

        return Response(data)


# -------------------- sony-accounts --------------------
class EmployeePanelOwnedSonyAccountList(generics.ListAPIView):
    serializer_class = EmployeeSonyAccountSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = SonyAccountPersonalFilter
    search_fields = ['username', 'status__title']

    def get_queryset(self):
        user = self.request.user
        try:
            employee = user.employee
            return SonyAccount.objects.filter(employee=employee)
        except AttributeError:
            return Response(status=404)


class EmployeePanelOwnedSonyAccountDetail(generics.RetrieveUpdateAPIView):
    serializer_class = EmployeeSonyAccountSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        user = self.request.user
        try:
            employee = user.employee
            return SonyAccount.objects.filter(employee=employee)
        except AttributeError:
            return Response(status=404)


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


# -------------------- tasks --------------------
class EmployeePanelTaskList(generics.ListAPIView):
    serializer_class = EmployeePersonalTaskSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]
    pagination_class = EmployeeOrganizeTaskPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = EmployeeTaskFilter
    ordering_fields = ['deadline', 'created_at']
    search_fields = ['title', 'description']

    def get_queryset(self):
        user = self.request.user
        try:
            employee = user.employee
            return EmployeeTask.objects.filter(employee=employee, is_deleted=False)
        except AttributeError:
            return Response(status=404)


class EmployeePanelTaskDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeePersonalTaskSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        user = self.request.user
        try:
            employee = user.employee
            return EmployeeTask.objects.filter(employee=employee)
        except AttributeError:
            return Response(status=404)


class EmployeePanelAddTask(generics.CreateAPIView):
    serializer_class = EmployeePersonalTaskSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        user = self.request.user
        try:
            employee = user.employee
            return EmployeeTask.objects.filter(employee=employee)
        except AttributeError:
            return Response(status=404)


# -------------------- transactions --------------------
class EmployeePanelOwnedOutTransactionList(generics.ListAPIView):
    serializer_class = EmployeeTransactionSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        receiver = self.request.user
        try:
            return Transaction.objects.filter(receiver=receiver, is_deleted=False)
        except AttributeError:
            return Response(status=404)


class EmployeePanelOwnedOutTransactionDetail(generics.RetrieveAPIView):
    serializer_class = EmployeeTransactionSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        receiver = self.request.user
        try:
            return Transaction.objects.filter(receiver=receiver, is_deleted=False)
        except AttributeError:
            return Response(status=404)


class EmployeePanelOwnedInTransactionList(generics.GenericAPIView):
    serializer_class = EmployeePersonalGameOrderItemSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, *args, **kwargs):
        employee = request.user.employee
        game_order_items = GameOrderItem.objects.filter(
            Q(account_setter=employee) | Q(data_uploader=employee),
            is_deleted=False
        )

        serializer = self.get_serializer(game_order_items, many=True)
        return Response(serializer.data)


class EmployeePanelOwnedInTransactionDetail(generics.RetrieveAPIView):
    queryset = GameOrderItem.objects.filter(is_deleted=False)
    serializer_class = EmployeePersonalGameOrderItemSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        employee = self.request.user.employee
        return GameOrderItem.objects.filter(
            is_deleted=False
        ).filter(
            Q(account_setter=employee) | Q(data_uploader=employee)
        )


# ==================== TaskManager Views ====================
class EmployeePanelOrganizeTaskListCreateView(generics.ListCreateAPIView):
    queryset = EmployeeTask.objects.filter(type='Organize')
    serializer_class = EmployeeOrganizeTaskSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    pagination_class = EmployeeOrganizeTaskPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EmployeeTaskFilter
    ordering_fields = ['created_at', 'dead_line']


class EmployeePanelOrganizeTaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EmployeeTask.objects.filter(type='Organize')
    serializer_class = EmployeeOrganizeTaskSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class EmployeePanelOrganizeTaskChoices(generics.ListAPIView):
    queryset = Employee.objects.filter(is_deleted=False)
    serializer_class = EmployeeSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


# ==================== Product Views ====================
class EmployeePanelProductList(generics.ListAPIView):
    serializer_class = EmployeeProductSerializer
    queryset = Product.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class EmployeePanelProductDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeProductSerializer
    queryset = Product.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class EmployeePanelAddProduct(generics.CreateAPIView):
    serializer_class = EmployeeProductSerializer
    queryset = Product.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class EmployeePanelProductChoices(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        colors = ProductColor.objects.all()
        categories = ProductCategory.objects.all()
        companies = ProductCompany.objects.all()

        response_data = {
            'colors': EmployeeProductColorSerializer(colors, many=True).data,
            'categories': EmployeeProductCategorySerializer(categories, many=True).data,
            'companies': EmployeeProductCompanySerializer(companies, many=True).data,
        }

        return Response(response_data)


# ==================== SonyAccounts Views ====================
class EmployeePanelGetNewSonyAccount(generics.GenericAPIView):
    serializer_class = EmployeeSonyAccountSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, *args, **kwargs):
        employee = request.user.employee

        # مرحله اول: بررسی اکانت‌های فعلی کارمند
        unchecked_account = SonyAccount.objects.filter(
            employee=employee,
            is_deleted=False,
            games__isnull=True
        ).filter(
            Q(status__is_available=True) | Q(status__isnull=True)
        ).first()

        if unchecked_account:
            return Response(
                {"error": "شمااکانت چک‌نشده دارید، لطفاً اول همان اکانت را بررسی کنید."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # مرحله دوم: گرفتن قدیمی‌ترین اکانت بدون کارمند
        oldest_account = SonyAccount.objects.filter(
            employee__isnull=True,
            is_deleted=False,
            is_owned=False
        ).order_by('created_at').first()

        if not oldest_account:
            return Response(
                {"error": "هیچ اکانت آزادی برای اختصاص یافتن موجود نیست."},
                status=status.HTTP_404_NOT_FOUND
            )

        # اساین به کارمند
        oldest_account.employee = employee
        oldest_account.save()

        serializer = self.get_serializer(oldest_account)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EmployeePanelSonyAccountList(generics.ListAPIView):
    queryset = SonyAccount.objects.filter(is_deleted=False)
    serializer_class = EmployeeSonyAccountSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SonyAccountFilter
    search_fields = ['employee__first_name', 'employee__last_name', 'status__title']
    ordering_fields = ['created_at', 'amount']


class EmployeePanelSonyAccountDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SonyAccount.objects.filter(is_deleted=False)
    serializer_class = EmployeeSonyAccountSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    lookup_field = 'pk'


class EmployeePanelSonyAccountChoices(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        games = Game.objects.all()
        statuses = SonyAccountStatus.objects.all()
        employees = Employee.objects.all()
        bank_accounts = SonyAccountBank.objects.all()
        response_data = {
            'games': EmployeeGameSerializer(games, many=True).data,
            'statuses': EmployeeSonyAccountStatusSerializer(statuses, many=True).data,
            'employees': EmployeeSerializer(employees, many=True).data,
            'banks': EmployeeSonyAccountBankSerializer(bank_accounts, many=True).data,
        }
        return Response(response_data)


# ==================== ProductOrders Views ====================
class EmployeePanelProductOrderList(generics.ListAPIView):
    serializer_class = EmployeeProductOrderSerializer
    queryset = Order.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class EmployeePanelProductOrderDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeProductOrderSerializer
    queryset = Order.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class EmployeePanelAddOrder(generics.CreateAPIView):
    serializer_class = EmployeeProductOrderSerializer
    queryset = Order.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class EmployeePanelProductOrderChoices(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        customers = Customer.objects.filter(is_deleted=False)
        products = Product.objects.filter(is_deleted=False)
        response_data = {
            'customers': EmployeeCustomerSerializer(customers, many=True).data,
            'products': EmployeeProductSerializer(products, many=True).data,

        }
        return Response(response_data)


# ==================== GameOrders Views ====================
class EmployeePanelGameOrder(generics.ListCreateAPIView):
    queryset = GameOrder.objects.filter(is_deleted=False).order_by('-created_at')
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


class EmployeePanelGameOrderDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = GameOrder.objects.filter(is_deleted=False).order_by('-created_at').select_related(
        'customer').prefetch_related('games')
    serializer_class = EmployeeGameOrderSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    lookup_field = 'pk'

    def perform_update(self, serializer):
        serializer.save()


class EmployeePanelGameOrderChoices(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        customers = Customer.objects.filter(is_deleted=False)
        employees = Employee.objects.filter(is_deleted=False)
        games = Game.objects.filter(is_deleted=False)
        sony_accounts = SonyAccount.objects.filter(is_deleted=False)
        payment_methods = PaymentMethod.objects.filter(is_online=False, is_deleted=False)

        payment_status_choices = [
            {'value': value, 'label': label} for value, label in GameOrder._meta.get_field('payment_status').choices
        ]
        status_choices = [
            {'value': value, 'label': label} for value, label in GameOrder._meta.get_field('status').choices
        ]
        order_console_type = [
            {'value': value, 'label': label} for value, label in GameOrder._meta.get_field('order_console_type').choices
        ]
        response_data = {
            'customers': EmployeeCustomerSerializer(customers, many=True).data,
            'employees': EmployeeSerializer(employees, many=True).data,
            'games': EmployeeGameSerializer(games, many=True).data,
            'sony_accounts': EmployeeSonyAccountSerializer(sony_accounts, many=True).data,
            'status_choices': EmployeeStatusChoicesSerializer(status_choices, many=True).data,
            'order_console_type': EmployeeStatusChoicesSerializer(order_console_type, many=True).data,
            'payment_status_choices': EmployeeStatusChoicesSerializer(payment_status_choices, many=True).data,
            'payment_methods': EmployeePaymentMethodSerializer(payment_methods, many=True).data,
        }

        return Response(response_data)


class AssignDeliveryToCustomerForGamedOrder(generics.GenericAPIView):
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request, order_id):
        try:
            repair_order = RepairOrder.objects.get(pk=order_id)
        except GameOrder.DoesNotExist:
            return Response({"error": "سفارش پیدا نشد."}, status=status.HTTP_404_NOT_FOUND)
        serializer = DeliveryManSerializer(data=request.data)
        if serializer.is_valid():
            deliveryman, created = DeliveryMan.objects.get_or_create(
                full_name=serializer.validated_data['full_name'],
                phone_number=serializer.validated_data['phone_number']
            )
            repair_order.delivery_to_customer = deliveryman
            repair_order.save()
            return Response({"message": "پیک با موفقیت به سفارش متصل شد."}, status=status.HTTP_200_OK)


# ==================== RepairOrders Views ====================
class EmployeePanelRepairOrderList(generics.ListCreateAPIView):
    serializer_class = RepairManRepairOrderSerializer
    queryset = RepairOrder.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class EmployeePanelRepairOrderDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RepairManRepairOrderSerializer
    queryset = RepairOrder.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class AssignDeliveryToCustomerForRepairOrder(generics.GenericAPIView):
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request, order_id):
        try:
            repair_order = RepairOrder.objects.get(pk=order_id)
        except GameOrder.DoesNotExist:
            return Response({"error": "سفارش پیدا نشد."}, status=status.HTTP_404_NOT_FOUND)
        serializer = DeliveryManSerializer(data=request.data)
        if serializer.is_valid():
            deliveryman, created = DeliveryMan.objects.get_or_create(
                full_name=serializer.validated_data['full_name'],
                phone_number=serializer.validated_data['phone_number']
            )
            repair_order.delivery_to_customer = deliveryman
            repair_order.save()
            return Response({"message": "پیک با موفقیت به سفارش متصل شد."}, status=status.HTTP_200_OK)


# ==================== CourseOrders Views ====================
class EmployeePanelCourseOrdersList(generics.ListAPIView):
    queryset = CourseOrder.objects.filter(is_deleted=False, payment_status="paid")
    serializer_class = EmployeeCourseOrderSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class EmployeePanelCourseOrdersDetail(generics.RetrieveAPIView):
    queryset = CourseOrder.objects.filter(is_deleted=False, payment_status="paid")
    serializer_class = EmployeeCourseOrderSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    lookup_field = 'pk'


# ==================== Transactions Views ====================
class EmployeePanelTransactionList(generics.ListAPIView):
    queryset = Transaction.objects.filter(is_deleted=False)
    serializer_class = EmployeeTransactionSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TransactionFilter
    search_fields = [
        'description',
        'payment_method__title',
        'payer__customer__full_name',
        'receiver__employee__first_name',
        'receiver__employee__last_name',
    ]
    ordering_fields = ['created_at', 'amount']


class EmployeePanelTransactionDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeTransactionSerializer
    queryset = Transaction.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    lookup_field = 'pk'


class EmployeePanelAddIncomingTransactionView(generics.CreateAPIView):
    queryset = Transaction.objects.filter(is_deleted=False)
    serializer_class = EmployeeIncomingTransactionSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class EmployeePanelAddOutGoingTransaction(generics.CreateAPIView):
    queryset = Transaction.objects.filter(is_deleted=False)
    serializer_class = EmployeesOutgoingTransactionSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class EmployeePanelTransactionPayerReceiverChoices(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        customers = Customer.objects.all()
        employees = Employee.objects.all()
        response_data = {
            'customers': EmployeeCustomerSerializer(customers, many=True).data,
            'employees': EmployeeSerializer(employees, many=True).data,
        }
        return Response(response_data)


class EmployeePanelTransactionOrderChoices(generics.ListAPIView):
    serializer_class = None
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        customer_id = self.kwargs.get('customer_id')
        order_type = self.kwargs.get('order_type')

        if order_type == 'order':
            self.serializer_class = EmployeeProductOrderSerializer
            return Order.objects.filter(customer_id=customer_id, is_deleted=False, payment_status='unpaid')

        elif order_type == 'game_order':
            self.serializer_class = EmployeeGameOrderSerializer
            return GameOrder.objects.filter(customer_id=customer_id, is_deleted=False, payment_status='unpaid')

        elif order_type == 'repair_order':
            self.serializer_class = EmployeeRepairOrderSerializer
            return RepairOrder.objects.filter(customer_id=customer_id, is_deleted=False, payment_status='unpaid')

        raise ValidationError(
            {"order_type": "نوع سفارش نامعتبر است. باید یکی از [order, game_order, repair_order] باشد."})


class EmployeePanelCreateRepairOrderTransactionView(generics.CreateAPIView):
    serializer_class = CreateTransactionGenericSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            "model_class": RepairOrder,
            "object_id": self.kwargs["repair_order_id"],
            "amount_field": "amount"
        })
        return context


class EmployeePanelCreateGameOrderTransactionView(generics.CreateAPIView):
    serializer_class = CreateTransactionGenericSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            "model_class": GameOrder,
            "object_id": self.kwargs["game_order_id"],
            "amount_field": "amount"
        })
        return context


class EmployeePanelCreateOrderTransactionView(generics.CreateAPIView):
    serializer_class = CreateTransactionGenericSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            "model_class": Order,
            "object_id": self.kwargs["order_id"],
            "amount_field": "amount"
        })
        return context


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


# ==================== GameStore Views ====================
class EmployeeGameListCreate(generics.ListCreateAPIView):
    serializer_class = EmployeeGameSerializer
    queryset = Game.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class EmployeeGameDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeGameSerializer
    queryset = Game.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class GameBulkPriceUpdateView(generics.GenericAPIView):
    serializer_class = GameBulkPriceUpdateSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        price_type = serializer.get_db_field()  # تبدیل خودکار
        price_value = serializer.validated_data['price']

        updated_count = Game.objects.update(**{price_type: price_value})

        return Response({
            "message": f"Updated {updated_count} games",
            "type": serializer.validated_data['type'],  # همون چیزی که کاربر فرستاده
            "price": price_value
        }, status=status.HTTP_200_OK)


# ==================== Blog Views ====================
class EmployeeBlogListCreate(generics.ListCreateAPIView):
    serializer_class = EmployeeBlogSerializer
    queryset = BlogPost.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class EmployeeBlogDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeBlogSerializer
    queryset = BlogPost.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    lookup_field = 'slug'


# ==================== Docs Views ====================
class EmployeePanelDocument(generics.ListCreateAPIView):
    queryset = Document.objects.filter(is_deleted=False)
    serializer_class = EmployeeDocsSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class EmployeePanelDocumentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.filter(is_deleted=False)
    serializer_class = EmployeeDocsSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    lockup_field = 'id'


class EmployeePanelDocCategory(generics.ListCreateAPIView):
    queryset = DocCategory.objects.filter(is_deleted=False)
    serializer_class = EmployeeDocCategorySerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


# ==================== Real Assets Views ====================
class EmployeePanelRealAssets(generics.ListCreateAPIView):
    queryset = RealAssets.objects.filter(is_deleted=False)
    serializer_class = EmployeeRealAssetsSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class EmployeePanelRealAssetsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = RealAssets.objects.filter(is_deleted=False)
    serializer_class = EmployeeRealAssetsSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    lockup_field = 'id'


class EmployeePanelRealAssetsCategory(generics.ListCreateAPIView):
    queryset = RealAssetsCategory.objects.filter(is_deleted=False)
    serializer_class = EmployeeRealAssetsCategorySerializer
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


# ==================== Stats Views ====================
class TaskStatsAPIView(generics.GenericAPIView):
    serializer_class = EmployeeTaskStatsSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, *args, **kwargs):
        employee = request.user.employee

        qs = EmployeeTask.objects.filter(employee=employee, is_deleted=False)

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
        qs = Order.objects.filter(is_deleted=False)

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
            'customers': qs.count(),
        }
        serializer = self.get_serializer(data)
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


class EmployeePanelRequests(generics.ListAPIView):
    queryset = EmployeeRequest.objects.filter(is_deleted=False)
    serializer_class = EmployeeRequestSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EmployeeRequestFilter
    search_fields = ['title', 'request_type', 'description']
    ordering_fields = ['-created_at']


class EmployeePanelRequestsDetail(generics.RetrieveAPIView):
    queryset = EmployeeRequest.objects.filter(is_deleted=False)
    serializer_class = EmployeeRequestSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
