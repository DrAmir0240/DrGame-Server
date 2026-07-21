from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters, status
from rest_framework import serializers as drf_serializers
from rest_framework.response import Response

''' LEGACY — commented out after the accounting restructure removed these models
(Order, GameOrder, PaymentMethod, RepairOrder, DeliveryMan, TelegramOrder, CourseOrder).
Dead code: nothing imports these views and their URLs are disabled.

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
'''  # END LEGACY


# =============================================================================
# =============================================================================
# ORDERS WORKFLOW (stage/action engine) — Sony Account / Repair / Product
# =============================================================================
# =============================================================================

from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer
from drf_spectacular.utils import extend_schema

from users.permissions import IsEmployee
from hr.permissions import employee_permission

from orders.filters import SonyAccountOrderFilter, RepairOrderFilter, ProductOrderFilter
from orders.models import (
    SonyAccountOrderCategory, SonyAccountOrderStage, SonyAccountOrderStageAction,
    SonyAccountOrder,
    RepairOrderCategory, RepairOrderStage, RepairOrderStageAction, RepairOrder,
    ProductOrderCategory, ProductOrderStage, ProductOrderStageAction, ProductOrder,
)
from orders.serializers import (
    # Sony
    SonyAccountOrderCategoryListSerializer, SonyAccountOrderCategoryDetailSerializer,
    SonyAccountOrderStageListSerializer, SonyAccountOrderStageDetailSerializer,
    SonyAccountOrderStageActionSerializer, SonyAccountOrderStageQueueSerializer,
    SonyAccountOrderCardSerializer, SonyAccountOrderDetailSerializer,
    SonyAccountOrderActionSerializer,
    # Repair
    RepairOrderCategoryListSerializer, RepairOrderCategoryDetailSerializer,
    RepairOrderStageListSerializer, RepairOrderStageDetailSerializer,
    RepairOrderStageActionSerializer, RepairOrderStageQueueSerializer,
    RepairOrderCardSerializer, RepairOrderDetailSerializer,
    RepairOrderActionSerializer,
    # Product
    ProductOrderCategoryListSerializer, ProductOrderCategoryDetailSerializer,
    ProductOrderStageListSerializer, ProductOrderStageDetailSerializer,
    ProductOrderStageActionSerializer, ProductOrderStageQueueSerializer,
    ProductOrderCardSerializer, ProductOrderDetailSerializer,
    ProductOrderActionSerializer,
    # Shared
    ExecuteActionSerializer, AdvanceStageSerializer,
)
from orders.services import (
    execute_sony_account_order_action, advance_sony_account_order_stage,
    execute_repair_order_action, advance_repair_order_stage,
    execute_product_order_action, advance_product_order_stage,
)


# =============================================================================
# SECTION 1 — SONY ACCOUNT ORDER
# =============================================================================

# --- 1.1 Config (manager): Category ---
@extend_schema(tags=['Orders — Sony Account — Config'], summary='لیست دسته‌بندی‌های اکانت سونی')
class SonyAccountOrderCategoryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'read')]
    serializer_class = SonyAccountOrderCategoryListSerializer
    queryset = SonyAccountOrderCategory.objects.filter(is_deleted=False)


@extend_schema(tags=['Orders — Sony Account — Config'], summary='ایجاد دسته‌بندی')
class SonyAccountOrderCategoryCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = SonyAccountOrderCategoryDetailSerializer
    queryset = SonyAccountOrderCategory.objects.filter(is_deleted=False)


@extend_schema(tags=['Orders — Sony Account — Config'], summary='ویرایش دسته‌بندی')
class SonyAccountOrderCategoryUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = SonyAccountOrderCategoryDetailSerializer
    queryset = SonyAccountOrderCategory.objects.filter(is_deleted=False)
    http_method_names = ['patch']


@extend_schema(tags=['Orders — Sony Account — Config'], summary='حذف دسته‌بندی')
class SonyAccountOrderCategoryDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = drf_serializers.Serializer
    queryset = SonyAccountOrderCategory.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


# --- 1.1 Config (manager): Stage ---
@extend_schema(tags=['Orders — Sony Account — Config'], summary='لیست مراحل یک دسته‌بندی')
class SonyAccountOrderStageListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'read')]
    serializer_class = SonyAccountOrderStageListSerializer

    def get_queryset(self):
        return SonyAccountOrderStage.objects.filter(
            category_id=self.kwargs['category_id'],
            is_deleted=False
        ).select_related('employee_role').order_by('order')


@extend_schema(tags=['Orders — Sony Account — Config'], summary='ایجاد مرحله')
class SonyAccountOrderStageCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = SonyAccountOrderStageDetailSerializer
    queryset = SonyAccountOrderStage.objects.filter(is_deleted=False)


@extend_schema(tags=['Orders — Sony Account — Config'], summary='جزئیات مرحله')
class SonyAccountOrderStageDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'read')]
    serializer_class = SonyAccountOrderStageDetailSerializer
    queryset = SonyAccountOrderStage.objects.filter(is_deleted=False)


@extend_schema(tags=['Orders — Sony Account — Config'], summary='ویرایش مرحله')
class SonyAccountOrderStageUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = SonyAccountOrderStageDetailSerializer
    queryset = SonyAccountOrderStage.objects.filter(is_deleted=False)
    http_method_names = ['patch']


@extend_schema(tags=['Orders — Sony Account — Config'], summary='حذف مرحله')
class SonyAccountOrderStageDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = drf_serializers.Serializer
    queryset = SonyAccountOrderStage.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


# --- 1.1 Config (manager): Stage Action ---
@extend_schema(tags=['Orders — Sony Account — Config'], summary='ایجاد اکشن برای مرحله')
class SonyAccountOrderStageActionCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = SonyAccountOrderStageActionSerializer
    queryset = SonyAccountOrderStageAction.objects.filter(is_deleted=False)


@extend_schema(tags=['Orders — Sony Account — Config'], summary='ویرایش اکشن')
class SonyAccountOrderStageActionUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = SonyAccountOrderStageActionSerializer
    queryset = SonyAccountOrderStageAction.objects.filter(is_deleted=False)
    http_method_names = ['patch']


@extend_schema(tags=['Orders — Sony Account — Config'], summary='حذف اکشن')
class SonyAccountOrderStageActionDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = drf_serializers.Serializer
    queryset = SonyAccountOrderStageAction.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


# --- 1.2 Worker panel ---
@extend_schema(tags=['Orders — Sony Account — Worker'], summary='لیست stage های قابل دسترس این کارمند')
class MySonyAccountStagesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    serializer_class = SonyAccountOrderStageQueueSerializer

    def get_queryset(self):
        employee = self.request.user.employee
        role_ids = employee.roles.values_list('id', flat=True)
        return SonyAccountOrderStage.objects.filter(
            employee_role_id__in=role_ids,
            is_deleted=False
        ).order_by('order')


@extend_schema(tags=['Orders — Sony Account — Worker'], summary='لیست سفارشات یک stage')
class SonyAccountOrderByStageView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    serializer_class = SonyAccountOrderCardSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = SonyAccountOrderFilter
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return SonyAccountOrder.objects.none()
        return SonyAccountOrder.objects.filter(
            stage_id=self.kwargs['stage_id'],
            is_deleted=False
        ).select_related(
            'customer', 'customer__user', 'category', 'stage'
        ).prefetch_related('action_logs').order_by('-created_at')


@extend_schema(tags=['Orders — Sony Account — Worker'], summary='جزئیات سفارش')
class SonyAccountOrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    serializer_class = SonyAccountOrderDetailSerializer
    queryset = SonyAccountOrder.objects.filter(is_deleted=False).select_related(
        'customer', 'customer__user', 'category', 'stage'
    ).prefetch_related(
        'items', 'consoles', 'action_logs', 'stage_logs'
    )


@extend_schema(tags=['Orders — Sony Account — Worker'], summary='لیست اکشن‌های stage فعلی سفارش')
class SonyAccountOrderActionsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    serializer_class = SonyAccountOrderActionSerializer

    def get_queryset(self):
        order = get_object_or_404(SonyAccountOrder, pk=self.kwargs['order_id'], is_deleted=False)
        if not order.stage:
            return SonyAccountOrderStageAction.objects.none()
        return order.stage.actions.filter(is_deleted=False)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['order_id'] = self.kwargs['order_id']
        return context


@extend_schema(tags=['Orders — Sony Account — Worker'], summary='اجرای یک اکشن روی سفارش')
class SonyAccountOrderExecuteActionView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    serializer_class = ExecuteActionSerializer

    def post(self, request, order_id):
        order = get_object_or_404(SonyAccountOrder, pk=order_id, is_deleted=False)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = dict(serializer.validated_data)
        action = get_object_or_404(
            SonyAccountOrderStageAction, pk=data['action_id'], is_deleted=False
        )
        data['action'] = action

        try:
            result = execute_sony_account_order_action(
                order=order,
                validated_data=data,
                performed_by=request.user.employee
            )
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result)


@extend_schema(tags=['Orders — Sony Account — Worker'], summary='انتقال سفارش به مرحله بعدی')
class SonyAccountOrderAdvanceStageView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    serializer_class = AdvanceStageSerializer

    def post(self, request, order_id):
        order = get_object_or_404(SonyAccountOrder, pk=order_id, is_deleted=False)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = advance_sony_account_order_stage(
                order=order,
                note=serializer.validated_data.get('note', ''),
                changed_by=request.user.employee
            )
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result)


# =============================================================================
# SECTION 2 — REPAIR ORDER
# =============================================================================

# --- 2.1 Config (manager): Category ---
@extend_schema(tags=['Orders — Repair — Config'], summary='لیست دسته‌بندی‌های تعمیر')
class RepairOrderCategoryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'read')]
    serializer_class = RepairOrderCategoryListSerializer
    queryset = RepairOrderCategory.objects.filter(is_deleted=False)


@extend_schema(tags=['Orders — Repair — Config'], summary='ایجاد دسته‌بندی')
class RepairOrderCategoryCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = RepairOrderCategoryDetailSerializer
    queryset = RepairOrderCategory.objects.filter(is_deleted=False)


@extend_schema(tags=['Orders — Repair — Config'], summary='ویرایش دسته‌بندی')
class RepairOrderCategoryUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = RepairOrderCategoryDetailSerializer
    queryset = RepairOrderCategory.objects.filter(is_deleted=False)
    http_method_names = ['patch']


@extend_schema(tags=['Orders — Repair — Config'], summary='حذف دسته‌بندی')
class RepairOrderCategoryDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = drf_serializers.Serializer
    queryset = RepairOrderCategory.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


# --- 2.1 Config (manager): Stage ---
@extend_schema(tags=['Orders — Repair — Config'], summary='لیست مراحل یک دسته‌بندی')
class RepairOrderStageListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'read')]
    serializer_class = RepairOrderStageListSerializer

    def get_queryset(self):
        return RepairOrderStage.objects.filter(
            category_id=self.kwargs['category_id'],
            is_deleted=False
        ).select_related('employee_role').order_by('order')


@extend_schema(tags=['Orders — Repair — Config'], summary='ایجاد مرحله')
class RepairOrderStageCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = RepairOrderStageDetailSerializer
    queryset = RepairOrderStage.objects.filter(is_deleted=False)


@extend_schema(tags=['Orders — Repair — Config'], summary='جزئیات مرحله')
class RepairOrderStageDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'read')]
    serializer_class = RepairOrderStageDetailSerializer
    queryset = RepairOrderStage.objects.filter(is_deleted=False)


@extend_schema(tags=['Orders — Repair — Config'], summary='ویرایش مرحله')
class RepairOrderStageUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = RepairOrderStageDetailSerializer
    queryset = RepairOrderStage.objects.filter(is_deleted=False)
    http_method_names = ['patch']


@extend_schema(tags=['Orders — Repair — Config'], summary='حذف مرحله')
class RepairOrderStageDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = drf_serializers.Serializer
    queryset = RepairOrderStage.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


# --- 2.1 Config (manager): Stage Action ---
@extend_schema(tags=['Orders — Repair — Config'], summary='ایجاد اکشن برای مرحله')
class RepairOrderStageActionCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = RepairOrderStageActionSerializer
    queryset = RepairOrderStageAction.objects.filter(is_deleted=False)


@extend_schema(tags=['Orders — Repair — Config'], summary='ویرایش اکشن')
class RepairOrderStageActionUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = RepairOrderStageActionSerializer
    queryset = RepairOrderStageAction.objects.filter(is_deleted=False)
    http_method_names = ['patch']


@extend_schema(tags=['Orders — Repair — Config'], summary='حذف اکشن')
class RepairOrderStageActionDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = drf_serializers.Serializer
    queryset = RepairOrderStageAction.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


# --- 2.2 Worker panel ---
@extend_schema(tags=['Orders — Repair — Worker'], summary='لیست stage های قابل دسترس این کارمند')
class MyRepairStagesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    serializer_class = RepairOrderStageQueueSerializer

    def get_queryset(self):
        employee = self.request.user.employee
        role_ids = employee.roles.values_list('id', flat=True)
        return RepairOrderStage.objects.filter(
            employee_role_id__in=role_ids,
            is_deleted=False
        ).order_by('order')


@extend_schema(tags=['Orders — Repair — Worker'], summary='لیست سفارشات یک stage')
class RepairOrderByStageView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    serializer_class = RepairOrderCardSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = RepairOrderFilter
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return RepairOrder.objects.none()
        return RepairOrder.objects.filter(
            stage_id=self.kwargs['stage_id'],
            is_deleted=False
        ).select_related(
            'customer', 'customer__user', 'category', 'stage'
        ).prefetch_related('action_logs').order_by('-created_at')


@extend_schema(tags=['Orders — Repair — Worker'], summary='جزئیات سفارش')
class RepairOrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    serializer_class = RepairOrderDetailSerializer
    queryset = RepairOrder.objects.filter(is_deleted=False).select_related(
        'customer', 'customer__user', 'category', 'stage'
    ).prefetch_related(
        'devices', 'action_logs', 'stage_logs'
    )


@extend_schema(tags=['Orders — Repair — Worker'], summary='لیست اکشن‌های stage فعلی سفارش')
class RepairOrderActionsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    serializer_class = RepairOrderActionSerializer

    def get_queryset(self):
        order = get_object_or_404(RepairOrder, pk=self.kwargs['order_id'], is_deleted=False)
        if not order.stage:
            return RepairOrderStageAction.objects.none()
        return order.stage.actions.filter(is_deleted=False)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['order_id'] = self.kwargs['order_id']
        return context


@extend_schema(tags=['Orders — Repair — Worker'], summary='اجرای یک اکشن روی سفارش')
class RepairOrderExecuteActionView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    serializer_class = ExecuteActionSerializer

    def post(self, request, order_id):
        order = get_object_or_404(RepairOrder, pk=order_id, is_deleted=False)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = dict(serializer.validated_data)
        action = get_object_or_404(
            RepairOrderStageAction, pk=data['action_id'], is_deleted=False
        )
        data['action'] = action

        try:
            result = execute_repair_order_action(
                order=order,
                validated_data=data,
                performed_by=request.user.employee
            )
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result)


@extend_schema(tags=['Orders — Repair — Worker'], summary='انتقال سفارش به مرحله بعدی')
class RepairOrderAdvanceStageView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    serializer_class = AdvanceStageSerializer

    def post(self, request, order_id):
        order = get_object_or_404(RepairOrder, pk=order_id, is_deleted=False)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = advance_repair_order_stage(
                order=order,
                note=serializer.validated_data.get('note', ''),
                changed_by=request.user.employee
            )
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result)


# =============================================================================
# SECTION 3 — PRODUCT ORDER
# =============================================================================

# --- 3.1 Config (manager): Category ---
@extend_schema(tags=['Orders — Product — Config'], summary='لیست دسته‌بندی‌های محصول')
class ProductOrderCategoryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'read')]
    serializer_class = ProductOrderCategoryListSerializer
    queryset = ProductOrderCategory.objects.filter(is_deleted=False)


@extend_schema(tags=['Orders — Product — Config'], summary='ایجاد دسته‌بندی')
class ProductOrderCategoryCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = ProductOrderCategoryDetailSerializer
    queryset = ProductOrderCategory.objects.filter(is_deleted=False)


@extend_schema(tags=['Orders — Product — Config'], summary='ویرایش دسته‌بندی')
class ProductOrderCategoryUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = ProductOrderCategoryDetailSerializer
    queryset = ProductOrderCategory.objects.filter(is_deleted=False)
    http_method_names = ['patch']


@extend_schema(tags=['Orders — Product — Config'], summary='حذف دسته‌بندی')
class ProductOrderCategoryDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = drf_serializers.Serializer
    queryset = ProductOrderCategory.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


# --- 3.1 Config (manager): Stage ---
@extend_schema(tags=['Orders — Product — Config'], summary='لیست مراحل یک دسته‌بندی')
class ProductOrderStageListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'read')]
    serializer_class = ProductOrderStageListSerializer

    def get_queryset(self):
        return ProductOrderStage.objects.filter(
            category_id=self.kwargs['category_id'],
            is_deleted=False
        ).select_related('employee_role').order_by('order')


@extend_schema(tags=['Orders — Product — Config'], summary='ایجاد مرحله')
class ProductOrderStageCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = ProductOrderStageDetailSerializer
    queryset = ProductOrderStage.objects.filter(is_deleted=False)


@extend_schema(tags=['Orders — Product — Config'], summary='جزئیات مرحله')
class ProductOrderStageDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'read')]
    serializer_class = ProductOrderStageDetailSerializer
    queryset = ProductOrderStage.objects.filter(is_deleted=False)


@extend_schema(tags=['Orders — Product — Config'], summary='ویرایش مرحله')
class ProductOrderStageUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = ProductOrderStageDetailSerializer
    queryset = ProductOrderStage.objects.filter(is_deleted=False)
    http_method_names = ['patch']


@extend_schema(tags=['Orders — Product — Config'], summary='حذف مرحله')
class ProductOrderStageDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = drf_serializers.Serializer
    queryset = ProductOrderStage.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


# --- 3.1 Config (manager): Stage Action ---
@extend_schema(tags=['Orders — Product — Config'], summary='ایجاد اکشن برای مرحله')
class ProductOrderStageActionCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = ProductOrderStageActionSerializer
    queryset = ProductOrderStageAction.objects.filter(is_deleted=False)


@extend_schema(tags=['Orders — Product — Config'], summary='ویرایش اکشن')
class ProductOrderStageActionUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = ProductOrderStageActionSerializer
    queryset = ProductOrderStageAction.objects.filter(is_deleted=False)
    http_method_names = ['patch']


@extend_schema(tags=['Orders — Product — Config'], summary='حذف اکشن')
class ProductOrderStageActionDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
    serializer_class = drf_serializers.Serializer
    queryset = ProductOrderStageAction.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


# --- 3.2 Worker panel ---
@extend_schema(tags=['Orders — Product — Worker'], summary='لیست stage های قابل دسترس این کارمند')
class MyProductStagesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    serializer_class = ProductOrderStageQueueSerializer

    def get_queryset(self):
        employee = self.request.user.employee
        role_ids = employee.roles.values_list('id', flat=True)
        return ProductOrderStage.objects.filter(
            employee_role_id__in=role_ids,
            is_deleted=False
        ).order_by('order')


@extend_schema(tags=['Orders — Product — Worker'], summary='لیست سفارشات یک stage')
class ProductOrderByStageView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    serializer_class = ProductOrderCardSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ProductOrderFilter
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return ProductOrder.objects.none()
        return ProductOrder.objects.filter(
            stage_id=self.kwargs['stage_id'],
            is_deleted=False
        ).select_related(
            'customer', 'customer__user', 'stage'
        ).prefetch_related('action_logs').order_by('-created_at')


@extend_schema(tags=['Orders — Product — Worker'], summary='جزئیات سفارش')
class ProductOrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    serializer_class = ProductOrderDetailSerializer
    queryset = ProductOrder.objects.filter(is_deleted=False).select_related(
        'customer', 'customer__user', 'stage'
    ).prefetch_related(
        'items', 'action_logs', 'stage_logs'
    )


@extend_schema(tags=['Orders — Product — Worker'], summary='لیست اکشن‌های stage فعلی سفارش')
class ProductOrderActionsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    serializer_class = ProductOrderActionSerializer

    def get_queryset(self):
        order = get_object_or_404(ProductOrder, pk=self.kwargs['order_id'], is_deleted=False)
        if not order.stage:
            return ProductOrderStageAction.objects.none()
        return order.stage.actions.filter(is_deleted=False)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['order_id'] = self.kwargs['order_id']
        return context


@extend_schema(tags=['Orders — Product — Worker'], summary='اجرای یک اکشن روی سفارش')
class ProductOrderExecuteActionView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    serializer_class = ExecuteActionSerializer

    def post(self, request, order_id):
        order = get_object_or_404(ProductOrder, pk=order_id, is_deleted=False)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = dict(serializer.validated_data)
        action = get_object_or_404(
            ProductOrderStageAction, pk=data['action_id'], is_deleted=False
        )
        data['action'] = action

        try:
            result = execute_product_order_action(
                order=order,
                validated_data=data,
                performed_by=request.user.employee
            )
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result)


@extend_schema(tags=['Orders — Product — Worker'], summary='انتقال سفارش به مرحله بعدی')
class ProductOrderAdvanceStageView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    serializer_class = AdvanceStageSerializer

    def post(self, request, order_id):
        order = get_object_or_404(ProductOrder, pk=order_id, is_deleted=False)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = advance_product_order_stage(
                order=order,
                note=serializer.validated_data.get('note', ''),
                changed_by=request.user.employee
            )


        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result)

