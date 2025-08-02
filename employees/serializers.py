from django.db import transaction
from rest_framework import serializers

from accounts.models import CustomUser, MainManager
from customers.models import Customer
from employees.models import EmployeeTask, Employee
from home.models import BlogPost
from payments.models import GameOrder, Transaction, Order, RepairOrder, PaymentMethod
from storage.models import Game, SonyAccount, Product, ProductColor, ProductCategory, ProductCompany, \
    GameImage, DocCategory, Document


class SoftDeleteSerializerMixin:
    def destroy(self, instance):
        instance.is_deleted = True
        instance.save()
        return instance


class CustomUserSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['phone']
        read_only_fields = ['is_deleted', 'is_active', 'is_staff', 'is_superuser']


class EmployeeSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='phone',
        queryset=CustomUser.objects.all()
    )

    class Meta:
        model = Employee
        fields = "__all__"


class EmployeeCustomerSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='phone',
        queryset=CustomUser.objects.all()
    )

    class Meta:
        model = Customer
        fields = "__all__"


class EmployeeGameImageSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = GameImage
        fields = "__all__"


class EmployeeGameSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    game_images = EmployeeGameImageSerializer(many=True)

    class Meta:
        model = Game
        fields = "__all__"
        read_only_fields = ['is_deleted', 'created_at', 'updated_at']


class EmployeeBlogSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = "__all__"
        read_only_fields = ['created_at', 'updated_at']


class EmployeeSonyAccountMatchedSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    games = serializers.SlugRelatedField(many=True, read_only=True, slug_field='title')
    matching_games_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = SonyAccount
        fields = ['id', 'username', 'games', 'matching_games_count', 'region', 'created_at', 'updated_at']
        read_only_fields = ['is_deleted', 'created_at', 'updated_at']


class EmployeeSonyAccountSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()
    games = serializers.SlugRelatedField(many=True, read_only=True, slug_field='title')

    class Meta:
        model = SonyAccount
        fields = "__all__"
        read_only_fields = ['is_deleted', 'created_at', 'updated_at']

    def get_employee(self, obj):
        if obj.employee:
            return f"{obj.employee.first_name} {obj.employee.last_name}"
        return None


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
    order_type = serializers.ChoiceField(
        choices=[('order', 'Order'), ('game_order', 'GameOrder'), ('repair_order', 'RepairOrder')],
        required=False, allow_blank=True, allow_null=True
    )
    order_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'payment_method_id', 'payer_id', 'receiver_id', 'amount', 'description',
            'in_out', 'status', 'order_type', 'order_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'in_out', 'status', 'created_at', 'updated_at']

    def validate(self, attrs):
        if attrs.get('payer') and attrs.get('payer_str'):
            raise serializers.ValidationError("فقط یکی از payer یا payer_str باید مقدار داشته باشد.")
        if attrs.get('receiver') and attrs.get('receiver_str'):
            raise serializers.ValidationError("فقط یکی از receiver یا receiver_str باید مقدار داشته باشد.")
        return attrs


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
        with transaction.atomic():
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
        with transaction.atomic():
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


class EmployeeProductColorSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ProductColor
        fields = ['id', 'title']


class EmployeeProductCategorySerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'title']


class EmployeeProductCompanySerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ProductCompany
        fields = ['id', 'title']


class EmployeeProductSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ['is_deleted', 'created_at', 'updated_at', 'units_sold']


class EmployeeTaskSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = EmployeeTask
        fields = ['id', 'title', 'type', 'description', 'status', 'deadline', 'employee', 'created_at', 'updated_at']
        read_only_fields = ['employee', 'type', 'created_at', 'updated_at', 'is_deleted']

    def create(self, validated_data):
        employee = self.context['request'].user.employee
        validated_data['employee'] = employee
        validated_data['type'] = 'Personal'
        return super().create(validated_data)


class EmployeeProductOrderSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    order_type = serializers.SlugRelatedField(read_only=True, slug_field='title')
    customer = serializers.SlugRelatedField(read_only=True, slug_field='full_name')
    product = EmployeeProductSerializer()

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = ['is_deleted', 'created_at', 'updated_at']


class EmployeeGameOrderSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    games = serializers.SlugRelatedField(slug_field='title', many=True, queryset=Game.objects.filter(is_deleted=False))

    class Meta:
        model = GameOrder
        fields = "__all__"
        read_only_fields = ['is_deleted', 'created_at', 'updated_at']


class EmployeeStatusChoicesSerializer(serializers.Serializer):
    value = serializers.CharField(max_length=50)
    label = serializers.CharField(max_length=100)


class EmployeeRepairOrderSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = RepairOrder
        fields = "__all__"
        read_only_fields = ['is_deleted', 'created_at', 'updated_at']


class EmployeeDocsSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='title',
        queryset=DocCategory.objects.all()
    )

    class Meta:
        model = Document
        fields = "__all__"
        read_only_fields = ['is_deleted', 'created_at', 'updated_at']


class EmployeeDocCategorySerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    docs = EmployeeDocsSerializer(many=True, read_only=True)

    class Meta:
        model = DocCategory
        fields = "__all__"
        read_only_fields = ['is_deleted', 'created_at', 'updated_at']
