from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters, status
from rest_framework.response import Response

from accounting.models import Order, GameOrder, PaymentMethod, RepairOrder, DeliveryMan, TelegramOrder, CourseOrder
from accounting.serializers import DeliveryManSerializer, EmployeePaymentMethodSerializer, \
    CreateTransactionGenericSerializer
from crm.models import Customer
from crm.serializers import EmployeeCustomerSerializer
from hr.filters import GameOrderFilter, TelegramOrderFilter
from hr.models import Employee
from hr.serializers import EmployeeSerializer, RepairManRepairOrderSerializer

from hr.views import EmployeeGameOrderPagination
from inventory.models import Product, Game, SonyAccount
from inventory.serializers import EmployeeProductSerializer
from orders.serializers import EmployeeProductOrderSerializer, EmployeeGameOrderSerializer, \
    EmployeeTelegramOrderSerializer, EmployeeCourseOrderSerializer
from platform_settings.serializers import EmployeeStatusChoicesSerializer
from psn.serializers import EmployeeSonyAccountSerializer
from users.auth import CustomJWTAuthentication
from users.permissions import IsEmployee, IsMainManager
from website.serializers import EmployeeGameSerializer


# Create your views here.

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
            'crm': EmployeeCustomerSerializer(customers, many=True).data,
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
            'crm': EmployeeCustomerSerializer(customers, many=True).data,
            'hr': EmployeeSerializer(employees, many=True).data,
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


# ==================== TelegramOrders Views ====================
class EmployeePanelTelegramOrderList(generics.ListAPIView):
    serializer_class = EmployeeTelegramOrderSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TelegramOrderFilter

    def get_queryset(self):
        return (
            TelegramOrder.objects
            .filter(is_deleted=False)
            .select_related("employee", "sony_account")
        )


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

