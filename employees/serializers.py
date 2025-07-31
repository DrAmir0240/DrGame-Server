from rest_framework import serializers

from accounts.models import CustomUser
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

        order_type = attrs.get('order_type')
        order_id = attrs.get('order_id')
        if order_type or order_id:
            if not (order_type and order_id):
                raise serializers.ValidationError("هر دو فیلد order_type و order_id باید با هم ارائه شوند.")

            payer = attrs.get('payer')
            if not payer:
                raise serializers.ValidationError("پرداخت‌کننده باید مشخص باشد.")
            try:
                customer = Customer.objects.get(user=payer, is_deleted=False)
            except Customer.DoesNotExist:
                raise serializers.ValidationError("پرداخت‌کننده باید یک مشتری باشد.")

            if order_type == 'order':
                try:
                    order = Order.objects.get(id=order_id, is_deleted=False)
                    if order.customer != customer:
                        raise serializers.ValidationError("سفارش با مشتری مطابقت ندارد.")
                    attrs['order'] = order
                except Order.DoesNotExist:
                    raise serializers.ValidationError("سفارش یافت نشد.")
            elif order_type == 'game_order':
                try:
                    game_order = GameOrder.objects.get(id=order_id, is_deleted=False)
                    if game_order.customer != customer:
                        raise serializers.ValidationError("سفارش بازی با مشتری مطابقت ندارد.")
                    attrs['game_order'] = game_order
                except GameOrder.DoesNotExist:
                    raise serializers.ValidationError("سفارش بازی یافت نشد.")
            elif order_type == 'repair_order':
                try:
                    repair_order = RepairOrder.objects.get(id=order_id, is_deleted=False)
                    if repair_order.customer != customer:
                        raise serializers.ValidationError("سفارش تعمیر با مشتری مطابقت ندارد.")
                    attrs['repair_order'] = repair_order
                except RepairOrder.DoesNotExist:
                    raise serializers.ValidationError("سفارش تعمیر یافت نشد.")

        return attrs


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
