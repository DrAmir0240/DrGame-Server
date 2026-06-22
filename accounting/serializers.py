from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction as db_transaction
from rest_framework import serializers

from crm.models import Customer
from hr.models import Employee
from platform_settings.serializers import SoftDeleteSerializerMixin
from users.models import CustomUser
from website.models import CartItem, Cart, GAME_CART_TYPE
from accounting.models import Order, Transaction, Product, OrderItem, GameOrder, DeliveryMan, RepairOrder, CourseOrder, \
    GameOrderItem, GAME_ORDER_CONSOLE_TYPE, PaymentMethod
from inventory.serializers import GameSerializer


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'price']


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total_item_price = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_item_price']


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'cart_items', 'total_price']


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    customer = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = [
            'created_at', 'updated_at', 'is_deleted',
            'customer', 'order_type', 'amount', 'order_items'
        ]


class DeliveryManSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryMan
        fields = ['full_name', 'phone_number']


class GameOrderItemSerializer(serializers.ModelSerializer):
    game = GameSerializer(read_only=True)

    class Meta:
        model = GameOrderItem
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']


class GameOrderSerializer(serializers.ModelSerializer):
    games = GameOrderItemSerializer(many=True, read_only=True)
    delivery_to_drgame = DeliveryManSerializer(read_only=True)

    class Meta:
        model = GameOrder
        fields = '__all__'
        read_only_fields = [
            'customer', 'games', 'amount', 'status', 'order_type', 'delivery_to_drgame',
            'is_deleted', 'created_at', 'updated_at'
        ]


class GameOrderCreateSerializer(serializers.Serializer):
    console = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    type = serializers.ChoiceField(choices=GAME_CART_TYPE)


class RepairOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairOrder
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted', 'customer', 'order_type', 'amount',
                            'delivery_to_drgame', 'delivery_to_customer']


class CourseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseOrder
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'payer', 'receiver', 'amount', 'authority', 'ref_id', 'status', 'order', 'description',
                  'is_deleted', 'created_at', 'updated_at']
        read_only_fields = fields


class EmployeeDepositSerializer(SoftDeleteSerializerMixin, serializers.Serializer):
    payment_method_id = serializers.IntegerField()
    amount = serializers.IntegerField()
    description = serializers.CharField()


class CustomerDepositSerializer(SoftDeleteSerializerMixin, serializers.Serializer):
    payment_method_id = serializers.IntegerField()
    amount = serializers.IntegerField()
    description = serializers.CharField(required=False, allow_blank=True)


class RepairmanDepositSerializer(SoftDeleteSerializerMixin, serializers.Serializer):
    payment_method_id = serializers.IntegerField()
    amount = serializers.IntegerField()
    description = serializers.CharField(required=False, allow_blank=True)


class BalanceSerializer(serializers.Serializer):
    balance = serializers.IntegerField(read_only=True)


class EmployeeTransactionSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    payment_method_id = serializers.PrimaryKeyRelatedField(
        queryset=PaymentMethod.objects.filter(is_deleted=False), source='payment_method'
    )
    payer_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(is_deleted=False), source='payer', required=False
    )
    receiver_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(is_deleted=False), source='receiver', required=False
    )
    payer_customer = serializers.SerializerMethodField()
    receiver_employee = serializers.SerializerMethodField()
    payment_method = serializers.SerializerMethodField()
    order_type = serializers.ChoiceField(
        choices=[('order', 'Order'), ('game_order', 'GameOrder'), ('repair_order', 'RepairOrder')],
        required=False, allow_blank=True, allow_null=True
    )
    order_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'payment_method_id', 'payment_method',
            'payer_id', 'payer_customer',
            'receiver_id', 'receiver_employee',
            'amount', 'description',
            'in_out', 'status',
            'order_type', 'order_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'in_out', 'status', 'created_at', 'updated_at']

    def validate(self, attrs):
        if attrs.get('payer') and attrs.get('payer_str'):
            raise serializers.ValidationError("فقط یکی از payer یا payer_str باید مقدار داشته باشد.")
        if attrs.get('receiver') and attrs.get('receiver_str'):
            raise serializers.ValidationError("فقط یکی از receiver یا receiver_str باید مقدار داشته باشد.")
        return attrs

    def get_payer_customer(self, obj):
        customer = getattr(obj.payer, 'customer', None)
        if customer:
            return {
                'id': customer.id,
                'full_name': customer.full_name,
                'balance': customer.balance,
            }
        return None

    def get_receiver_employee(self, obj):
        employee = getattr(obj.receiver, 'employee', None)
        if employee:
            return {
                'id': employee.id,
                'full_name': employee.first_name + ' ' + employee.last_name,
                'position': employee.position if hasattr(employee, 'position') else None,
            }
        return None

    def get_payment_method(self, obj):
        if obj.payment_method_id:
            payment_method = PaymentMethod.objects.get(is_deleted=False, id=obj.payment_method_id)
            return {
                'payment_method': payment_method.title
            }
        return None


class EmployeeIncomingTransactionSerializer(serializers.ModelSerializer):
    payment_method_id = serializers.IntegerField(write_only=True)
    customer_id = serializers.IntegerField(required=False, write_only=True)
    payer_str = serializers.CharField(required=False, allow_blank=True)
    order_type = serializers.ChoiceField(choices=['order', 'game_order', 'repair_order'], write_only=True,
                                         required=False)
    order_id = serializers.IntegerField(required=False, write_only=True)
    amount = serializers.IntegerField(required=False)

    class Meta:
        model = Transaction
        fields = [
            'payment_method_id', 'customer_id', 'payer_str',
            'order_type', 'order_id', 'amount',
            'description', 'in_out'
        ]

    def validate(self, attrs):
        customer_id = attrs.get('customer_id')
        payer_str = attrs.get('payer_str')

        if customer_id and payer_str:
            raise serializers.ValidationError("یا customer_id یا payer_str را وارد کنید، نه هر دو.")

        if not customer_id and not payer_str:
            raise serializers.ValidationError("حداقل یکی از customer_id یا payer_str الزامی است.")

        return attrs

    def create(self, validated_data):
        with db_transaction.atomic():
            payment_method_id = validated_data.pop('payment_method_id')
            customer_id = validated_data.pop('customer_id', None)
            payer_str = validated_data.pop('payer_str', None)
            order_type = validated_data.pop('order_type', None)
            order_id = validated_data.pop('order_id', None)
            amount = validated_data.pop('amount', None)

            # گرفتن متود پرداخت
            try:
                payment_method = PaymentMethod.objects.get(id=payment_method_id, is_deleted=False)
            except PaymentMethod.DoesNotExist:
                raise serializers.ValidationError({"payment_method_id": "متود پرداخت پیدا نشد."})

            # گرفتن مشتری و یوزر
            user = None
            customer = None
            if customer_id:
                try:
                    customer = Customer.objects.get(id=customer_id, is_deleted=False)
                    user = customer.user
                except Customer.DoesNotExist:
                    raise serializers.ValidationError({"customer_id": "مشتری پیدا نشد."})

            # گرفتن سفارش و تنظیم مبلغ
            order_obj = None
            if order_type == 'order':
                order_obj = Order.objects.filter(id=order_id, is_deleted=False).first()
            elif order_type == 'game_order':
                order_obj = GameOrder.objects.filter(id=order_id, is_deleted=False).first()
            elif order_type == 'repair_order':
                order_obj = RepairOrder.objects.filter(id=order_id, is_deleted=False).first()

            if order_id and not order_obj:
                raise serializers.ValidationError({"order_id": "سفارشی با این مشخصات پیدا نشد."})

            if order_obj and not amount:
                amount = int(order_obj.amount)
            elif not amount:
                raise serializers.ValidationError({"amount": "مبلغ الزامی است اگر سفارشی انتخاب نشده باشد."})

            # ساخت تراکنش
            tx = Transaction.objects.create(
                payer=user if user else None,
                payer_str=None if user else payer_str,
                receiver=None,  # گیرنده مشخص نیست (می‌تونی مثلاً MainManager یا System باشه)
                receiver_str='دکتر گیم',
                payment_method=payment_method,
                amount=amount,
                in_out=True,
                description=validated_data.get("description", ""),
                status='paid'
            )

            # وصل کردن تراکنش به سفارش
            if order_obj:
                order_obj.transaction = tx
                order_obj.payment_status = 'paid'
                order_obj.save()

            # افزایش موجودی
            payment_method.balance += amount
            payment_method.save()

            if customer:
                customer.balance += amount
                customer.save()

            return tx


class EmployeesOutgoingTransactionSerializer(serializers.ModelSerializer):
    payment_method_id = serializers.IntegerField(write_only=True)
    employee_id = serializers.IntegerField(required=False, write_only=True)
    receiver_str = serializers.CharField(required=False, allow_blank=True)
    amount = serializers.IntegerField()
    receiver_info = serializers.SerializerMethodField()
    payment_method_title = serializers.CharField(source='payment_method.title', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'payment_method_id', 'employee_id', 'receiver_str',
            'amount', 'description',
            'receiver_info', 'payment_method_title'
        ]

    def validate(self, attrs):
        employee_id = attrs.get('employee_id')
        receiver_str = attrs.get('receiver_str')

        if employee_id and receiver_str:
            raise serializers.ValidationError("یا employee_id یا receiver_str را وارد کنید، نه هر دو.")

        if not employee_id and not receiver_str:
            raise serializers.ValidationError("حداقل یکی از employee_id یا receiver_str الزامی است.")

        return attrs

    def create(self, validated_data):
        with db_transaction.atomic():
            employee_id = validated_data.pop('employee_id', None)
            receiver_str = validated_data.pop('receiver_str', None)
            payment_method_id = validated_data.pop('payment_method_id')
            amount = validated_data.pop('amount')

            # بررسی و گرفتن متود پرداخت
            try:
                payment_method = PaymentMethod.objects.get(id=payment_method_id, is_deleted=False)
            except PaymentMethod.DoesNotExist:
                raise serializers.ValidationError({"payment_method_id": "متود پرداخت پیدا نشد."})

            # بررسی و گرفتن گیرنده
            receiver_user = None
            if employee_id:
                try:
                    employee = Employee.objects.get(id=employee_id)
                    receiver_user = employee.user
                except Employee.DoesNotExist:
                    raise serializers.ValidationError({"employee_id": "کارمند پیدا نشد."})

            # بررسی موجودی
            if payment_method.balance < amount:
                raise serializers.ValidationError("موجودی متود پرداخت کافی نیست.")

            # ساخت تراکنش
            tx = Transaction.objects.create(
                payer_str="دکتر گیم",
                receiver=receiver_user if receiver_user else None,
                receiver_str=receiver_str,
                payment_method=payment_method,
                amount=amount,
                in_out=False,
                description=validated_data.get('description', ''),
                status='paid'
            )

            # به‌روزرسانی موجودی‌ها
            payment_method.balance -= amount
            payment_method.save()

            if receiver_user and hasattr(receiver_user, 'employee'):
                receiver_user.employee.balance -= amount
                receiver_user.employee.save()

            return tx

    def get_receiver_info(self, obj):
        if obj.receiver:
            employee = getattr(obj.receiver, 'employee', None)
            if employee:
                return {
                    "id": employee.id,
                    "full_name": getattr(employee, 'full_name', obj.receiver.phone),
                    "phone": obj.receiver.phone,
                    "balance": employee.balance
                }
            return {
                "id": obj.receiver.id,
                "phone": obj.receiver.phone,
                "full_name": obj.receiver.phone
            }
        elif obj.receiver_str:
            return {"receiver_str": obj.receiver_str}
        return None


class CreateTransactionGenericSerializer(serializers.Serializer):
    payment_method = serializers.PrimaryKeyRelatedField(
        queryset=PaymentMethod.objects.filter(is_deleted=False),
        help_text="ID متود پرداخت"
    )
    description = serializers.CharField(
        required=False, allow_blank=True, help_text="توضیحات تراکنش"
    )

    # 1) تمام چک‌ها بیاد داخل validate
    def validate(self, attrs):
        model_class = self.context["model_class"]  # Order, GameOrder, RepairOrder
        object_id = self.context["object_id"]  # id سفارش
        object_field = self.context.get("amount_field", "amount")

        obj = model_class.objects.filter(id=object_id, is_deleted=False).first()
        if not obj:
            raise serializers.ValidationError({"error": "سفارش مورد نظر یافت نشد."})

        # اگر فیلد مبلغ وجود نداشته باشد یا مقدارش None باشد
        if not hasattr(obj, object_field):
            raise serializers.ValidationError({"error": f"فیلد مبلغ '{object_field}' در سفارش وجود ندارد."})

        amount = getattr(obj, object_field)
        if amount is None:
            raise serializers.ValidationError({"error": "سفارش مورد نظر هنوز تعیین قیمت نشده است."})

        # برای استفاده در create
        attrs["__obj"] = obj
        attrs["__amount"] = amount
        return attrs

    # 2) create فقط کار ساخت را انجام می‌دهد
    def create(self, validated_data):
        obj = validated_data.pop("__obj")
        amount = validated_data.pop("__amount")

        with db_transaction.atomic():
            transaction = Transaction.objects.create(
                payer=obj.customer.user if getattr(obj, "customer", None) else None,
                receiver_str="DrGame",
                payment_method=validated_data["payment_method"],
                amount=amount,
                description=validated_data.get("description", ""),
                in_out=True,
                status="pending"
            )

            obj.transaction = transaction
            obj.save(update_fields=["transaction"])

            pm = validated_data["payment_method"]
            pm.balance = (pm.balance or 0) + transaction.amount
            pm.save(update_fields=["balance"])

            if getattr(obj, "customer", None) and hasattr(obj.customer, "balance"):
                obj.customer.balance = (obj.customer.balance or 0) + transaction.amount
                obj.customer.save(update_fields=["balance"])

        return transaction

    # 3) نمایش امن بدون خطای رابطه‌های ناموجود
    def to_representation(self, instance):
        customer_balance = None
        try:
            # تلاش از مسیر سفارش‌های مرسوم
            for rel in ("repair", "order", "game_order"):
                related = getattr(instance, rel, None)  # اگر رابطه نباشد None
                if related and getattr(related, "customer", None):
                    customer_balance = getattr(related.customer, "balance", None)
                    break
        except ObjectDoesNotExist:
            customer_balance = None

        if customer_balance is None:
            # تلاش از مسیر payer -> customer (اگر چنین OneToOneای داشته باشید)
            try:
                if getattr(instance, "payer", None):
                    customer_obj = getattr(instance.payer, "customer", None)
                    if customer_obj:
                        customer_balance = getattr(customer_obj, "balance", None)
            except ObjectDoesNotExist:
                customer_balance = None

        return {
            "transaction_id": instance.id,
            "amount": instance.amount,
            "payment_method": instance.payment_method.title if instance.payment_method else None,
            "payment_method_balance": instance.payment_method.balance if instance.payment_method else None,
            "customer_balance": customer_balance,
            "description": instance.description,
            "status": instance.status,
        }


class EmployeePaymentMethodSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = "__all__"
        read_only_fields = ['is_deleted', 'created_at', 'updated_at']


class TransactionSearchSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    payer_name = serializers.SerializerMethodField()
    receiver_name = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id',
            'amount',
            'payer_name',
            'receiver_name',
            'type'
        ]

    def get_payer_name(self, obj):
        return obj.payer_str or (obj.payer.phone if obj.payer else None)

    def get_receiver_name(self, obj):
        return obj.receiver_str or (obj.receiver.phone if obj.receiver else None)

    def get_type(self, obj):
        return "transaction"
