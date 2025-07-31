from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, filters
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.db import transaction as db_transaction, transaction
from accounts.auth import CustomJWTAuthentication
from accounts.models import MainManager, CustomUser
from accounts.permissions import IsEmployee, restrict_access, IsMainManager
from customers.models import Customer
from employees.filters import EmployeeTaskFilter, TransactionFilter
from employees.models import EmployeeTask, Employee
from employees.serializers import EmployeeGameSerializer, EmployeeGameOrderSerializer, \
    EmployeeSonyAccountMatchedSerializer, \
    EmployeeSonyAccountSerializer, EmployeeTransactionSerializer, EmployeeProductSerializer, \
    EmployeeTaskSerializer, EmployeeProductOrderSerializer, EmployeeRepairOrderSerializer, \
    EmployeeProductColorSerializer, EmployeeProductCategorySerializer, EmployeeProductCompanySerializer, \
    EmployeeCustomerSerializer, EmployeeSerializer, \
    EmployeeStatusChoicesSerializer, CustomUserSerializer, EmployeeBlogSerializer, EmployeeDocsSerializer, \
    EmployeeDocCategorySerializer
from home.models import BlogPost
from payments.models import GameOrder, Transaction, Order, RepairOrder, PaymentMethod
from storage.models import SonyAccount, SonyAccountGame, Product, ProductColor, ProductCategory, ProductCompany, Game, \
    Document, DocCategory


# Create your views here.

# ==================== Personal Views ====================
# -------------------- sony-accounts --------------------
class EmployeePanelOwnedSonyAccountList(generics.ListAPIView):
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


class EmployeePanelSonyAccountDetail(generics.RetrieveUpdateDestroyAPIView):
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


class EmployeePanelSonyAccountByOrderGamesView(generics.ListAPIView):
    serializer_class = EmployeeSonyAccountMatchedSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        order_id = self.kwargs['order_id']

        try:
            order = GameOrder.objects.get(id=order_id, is_deleted=False)
        except GameOrder.DoesNotExist:
            return SonyAccount.objects.none()

        selected_games = order.games.all()

        queryset = SonyAccount.objects.filter(
            is_deleted=False,
            games__in=selected_games
        ).annotate(
            matching_games_count=Count('games')
        ).order_by('-matching_games_count')

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# -------------------- orders --------------------
class EmployeePanelOwnedGameOrderList(generics.ListAPIView):
    serializer_class = EmployeeGameOrderSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        user = self.request.user
        try:
            employee = user.employee
            return GameOrder.objects.filter(
                Q(account_setter=employee) | Q(data_uploader=employee)
            ).select_related('customer', 'order_type').prefetch_related('games')
        except AttributeError:
            return Response(status=404)


# -------------------- tasks --------------------
class EmployeePanelTaskList(generics.ListAPIView):
    serializer_class = EmployeeTaskSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]
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
    serializer_class = EmployeeTaskSerializer
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
    serializer_class = EmployeeTaskSerializer
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
class EmployeePanelOwnedTransactionList(generics.ListAPIView):
    serializer_class = EmployeeTransactionSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        receiver = self.request.user
        try:
            return Transaction.objects.filter(receiver=receiver, is_deleted=False)
        except AttributeError:
            return Response(status=404)


class EmployeePanelOwnedTransactionDetail(generics.RetrieveAPIView):
    serializer_class = EmployeeTransactionSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        receiver = self.request.user
        try:
            return Transaction.objects.filter(receiver=receiver, is_deleted=False)
        except AttributeError:
            return Response(status=404)


# ==================== Product Views ====================
@restrict_access('has_access_to_site')
class EmployeePanelProductList(generics.ListAPIView):
    serializer_class = EmployeeProductSerializer
    queryset = Product.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


@restrict_access('has_access_to_site')
class EmployeePanelProductDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeProductSerializer
    queryset = Product.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


@restrict_access('has_access_to_site')
class EmployeePanelAddProduct(generics.CreateAPIView):
    serializer_class = EmployeeProductSerializer
    queryset = Product.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


@restrict_access('has_access_to_site')
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
@restrict_access('has_access_to_accounts')
class EmployeePanelGetNewSonyAccount(generics.RetrieveAPIView):
    queryset = SonyAccount.objects.filter(is_owned=False, is_deleted=False)
    serializer_class = EmployeeSonyAccountSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def get_object(self):
        try:
            oldest_account = self.queryset.order_by('created_at').first()
            if not oldest_account:
                return Response(
                    {"error": "هیچ حساب Sony با شرایط مورد نظر یافت نشد."},
                    status=status.HTTP_404_NOT_FOUND
                )
            if oldest_account.employee:
                unchecked_games = SonyAccountGame.objects.filter(
                    Q(account__employee=oldest_account.employee) & Q(is_checked=False)
                )
                if unchecked_games.exists():
                    return Response(
                        {"error": "شما حساب‌های بازی چک‌نشده دارید."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            return oldest_account
        except SonyAccount.DoesNotExist:
            return Response(
                {"error": "هیچ حساب Sony با شرایط مورد نظر یافت نشد."},
                status=status.HTTP_404_NOT_FOUND
            )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if isinstance(instance, Response):
            return instance
        serializer = self.get_serializer(instance)
        return Response({
            "username": serializer.data["username"],
            "password": serializer.data["password"]
        })


@restrict_access('has_access_to_accounts')
class EmployeePanelSonyAccountList(generics.ListCreateAPIView):
    queryset = SonyAccount.objects.filter(is_deleted=False)
    serializer_class = EmployeeSonyAccountSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


@restrict_access('has_access_to_accounts')
class EmployeePanelSonyAccountChoices(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        games = Game.objects.all()
        response_data = {
            'games': EmployeeGameSerializer(games, many=True).data,
        }
        return Response(response_data)


# ==================== ProductOrders Views ====================
@restrict_access('has_access_to_orders')
class EmployeePanelProductOrderList(generics.ListAPIView):
    serializer_class = EmployeeProductOrderSerializer
    queryset = Order.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


@restrict_access('has_access_to_orders')
class EmployeePanelProductOrderDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeProductOrderSerializer
    queryset = Order.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


@restrict_access('has_access_to_orders')
class EmployeePanelAddOrder(generics.CreateAPIView):
    serializer_class = EmployeeProductOrderSerializer
    queryset = Order.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


@restrict_access('has_access_to_orders')
class EmployeePanelProductOrderChoices(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        customers = Customer.objects.filter(is_deleted=False)
        products = Product.objects.filter(is_deleted=False)
        response_data = {
            'customers': EmployeeGameSerializer(customers, many=True).data,
            'products': EmployeeGameSerializer(products, many=True).data,

        }
        return Response(response_data)


# ==================== GameOrders Views ====================
@restrict_access('has_access_to_game_order')
class EmployeePanelGameOrderList(generics.ListCreateAPIView):
    queryset = GameOrder.objects.filter(is_deleted=False)
    serializer_class = EmployeeGameOrderSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


@restrict_access('has_access_to_game_order')
class EmployeePanelGameOrderDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeGameSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        try:
            employee = user.employee
            return GameOrder.objects.filter(
                Q(account_setter=employee) | Q(data_uploader=employee)
            ).select_related('customer', 'order_type').prefetch_related('games')
        except AttributeError:
            return Response(status=400)


@restrict_access('has_access_to_game_order')
class EmployeePanelGameOrderChoices(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        customers = Customer.objects.all()
        employees = Employee.objects.all()
        games = Game.objects.all()
        sony_accounts = SonyAccount.objects.all()

        status_choices = [
            {'value': value, 'label': label} for value, label in GameOrder._meta.get_field('status').choices
        ]

        response_data = {
            'customers': EmployeeCustomerSerializer(customers, many=True).data,
            'employees': EmployeeSerializer(employees, many=True).data,
            'games': EmployeeGameSerializer(games, many=True).data,
            'sony_accounts': EmployeeSonyAccountSerializer(sony_accounts, many=True).data,
            'status_choices': EmployeeStatusChoicesSerializer(status_choices, many=True).data,
        }

        return Response(response_data)


# ==================== RepairOrders Views ====================
@restrict_access('has_access_to_orders')
class EmployeePanelRepairOrderList(generics.ListAPIView):
    serializer_class = EmployeeRepairOrderSerializer
    queryset = Order.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


@restrict_access('has_access_to_orders')
class EmployeePanelRepairOrderDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeRepairOrderSerializer
    queryset = Order.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


@restrict_access('has_access_to_orders')
class EmployeePanelAddRepairOrder(generics.CreateAPIView):
    serializer_class = EmployeeRepairOrderSerializer
    queryset = Order.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


# ==================== Transactions Views ====================
@restrict_access('has_access_to_transactions')
class EmployeePanelTransactionList(generics.ListAPIView):
    queryset = Transaction.objects.filter(is_deleted=False)
    serializer_class = EmployeeTransactionSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TransactionFilter
    search_fields = ['description', 'payment_method', 'payer', 'receiver']
    ordering_fields = ['created_at', 'amount']


@restrict_access('has_access_to_transactions')
class EmployeePanelTransactionDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeTransactionSerializer
    queryset = Transaction.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    lookup_field = 'pk'


@restrict_access('has_access_to_transactions')
class EmployeePanelAddTransaction(generics.CreateAPIView):
    serializer_class = EmployeeTransactionSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    @transaction.atomic
    def perform_create(self, serializer):
        instance = serializer.save()

        payer = instance.payer
        receiver = instance.receiver
        amount = instance.amount
        payment_method = instance.payment_method

        try:
            main_manager = MainManager.objects.get(user=receiver or payer)
        except MainManager.DoesNotExist:
            main_manager = None

        if main_manager and receiver == main_manager.user:
            if payment_method:
                payment_method.balance += amount
                payment_method.save()
            main_manager.balance += amount
            main_manager.save()

        elif main_manager and payer == main_manager.user:
            if payment_method:
                if payment_method.balance < amount:
                    raise ValidationError("موجودی متود پرداخت کافی نیست.")
                payment_method.balance -= amount
                payment_method.save()

            if main_manager.balance < amount:
                raise ValidationError("موجودی مین منیجر کافی نیست.")
            main_manager.balance -= amount
            main_manager.save()

        if payer:
            try:
                customer = payer.customer
                customer.balance = min(0, customer.balance - amount)
                customer.save()
            except Customer.DoesNotExist:
                pass


class EmployeePanelIncomingTransactionView(generics.CreateAPIView):
    queryset = Transaction.objects.filter(is_deleted=False)
    serializer_class = EmployeeTransactionSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def perform_create(self, serializer):
        with db_transaction.atomic():
            try:
                main_manager = MainManager.objects.get(id=1)
                receiver = main_manager.user
            except MainManager.DoesNotExist:
                return Response(
                    {"detail": "MainManager با id=1 یافت نشد."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # بررسی اینکه payer یک مشتری باشد
            payer_id = self.request.data.get('payer')
            try:
                customer = Customer.objects.get(id=payer_id, is_deleted=False)
            except Customer.DoesNotExist:
                return Response(
                    {"detail": "پرداخت‌کننده باید یک مشتری باشد."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # دریافت payment_method
            payment_method_id = self.request.data.get('payment_method_id')
            try:
                payment_method = PaymentMethod.objects.get(id=payment_method_id, is_deleted=False)
            except PaymentMethod.DoesNotExist:
                return Response(
                    {"detail": "روش پرداخت معتبر نیست."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # آماده‌سازی داده‌های تراکنش
            transaction_data = {
                'payer': customer.user,
                'receiver': receiver,
                'in_out': True,
                'status': 'pending'
            }

            # افزودن سفارش مرتبط فقط در صورت وجود order_type و order_id
            order_type = self.request.data.get('order_type')
            order_id = self.request.data.get('order_id')
            if order_type and order_id:
                if order_type == 'order':
                    transaction_data['order'] = serializer.validated_data['order']
                elif order_type == 'game_order':
                    transaction_data['game_order'] = serializer.validated_data['game_order']
                elif order_type == 'repair_order':
                    transaction_data['repair_order'] = serializer.validated_data['repair_order']

            # ثبت تراکنش
            transaction = serializer.save(**transaction_data)

            # به‌روزرسانی موجودی‌ها
            payment_method.balance += transaction.amount
            customer.balance += transaction.amount
            payment_method.save()
            customer.save()

            # به‌روزرسانی وضعیت سفارش فقط در صورت وجود سفارش
            if order_type and order_id:
                if order_type == 'game_order' and transaction.game_order:
                    transaction.game_order.payment_status = 'paid'
                    transaction.game_order.save()
                elif order_type == 'repair_order' and transaction.repair_order:
                    transaction.repair_order.payment_status = 'paid'
                    transaction.repair_order.save()
                elif order_type == 'order' and transaction.order:
                    # مدل Order فیلد payment_status ندارد، در صورت نیاز منطق دیگری اضافه کنید
                    pass


@restrict_access('has_access_to_transactions')
class EmployeePanelTransactionChoices(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        customers = Customer.objects.all()
        employees = Employee.objects.all()
        game_orders = GameOrder.objects.all()
        repair_orders = RepairOrder.objects.all()
        orders = Order.objects.all()

        response_data = {
            'customers': EmployeeCustomerSerializer(customers, many=True).data,
            'employees': EmployeeSerializer(employees, many=True).data,
            'game_orders': EmployeeGameOrderSerializer(game_orders, many=True).data,
            'repair_orders': EmployeeRepairOrderSerializer(repair_orders, many=True).data,
            'orders': EmployeeProductOrderSerializer(orders, many=True).data,

        }
        return Response(response_data)


# ==================== Employees Views ====================
@restrict_access('has_access_to_add_users')
class UserCreat(generics.CreateAPIView):
    queryset = CustomUser.objects.filter(is_deleted=False)
    serializer_class = CustomUserSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


@restrict_access('has_access_to_employees')
class EmployeeListAdd(generics.ListCreateAPIView):
    queryset = Employee.objects.filter(is_deleted=False)
    serializer_class = EmployeeSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


@restrict_access('has_access_to_employees')
class EmployeeDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


# ==================== Customer Views ====================
@restrict_access('has_access_to_customers')
class CustomerListCreate(generics.ListCreateAPIView):
    serializer_class = EmployeeCustomerSerializer
    queryset = Customer.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


@restrict_access('has_access_to_customers')
class CustomerDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeCustomerSerializer
    queryset = Customer.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


# ==================== GameStore Views ====================
@restrict_access('has_access_to_site')
class EmployeeGameListCreate(generics.ListCreateAPIView):
    serializer_class = EmployeeGameSerializer
    queryset = Game.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


@restrict_access('has_access_to_site')
class EmployeeGameDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeGameSerializer
    queryset = Game.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


# ==================== Blog Views ====================
@restrict_access('has_access_to_site')
class EmployeeBlogListCreate(generics.ListCreateAPIView):
    serializer_class = EmployeeBlogSerializer
    queryset = BlogPost.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


@restrict_access('has_access_to_site')
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


class EmployeePanelDetail(generics.RetrieveUpdateDestroyAPIView):
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
