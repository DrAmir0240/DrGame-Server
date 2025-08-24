from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import transaction
from django.db.models import Sum
from django.utils.dateparse import parse_date
from rest_framework import serializers
from django.db import transaction as db_transaction
from accounts.models import CustomUser
from customers.models import Customer
from employees.models import EmployeeTask, Employee, Repairman, EmployeeFile, EmployeeRequest, EmployeeHire
from home.models import BlogPost
from payments.models import GameOrder, Transaction, Order, RepairOrder, PaymentMethod, OrderItem, GameOrderItem, \
    CourseOrder, RepairOrderType
from payments.serializers import DeliveryManSerializer
from storage.models import Game, SonyAccount, Product, ProductColor, ProductCategory, ProductCompany, \
    GameImage, DocCategory, Document, RealAssetsCategory, RealAssets, SonyAccountStatus, SonyAccountBank, \
    SonyAccountGame


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


class EmployeeFileSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = EmployeeFile
        exclude = ["employee"]


class EmployeeSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='phone',
        queryset=CustomUser.objects.all()
    )
    files = EmployeeFileSerializer(many=True, required=False)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = "__all__"

    def get_full_name(self, obj):
        return obj.first_name + " " + obj.last_name

    def create(self, validated_data):
        files_data = validated_data.pop('files', [])
        validated_data.pop('file_ids_to_delete', None)  # برای اطمینان

        employee = Employee.objects.create(**validated_data)

        for file_data in files_data:
            EmployeeFile.objects.create(employee=employee, **file_data)

        return employee

    def update(self, instance, validated_data):
        files_data = validated_data.pop('files', None)
        file_ids_to_delete = validated_data.pop('file_ids_to_delete', [])

        # آپدیت فیلدهای خود Employee
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # اضافه کردن فایل‌های جدید
        if files_data:
            for file_data in files_data:
                EmployeeFile.objects.create(employee=instance, **file_data)

        # حذف فایل‌ها
        if file_ids_to_delete:
            EmployeeFile.objects.filter(id__in=file_ids_to_delete, employee=instance).delete()

        return instance


class EmployeeHireSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeHire
        fields = "__all__"
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


class EmployeeDepositSerializer(SoftDeleteSerializerMixin, serializers.Serializer):
    payment_method_id = serializers.IntegerField()
    amount = serializers.IntegerField()
    description = serializers.CharField()


class SendSmsToEmployeeSerializer(serializers.Serializer):
    message = serializers.CharField()
    employee_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False
    )
    send_time = serializers.DateTimeField(required=False)


class SendSmsSerializer(serializers.Serializer):
    message = serializers.CharField()
    customer_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False
    )
    send_time = serializers.DateTimeField(required=False)


class EmployeeCustomerSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='phone',
        queryset=CustomUser.objects.all()
    )

    class Meta:
        model = Customer
        fields = "__all__"


class CustomerDepositSerializer(SoftDeleteSerializerMixin, serializers.Serializer):
    payment_method_id = serializers.IntegerField()
    amount = serializers.IntegerField()
    description = serializers.CharField(required=False, allow_blank=True)


class RepairmanDepositSerializer(SoftDeleteSerializerMixin, serializers.Serializer):
    payment_method_id = serializers.IntegerField()
    amount = serializers.IntegerField()
    description = serializers.CharField(required=False, allow_blank=True)


class EmployeeGameImageSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    # برای اینکه بتوانیم در آپدیت، id را از ورودی بخوانیم
    id = serializers.IntegerField(required=False)

    class Meta:
        model = GameImage
        # game را از ورودی حذف می‌کنیم؛ اتصال را خودمان انجام می‌دهیم
        exclude = ['game']


class EmployeeGameSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    game_images = EmployeeGameImageSerializer(many=True, required=False)

    class Meta:
        model = Game
        fields = "__all__"
        read_only_fields = ['is_deleted', 'created_at', 'updated_at']

    def create(self, validated_data):
        images_data = validated_data.pop('game_images', [])
        game = Game.objects.create(**validated_data)
        # ساخت تصاویر جدید (بدون نیاز به game در ورودی)
        for img_data in images_data:
            img_data.pop('id', None)  # ورودی id برای ساخت لازم نیست
            img_data.pop('game', None)  # امنیت بیشتر
            # اگر کاربر به اشتباه is_deleted=true فرستاد، ایجاد نکن
            if img_data.get('is_deleted'):
                continue
            GameImage.objects.create(game=game, **img_data)
        return game

    def update(self, instance, validated_data):
        images_data = validated_data.pop('game_images', None)

        # آپدیت فیلدهای خود Game
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if images_data is not None:
            # حذف همه عکس‌های قبلی
            instance.game_images.all().delete()
            # ساخت عکس‌های جدید
            for img_data in images_data:
                img_data.pop('id', None)
                img_data.pop('game', None)
                if img_data.get('is_deleted'):
                    continue
                GameImage.objects.create(game=instance, **img_data)

        return instance


class GameBulkPriceUpdateSerializer(serializers.Serializer):
    TYPE_CHOICES = [
        ('online_ps4', 'Online PS4'),
        ('online_ps5', 'Online PS5'),
        ('offline_ps4', 'Offline PS4'),
        ('offline_ps5', 'Offline PS5'),
        ('data_ps4', 'Data PS4'),
        ('data_ps5', 'Data PS5'),
        ('xbox', 'Xbox'),
        ('nintendo', 'Nintendo'),
    ]

    type = serializers.ChoiceField(choices=TYPE_CHOICES)
    price = serializers.IntegerField(min_value=0)

    def get_db_field(self):
        """
        تبدیل ورودی کاربر به اسم واقعی فیلد دیتابیس
        """
        type_map = {
            'online_ps4': 'online_ps4_price',
            'online_ps5': 'online_ps5_price',
            'offline_ps4': 'offline_ps4_price',
            'offline_ps5': 'offline_ps5_price',
            'data_ps4': 'data_ps4_price',
            'data_ps5': 'data_ps5_price',
            'xbox': 'xbox_price',
            'nintendo': 'nintendo_price',
        }
        return type_map[self.validated_data['type']]


class EmployeeBlogSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = "__all__"
        read_only_fields = ['created_at', 'updated_at']


class EmployeeSonyAccountBankSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = SonyAccountBank
        fields = "__all__"


class EmployeeSonyAccountStatusSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = SonyAccountStatus
        fields = "__all__"


class EmployeeSonyAccountSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()
    games = serializers.SlugRelatedField(many=True, read_only=True, slug_field='title')
    status_title = serializers.SerializerMethodField()
    game_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = SonyAccount
        fields = "__all__"
        read_only_fields = ['is_deleted', 'created_at', 'updated_at']

    def get_employee(self, obj):
        if obj.employee:
            return f"{obj.employee.first_name} {obj.employee.last_name}"
        return None

    def get_status_title(self, obj):
        if obj.status:
            return obj.status.title
        return None

    def update(self, instance, validated_data):
        game_ids = validated_data.pop("game_ids", None)

        # آپدیت فیلدهای معمولی
        instance = super().update(instance, validated_data)

        if game_ids is not None:
            from django.db import transaction
            with transaction.atomic():
                # همه‌ی بازی‌های قبلی این اکانت پاک میشن
                SonyAccountGame.objects.filter(sony_account=instance).delete()

                # بازی‌های جدید ست میشن
                for game_id in game_ids:
                    SonyAccountGame.objects.create(
                        sony_account=instance,
                        game_id=game_id
                    )

        return instance


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


class EmployeePersonalGameOrderItemSerializer(serializers.ModelSerializer):
    account_setter = serializers.SerializerMethodField()
    data_uploader = serializers.SerializerMethodField()
    game_order_customer = serializers.SerializerMethodField()

    class Meta:
        model = GameOrderItem
        fields = ["id", "game_order", "game_order_customer", "game", "account_setter", "data_uploader", "amount",
                  "created_at"]

    def get_account_setter(self, obj):
        if obj.account_setter:
            return obj.account_setter.first_name + " " + obj.account_setter.last_name
        return None

    def get_data_uploader(self, obj):
        if obj.data_uploader:
            return obj.data_uploader.first_name + " " + obj.data_uploader.last_name
        return None

    def get_game_order_customer(self, obj):
        return obj.game_order.customer.full_name


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


class EmployeePersonalTaskSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = EmployeeTask
        fields = ['id', 'title', 'voice', 'type', 'description', 'status', 'deadline', 'employee', 'created_at',
                  'updated_at']
        read_only_fields = ['employee', 'type', 'created_at', 'updated_at', 'is_deleted']

    def create(self, validated_data):
        employee = self.context['request'].user.employee
        validated_data['employee'] = employee
        validated_data['type'] = 'Personal'
        return super().create(validated_data)


class EmployeeOrganizeTaskSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = EmployeeTask
        fields = [
            'id', 'title', 'voice', 'type', 'description', 'status', 'deadline', 'employee',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['type', 'created_at', 'updated_at', 'is_deleted']

    def create(self, validated_data):
        validated_data['type'] = 'Organize'
        return super().create(validated_data)


class EmployeeOrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        source='product',
        queryset=Product.objects.filter(is_deleted=False)
    )
    quantity = serializers.IntegerField(min_value=1)

    # اینها فقط read_only هستن
    title = serializers.CharField(source='product.title', read_only=True)
    amount = serializers.DecimalField(source='product.price', max_digits=12, decimal_places=2, read_only=True)
    main_img = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['product_id', 'quantity', 'title', 'amount', 'main_img']

    def get_main_img(self, obj):
        request = self.context.get('request')
        if obj.product.main_img and hasattr(obj.product.main_img, 'url'):
            return request.build_absolute_uri(obj.product.main_img.url) if request else obj.product.main_img.url
        return None


class EmployeeProductOrderSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.filter(is_deleted=False)
    )
    order_items = EmployeeOrderItemSerializer(many=True)
    customer_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'customer_name', 'amount', 'order_type', 'description', 'payment_status',
            'order_items', 'created_at'
        ]
        read_only_fields = ['amount', 'order_type', 'is_deleted', 'updated_at', 'created_at']

    def get_customer_name(self, obj):
        return obj.customer.full_name if obj.customer else None

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        total_amount = 0

        # ساخت Order
        order = Order.objects.create(
            order_type="employee",
            **validated_data
        )

        # ساخت OrderItem ها
        for item in order_items_data:
            product = item['product']
            quantity = item['quantity']
            total_amount += product.price * quantity

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )

        order.amount = total_amount
        order.save()
        order.customer.balance -= order.amount
        order.customer.save()

        return order


class EmployeeGameOrderItemSerializer(serializers.ModelSerializer):
    game = serializers.CharField(source='game.title')
    account_setter = serializers.SerializerMethodField()
    data_uploader = serializers.SerializerMethodField()

    class Meta:
        model = GameOrderItem
        fields = ['game', 'account', 'data', 'amount', 'account_setter', 'data_uploader']

    def get_account_setter(self, obj):
        if obj.account_setter:
            return f"{obj.account_setter.first_name} {obj.account_setter.last_name}"
        return None

    def get_data_uploader(self, obj):
        if obj.data_uploader:
            return f"{obj.data_uploader.first_name} {obj.data_uploader.last_name}"
        return None


class EmployeeGameOrderItemWriteSerializer(serializers.Serializer):
    game = serializers.SlugRelatedField(slug_field='title', queryset=Game.objects.filter(is_deleted=False))
    account = serializers.BooleanField(required=False)
    data = serializers.BooleanField(required=False)
    account_setter = serializers.BooleanField(required=False, allow_null=True)
    data_uploader = serializers.BooleanField(required=False, allow_null=True)


class EmployeeGameOrderSerializer(serializers.ModelSerializer):
    customer = serializers.SlugRelatedField(slug_field='full_name',
                                            queryset=Customer.objects.filter(is_deleted=False))
    recipient = serializers.SerializerMethodField()
    employee = serializers.SerializerMethodField()

    class Meta:
        model = GameOrder
        fields = [
            'id', 'employee', 'customer', 'order_console_type', 'status', 'payment_status', 'console', 'dead_line',
            'games',
            'amount', 'recipient'
        ]

    def get_employee(self, obj):
        if obj.recipient:
            return f"{obj.recipient.first_name} {obj.recipient.last_name}"
        return None

    def get_recipient(self, obj):
        if obj.recipient:
            return f"{obj.recipient.first_name} {obj.recipient.last_name}"
        return None

    def get_game_price(self, game, order_console_type):
        field_map = {
            'online_ps4': game.online_ps4_price,
            'online_ps5': game.online_ps5_price,
            'offline_ps4': game.offline_ps4_price,
            'offline_ps5': game.offline_ps5_price,
            'data_ps4': game.data_ps4_price,
            'data_ps5': game.data_ps5_price,
            'xbox': game.xbox_price,
            'nintendo': game.nintendo_price,
        }

        price = field_map.get(order_console_type)
        if price is None:
            raise ValidationError(f"قیمت بازی '{game.title}' برای '{order_console_type}' تنظیم نشده است.")
        return price

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request', None)
        if request and request.method in ['POST', 'PATCH', 'PUT']:
            fields['games'] = EmployeeGameOrderItemWriteSerializer(many=True)
        else:
            fields['games'] = EmployeeGameOrderItemSerializer(many=True)
        return fields

    def create(self, validated_data):
        games_data = validated_data.pop('games')
        order_console_type = validated_data['order_console_type']
        customer = validated_data['customer']
        console = validated_data['console']
        dead_line = validated_data['dead_line']
        total_amount = 0
        game_order_items = []

        for game_item in games_data:
            game = game_item['game']
            price = self.get_game_price(game, order_console_type)
            total_amount += price
            game_order_items.append((game, price))

        game_order = GameOrder.objects.create(
            customer=customer,
            order_type='employee',
            order_console_type=order_console_type,
            status='delivered_to_drgame_and_in_waiting_queue',
            console=console,
            dead_line=dead_line,
            amount=total_amount,
            recipient=self.context['request'].user.employee
        )

        for game, price in game_order_items:
            GameOrderItem.objects.create(
                game_order=game_order,
                game=game,
                amount=price,
            )
        total_amount = total_amount * (customer.discount / 100)
        customer.balance -= total_amount
        customer.save()
        return game_order

    def update(self, instance, validated_data):
        print(instance.employee)
        request = self.context.get('request')
        old_amount = instance.amount  # مبلغ قبلی سفارش
        old_status = instance.status
        new_status = validated_data.get('status', old_status)

        # فقط وقتی status تغییر کرده
        if old_status != new_status:
            if new_status == 'done':
                validated_data['employee'] = instance.recipient
            else:
                validated_data['employee'] = request.user.employee

        # مدیریت games_data
        games_data = validated_data.pop('games', None)

        if games_data:
            for item_data in games_data:
                game = item_data['game']
                game_item_qs = GameOrderItem.objects.filter(
                    game_order=instance, game=game, is_deleted=False
                )
                if not game_item_qs.exists():
                    raise serializers.ValidationError(
                        f"آیتم مربوط به بازی '{game.title}' در این سفارش وجود ندارد."
                    )
                game_item = game_item_qs.first()

                if 'data' in item_data:
                    game_item.data = item_data['data']
                    request.user.employee.balance += game_item.amount
                    request.user.employee.save()
                if 'account' in item_data:
                    game_item.account = item_data['account']
                    request.user.employee.balance += game_item.amount
                    request.user.employee.save()
                if 'account_setter' in item_data and item_data['account_setter'] is True:
                    game_item.account_setter = request.user.employee
                if 'data_uploader' in item_data and item_data['data_uploader'] is True:
                    game_item.data_uploader = request.user.employee

                game_item.save()

        if old_status != new_status and new_status == 'done':
            instance.employee = instance.recipient or request.user.employee
            instance.save()

            for item in instance.games.filter(is_deleted=False):
                if item.account_setter and item.account_setter.commission_amount:
                    item.account_setter.balance += item.amount * (item.account_setter.commission_amount / 100)
                    item.account_setter.save()
                if item.data_uploader and item.data_uploader.commission_amount:
                    item.data_uploader.balance += item.amount * (item.data_uploader.commission_amount / 100)
                    item.data_uploader.save()

        new_amount = sum(item.amount for item in instance.games.filter(is_deleted=False))
        if new_amount != old_amount:
            # برگردوندن مبلغ قبلی به مشتری
            instance.customer.balance += old_amount * (instance.customer.discount / 100)
            # کم کردن مبلغ جدید
            instance.customer.balance -= new_amount * (instance.customer.discount / 100)
            instance.customer.save()
            instance.amount = new_amount
            instance.save()

        instance = super().update(instance, validated_data)
        print(instance.employee)
        return instance


class EmployeeStatusChoicesSerializer(serializers.Serializer):
    value = serializers.CharField(max_length=50)
    label = serializers.CharField(max_length=100)


class EmployeeRepairOrderSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = RepairOrder
        fields = "__all__"
        read_only_fields = ['is_deleted', 'created_at', 'updated_at']


class EmployeePaymentMethodSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
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


class EmployeeRealAssetsSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='title',
        queryset=RealAssetsCategory.objects.all()
    )

    class Meta:
        model = RealAssets
        fields = "__all__"
        read_only_fields = ['is_deleted', 'created_at', 'updated_at']


class EmployeeRealAssetsCategorySerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    real_assets = EmployeeRealAssetsSerializer(many=True, read_only=True)

    class Meta:
        model = RealAssetsCategory
        fields = "__all__"
        read_only_fields = ['is_deleted', 'created_at', 'updated_at']


class EmployeeCourseOrderSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()

    class Meta:
        model = CourseOrder
        fields = "__all__"
        read_only_fields = ['customer', 'amount', 'transaction', 'payment_status', 'is_deleted', 'created_at',
                            'updated_at']

    def get_customer(self, obj):
        return obj.customer.full_name


class RepairmanSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='phone',
        queryset=CustomUser.objects.all()
    )

    class Meta:
        model = Repairman
        fields = "__all__"


class RepairOrderTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairOrderType
        fields = '__all__'


class RepairManRepairOrderSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    order_type = serializers.SlugRelatedField(slug_field='title', read_only=True)
    delivery_to_drgame = DeliveryManSerializer(read_only=True)
    delivery_to_customer = DeliveryManSerializer(read_only=True)

    class Meta:
        model = RepairOrder
        fields = "__all__"
        read_only_fields = ['is_deleted', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        request = self.context.get("request")
        user = request.user

        new_status = validated_data.get("status", instance.status)

        # شرط 1: اگه سفارش تو صف پذیرش باشه و تعمیرکار بخواد آپدیتش کنه → ست بشه روی repair_man
        if instance.status == "in_accepting_queue" and new_status == "waiting_for_repairman_fee":
            instance.repair_man = user.repairman

        # شرط 2: اگه وضعیت از waiting_for_repairman_fee → waiting_for_amount تغییر کنه
        if instance.status == "waiting_for_repairman_fee" and new_status == "waiting_for_amount":
            repairman_fee = validated_data.get("repairman_fee")
            if not repairman_fee:
                raise serializers.ValidationError({
                    "repairman_fee": "برای تغییر وضعیت به 'waiting_for_amount' باید مبلغ تعمیرکار را وارد کنید."
                })
        # شرط 3: اگه وضعیت از waiting_for_amount → waiting_for_customer_to_accept تغییر کنه
        if instance.status == "waiting_for_amount" and new_status == "waiting_for_customer_to_accept":
            amount = validated_data.get("amount")
            if not amount:
                raise serializers.ValidationError({
                    "amount": "برای تغییر وضعیت به 'waiting_for_amount' باید مبلغ تعمیرکار را وارد کنید."
                })
        # شرط 4: اگه وضعیت شد in_progress → کم کردن مبلغ از موجودی مشتری
        if new_status == "in_progress" and instance.status != "in_progress":
            amount = instance.amount or validated_data.get("amount")
            customer = instance.customer

            if not amount:
                raise serializers.ValidationError({
                    "amount": "برای شروع سفارش باید مبلغ مشخص شده باشد."
                })
            customer.balance -= amount
            customer.save()

        if "amount" in validated_data:
            new_amount = validated_data.get("amount")
            if instance.amount != new_amount and instance.amount != 0:
                customer = instance.customer
                if instance.amount:
                    customer.balance += instance.amount

                customer.wallet_balance -= new_amount
                customer.save()

        if new_status == 'done' and instance.status == 'in_progress':
            instance.repair_man.balance += instance.repairman_fee
            instance.repair_man.save()

        return super().update(instance, validated_data)

    def create(self, validated_data):

        # وضعیت رو دیفالت دومین مقدار choices می‌ذاریم
        status_default = "in_accepting_queue"

        # ساخت سفارش
        order = RepairOrder.objects.create(
            customer=validated_data['customer'],
            console=validated_data['console'],
            description=validated_data['description'],
            status=status_default,  # دومی از choices
        )
        return order

    def get_customer_name(self, obj):
        if obj.customer:
            return obj.customer.full_name
        return None


class RepairManTransactionSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['amount', 'created_at', 'description']
        read_only_fields = fields


class EmployeeTaskStatsSerializer(serializers.Serializer):
    planed = serializers.IntegerField(read_only=True)
    in_progress = serializers.IntegerField(read_only=True)
    done = serializers.IntegerField(read_only=True)
    all = serializers.IntegerField(read_only=True)


class GameAndRepairOrderStatsSerializer(serializers.Serializer):
    by_order_type = serializers.DictField(child=serializers.IntegerField(), read_only=True)
    unpaid = serializers.IntegerField(read_only=True)
    delivered_to_customer = serializers.IntegerField(read_only=True)
    in_progress = serializers.IntegerField(read_only=True)


class OrderStatsSerializer(serializers.Serializer):
    employee = serializers.CharField(read_only=True)
    in_progress_orders = serializers.IntegerField(read_only=True, help_text="تعداد سفارشات در حال انجام")
    set_up_accounts = serializers.IntegerField(read_only=True, help_text="تعداد آیتم‌هایی که account_setter بوده")
    uploaded_data = serializers.IntegerField(read_only=True, help_text="تعداد آیتم‌هایی که data_uploader بوده")
    as_receptionist = serializers.IntegerField(read_only=True, help_text="تعداد سفارشاتی که رسپشن بوده")


class ProductOrderStatsSerializer(serializers.Serializer):
    by_order_type = serializers.DictField(child=serializers.IntegerField(), read_only=True)
    unpaid = serializers.IntegerField(read_only=True)
    paid = serializers.IntegerField(read_only=True)


class FinanceSummarySerializer(serializers.Serializer):
    total_employee_debt = serializers.IntegerField(help_text='بستانکاری از کارمندان')
    total_employee_credit = serializers.IntegerField(help_text='بدهکاری به کارمندان')
    total_customer_debt = serializers.IntegerField(help_text='بستانکاری از مشتریان')
    total_customer_credit = serializers.IntegerField(help_text='بدهکاری به مشتریان')
    total_payment_method_balance = serializers.IntegerField(help_text='مجموع موجودی')
    net_balance = serializers.IntegerField(help_text='تراز مالی خالص')


class EmployeeStatsSerializer(serializers.Serializer):
    account_setters = serializers.IntegerField()
    data_uploaders = serializers.IntegerField()
    recipients = serializers.IntegerField()
    mangers = serializers.IntegerField()
    all_employees = serializers.IntegerField()


class CustomerStatsSerializer(serializers.Serializer):
    business_customers = serializers.IntegerField()
    user_customers = serializers.IntegerField()
    customers = serializers.IntegerField()


class SellReportSerializer(serializers.Serializer):
    game_income = serializers.IntegerField()
    game_count = serializers.IntegerField()
    repair_income = serializers.IntegerField()
    repair_count = serializers.IntegerField()
    product_income = serializers.IntegerField()
    product_count = serializers.IntegerField()
    course_income = serializers.IntegerField()
    course_count = serializers.IntegerField()
    telegram_income = serializers.IntegerField()
    telegram_count = serializers.IntegerField()


class PaymentMethodReportSerializer(serializers.Serializer):
    title = serializers.CharField()
    balance = serializers.IntegerField()


class FinanceReportSerializer(serializers.Serializer):
    income_amount = serializers.IntegerField()
    outcome_amount = serializers.IntegerField()
    net_balance = serializers.IntegerField()
    balance = serializers.IntegerField()
    payment_methods = PaymentMethodReportSerializer(many=True)


class PerformanceReportSerializer(serializers.ModelSerializer):
    game_order_item_count_account = serializers.SerializerMethodField()
    game_order_item_count_data = serializers.SerializerMethodField()
    game_order_item_amount_sum = serializers.SerializerMethodField()
    employee_income_amount = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            'full_name',
            'game_order_item_count_account',
            'game_order_item_count_data',
            'game_order_item_amount_sum',
            'employee_income_amount'
        ]
        read_only_fields = fields

    def get_date_filters(self):
        """متد کمکی برای دریافت start-date و end-date از context"""
        request = self.context.get('request')
        start_date_str = request.GET.get('start-date')
        end_date_str = request.GET.get('end-date')
        start_date = parse_date(start_date_str) if start_date_str else None
        end_date = parse_date(end_date_str) if end_date_str else None
        filters = {}
        if start_date:
            filters['created_at__date__gte'] = start_date
        if end_date:
            filters['created_at__date__lte'] = end_date
        return filters

    def get_game_order_item_count_account(self, obj):
        filters = self.get_date_filters()
        return GameOrderItem.objects.filter(account_setter=obj, **filters).count()

    def get_game_order_item_count_data(self, obj):
        filters = self.get_date_filters()
        return GameOrderItem.objects.filter(data_uploader=obj, **filters).count()

    def get_game_order_item_amount_sum(self, obj):
        filters = self.get_date_filters()
        return GameOrderItem.objects.filter(account_setter=obj, **filters).aggregate(
            total=Sum('amount')
        )['total'] or 0

    def get_employee_income_amount(self, obj):
        filters = self.get_date_filters()
        return Transaction.objects.filter(receiver=obj.user, in_out=False, **filters).aggregate(
            total=Sum('amount')
        )['total'] or 0

    def get_full_name(self, obj):
        return str(obj)


class CustomerReportSerializer(serializers.ModelSerializer):
    game_order_count = serializers.SerializerMethodField()
    product_order_count = serializers.SerializerMethodField()
    repair_order_count = serializers.SerializerMethodField()
    customer_profit = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'full_name',
            'game_order_count',
            'product_order_count',
            'repair_order_count',
            'customer_profit'
        ]

    def get_date_filters(self):
        """کمک‌کننده برای فیلتر بر اساس start-date و end-date"""
        request = self.context.get('request')
        start_date_str = request.GET.get('start-date')
        end_date_str = request.GET.get('end-date')
        start_date = parse_date(start_date_str) if start_date_str else None
        end_date = parse_date(end_date_str) if end_date_str else None
        filters = {}
        if start_date:
            filters['created_at__date__gte'] = start_date
        if end_date:
            filters['created_at__date__lte'] = end_date
        return filters

    def get_game_order_count(self, obj):
        filters = self.get_date_filters()
        return GameOrder.objects.filter(
            customer=obj, is_deleted=False, payment_status='paid', **filters
        ).count()

    def get_product_order_count(self, obj):
        filters = self.get_date_filters()
        return Order.objects.filter(
            customer=obj, is_deleted=False, payment_status='paid', **filters
        ).count()

    def get_repair_order_count(self, obj):
        filters = self.get_date_filters()
        return RepairOrder.objects.filter(
            customer=obj, is_deleted=False, payment_status='paid', **filters
        ).count()

    def get_customer_profit(self, obj):
        filters = self.get_date_filters()
        return Transaction.objects.filter(
            payer=obj.user, in_out=True, is_deleted=False, status='paid', **filters
        ).aggregate(total=Sum('amount'))['total'] or 0


class EmployeeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeRequest
        fields = ['title', 'request_type', 'description', 'employee', 'created_at']
        read_only_fields = ['created_at', 'employee']
