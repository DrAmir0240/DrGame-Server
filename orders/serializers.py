from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction
from rest_framework import serializers

''' LEGACY — commented out after the accounting restructure removed these models
(Order, GameOrder, OrderItem, GameOrderItem, TelegramOrder, RepairOrder, CourseOrder,
RepairOrderType). Dead code: nothing imports these classes and their URLs are disabled.

from accounting.models import GameOrderItem, OrderItem, Order, GameOrder, TelegramOrder, RepairOrder, CourseOrder, \
    RepairOrderType
from crm.models import Customer
from inventory.models import Product, Game
from platform_settings.serializers import SoftDeleteSerializerMixin


class EmployeePersonalGameOrderItemSerializer(
    serializers.ModelSerializer):
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
        request = self.context['request']
        current_employee = request.user.employee

        old_status = instance.status
        new_status = validated_data.get('status', old_status)

        games_data = validated_data.pop('games', [])

        with db_transaction.atomic():

            # ---------- GameOrderItem logic ----------
            for item_data in games_data:
                game = item_data['game']
                item = GameOrderItem.objects.select_for_update().get(
                    game_order=instance,
                    game=game,
                    is_deleted=False
                )

                # account setter
                if item_data.get('account') is True and not item.account_setter:
                    item.account = True
                    item.account_setter = current_employee
                    item.save()

                # data uploader
                if item_data.get('data') is True and not item.data_uploader:
                    item.data = True
                    item.data_uploader = current_employee
                    item.save()

            # ---------- status change logic ----------
            if old_status != new_status:

                # رسپشن: تحویل به دکتر گیم
                if (
                        old_status == 'delivered_to_drgame_and_in_waiting_queue'
                        and new_status == 'delivered_to_drgame'
                ):
                    instance.recipient = current_employee

                # پورسانت‌ها: انتظار تحویل به مشتری
                if new_status == 'done':
                    for item in instance.games.filter(is_deleted=False):

                        if item.account_setter and item.account_setter.has_commission == True:
                            print(f'account setter old balance :{item.account_setter.balance}')
                            commission = (
                                                 item.amount * item.account_setter.commission_amount
                                         ) / 100
                            item.account_setter.balance += commission
                            print(f'account setter new balance :{item.account_setter.balance}')
                            item.account_setter.save()

                        if item.data_uploader and item.data_uploader.has_commission == True:
                            print(f'data uploader old balance :{item.data_uploader.balance}')
                            commission = (
                                                 item.amount * item.data_uploader.commission_amount
                                         ) / 100
                            item.data_uploader.balance += commission
                            print(f'data uploader new balance :{item.data_uploader.balance}')
                            item.data_uploader.save()

            # ---------- last operator ----------
            instance.employee = current_employee

            # ---------- update amount ----------
            new_amount = sum(
                item.amount for item in instance.games.filter(is_deleted=False)
            )
            instance.amount = new_amount

            instance = super().update(instance, validated_data)

        return instance


class EmployeeTelegramOrderSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField(read_only=True)
    sony_account_game_list = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TelegramOrder
        fields = "__all__"
        read_only_fields = ['is_deleted', 'created_at', 'updated_at']

    def get_employee_name(self, obj):
        if obj.employee:
            return obj.employee.first_name + " " + obj.employee.last_name
        return None

    def get_sony_account_game_list(self, obj):
        game_list = [game.title for game in obj.sony_account.games.all()]
        return game_list


class EmployeeRepairOrderSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = RepairOrder
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

class RepairOrderTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairOrderType
        fields = '__all__'
'''  # END LEGACY


# =============================================================================
# =============================================================================
# ORDERS WORKFLOW (stage/action engine) — Sony Account / Repair / Product
# =============================================================================
# =============================================================================

from drf_spectacular.utils import extend_schema_field
from hr.serializers import EmployeeRoleListSerializer
from crm.serializers import CustomerListSerializer
from orders.models import (
    SonyAccountOrderCategory, SonyAccountOrderStage, SonyAccountOrderStageAction,
    SonyAccountOrder, SonyAccountOrderItem, SonyAccountOrderConsole,
    SonyAccountOrderActionLog, SonyAccountOrderStageLog,
    RepairOrderCategory, RepairOrderStage, RepairOrderStageAction,
    RepairOrder, RepairOrderDevice, RepairOrderActionLog, RepairOrderStageLog,
    ProductOrderCategory, ProductOrderStage, ProductOrderStageAction,
    ProductOrder, ProductOrderItem, ProductOrderActionLog, ProductOrderStageLog,
)


def _employee_name(employee):
    if employee:
        return f'{employee.first_name} {employee.last_name}'
    return None


# =============================================================================
# SECTION 1 — SONY ACCOUNT ORDER
# =============================================================================

# --- 1.a Category ---
class SonyAccountOrderCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SonyAccountOrderCategory
        fields = ['id', 'title', 'type', 'account_capacity', 'rent_time_days']


class SonyAccountOrderCategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SonyAccountOrderCategory
        fields = '__all__'


# --- 1.b Stage Action ---
class SonyAccountOrderStageActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SonyAccountOrderStageAction
        fields = [
            'id', 'stage', 'title', 'action_type', 'description',
            'is_required', 'order', 'target_field'
        ]

    def validate(self, attrs):
        action_type = attrs.get('action_type', getattr(self.instance, 'action_type', None))
        target_field = attrs.get('target_field', getattr(self.instance, 'target_field', ''))

        if action_type in ('update_order_field', 'update_order_item_field') and not target_field:
            raise serializers.ValidationError(
                {'target_field': 'این فیلد برای این نوع اکشن الزامی است.'}
            )

        # مطابق مدل‌های فعلی پروژه — is_done روی آیتم وجود ندارد
        VALID_ORDER_FIELDS = {'description'}
        VALID_ITEM_FIELDS = {'sony_account'}

        if action_type == 'update_order_field' and target_field not in VALID_ORDER_FIELDS:
            raise serializers.ValidationError(
                {'target_field': f'مقدار مجاز: {VALID_ORDER_FIELDS}'}
            )

        if action_type == 'update_order_item_field' and target_field not in VALID_ITEM_FIELDS:
            raise serializers.ValidationError(
                {'target_field': f'مقدار مجاز: {VALID_ITEM_FIELDS}'}
            )

        return attrs


# --- 1.c Stage ---
class SonyAccountOrderStageListSerializer(serializers.ModelSerializer):
    employee_role_detail = EmployeeRoleListSerializer(source='employee_role', read_only=True)

    class Meta:
        model = SonyAccountOrderStage
        fields = [
            'id', 'title', 'order', 'is_start', 'is_end',
            'employee_role', 'employee_role_detail'
        ]


class SonyAccountOrderStageDetailSerializer(serializers.ModelSerializer):
    actions = serializers.SerializerMethodField()
    employee_role_detail = EmployeeRoleListSerializer(source='employee_role', read_only=True)

    class Meta:
        model = SonyAccountOrderStage
        fields = [
            'id', 'category', 'title', 'description', 'order',
            'is_start', 'is_end',
            'employee_role', 'employee_role_detail',
            'actions', 'created_at', 'updated_at'
        ]

    @extend_schema_field(SonyAccountOrderStageActionSerializer(many=True))
    def get_actions(self, obj):
        actions = obj.actions.filter(is_deleted=False)
        return SonyAccountOrderStageActionSerializer(actions, many=True).data


# --- 1.d Nested (items / consoles / logs) ---
class SonyAccountOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SonyAccountOrderItem
        fields = ['id', 'sony_account_order', 'sony_account', 'employee', 'created_at']


class SonyAccountOrderConsoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SonyAccountOrderConsole
        fields = ['id', 'customer', 'sony_account_order', 'serial_number', 'created_at']


class SonyAccountOrderActionLogSerializer(serializers.ModelSerializer):
    action_title = serializers.CharField(source='action.title', read_only=True)
    performed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = SonyAccountOrderActionLog
        fields = ['id', 'action', 'action_title', 'performed_by', 'performed_by_name', 'note', 'created_at']

    def get_performed_by_name(self, obj) -> str:
        return _employee_name(obj.performed_by)


class SonyAccountOrderStageLogSerializer(serializers.ModelSerializer):
    from_stage_title = serializers.CharField(source='from_stage.title', read_only=True)
    to_stage_title = serializers.CharField(source='to_stage.title', read_only=True)
    changed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = SonyAccountOrderStageLog
        fields = [
            'id', 'from_stage', 'from_stage_title', 'to_stage', 'to_stage_title',
            'changed_by', 'changed_by_name', 'note', 'created_at'
        ]

    def get_changed_by_name(self, obj) -> str:
        return _employee_name(obj.changed_by)


# --- 1.e Worker panel ---
class SonyAccountOrderStageQueueSerializer(serializers.ModelSerializer):
    category_id    = serializers.IntegerField(source='category.id', read_only=True)
    category_title = serializers.CharField(source='category.title', read_only=True)

    class Meta:
        model  = SonyAccountOrderStage
        fields = ['id', 'title', 'order', 'category_id', 'category_title']


class SonyAccountOrderCardSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    category_title = serializers.CharField(source='category.title', read_only=True)
    stage_title = serializers.CharField(source='stage.title', read_only=True)
    pending_actions_count = serializers.SerializerMethodField()

    class Meta:
        model = SonyAccountOrder
        fields = [
            'id', 'customer_name', 'category_title',
            'stage_title', 'source', 'type',
            'amount', 'pending_actions_count', 'created_at'
        ]

    def get_customer_name(self, obj) -> str:
        return obj.customer.user.full_name() if obj.customer else None

    def get_pending_actions_count(self, obj) -> int:
        if not obj.stage:
            return 0
        completed_ids = obj.action_logs.filter(
            action__stage=obj.stage
        ).values_list('action_id', flat=True)
        return obj.stage.actions.filter(
            is_required=True, is_deleted=False
        ).exclude(id__in=completed_ids).count()


class SonyAccountOrderDetailSerializer(serializers.ModelSerializer):
    customer_detail = CustomerListSerializer(source='customer', read_only=True)
    category_detail = SonyAccountOrderCategoryListSerializer(source='category', read_only=True)
    stage_detail = SonyAccountOrderStageDetailSerializer(source='stage', read_only=True)
    items = serializers.SerializerMethodField()
    consoles = serializers.SerializerMethodField()
    action_logs = serializers.SerializerMethodField()
    stage_logs = serializers.SerializerMethodField()

    class Meta:
        model = SonyAccountOrder
        fields = [
            'id', 'customer', 'customer_detail',
            'category', 'category_detail',
            'stage', 'stage_detail',
            'source', 'type', 'amount',
            'items', 'consoles',
            'action_logs', 'stage_logs',
            'created_at', 'updated_at'
        ]

    @extend_schema_field(SonyAccountOrderItemSerializer(many=True))
    def get_items(self, obj):
        qs = obj.items.filter(is_deleted=False)
        return SonyAccountOrderItemSerializer(qs, many=True).data

    @extend_schema_field(SonyAccountOrderConsoleSerializer(many=True))
    def get_consoles(self, obj):
        qs = obj.consoles.filter(is_deleted=False)
        return SonyAccountOrderConsoleSerializer(qs, many=True).data

    @extend_schema_field(SonyAccountOrderActionLogSerializer(many=True))
    def get_action_logs(self, obj):
        qs = obj.action_logs.filter(is_deleted=False).order_by('-created_at')
        return SonyAccountOrderActionLogSerializer(qs, many=True).data

    @extend_schema_field(SonyAccountOrderStageLogSerializer(many=True))
    def get_stage_logs(self, obj):
        qs = obj.stage_logs.filter(is_deleted=False).order_by('-created_at')
        return SonyAccountOrderStageLogSerializer(qs, many=True).data


class SonyAccountOrderActionSerializer(serializers.ModelSerializer):
    is_done = serializers.SerializerMethodField()

    class Meta:
        model = SonyAccountOrderStageAction
        fields = [
            'id', 'title', 'action_type',
            'target_field', 'is_required',
            'order', 'is_done'
        ]

    def get_is_done(self, obj) -> bool:
        order_id = self.context.get('order_id')
        if not order_id:
            return False
        return SonyAccountOrderActionLog.objects.filter(
            order_id=order_id, action=obj
        ).exists()


# =============================================================================
# SECTION 2 — REPAIR ORDER
# =============================================================================

# --- 2.a Category ---
class RepairOrderCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairOrderCategory
        fields = ['id', 'title', 'description']


class RepairOrderCategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairOrderCategory
        fields = '__all__'
        read_only_fields = ['is_deleted', 'created_at', 'updated_at']


# --- 2.b Stage Action ---
class RepairOrderStageActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairOrderStageAction
        fields = [
            'id', 'stage', 'title', 'action_type', 'description',
            'is_required', 'order', 'target_field'
        ]

    def validate(self, attrs):
        action_type = attrs.get('action_type', getattr(self.instance, 'action_type', None))
        target_field = attrs.get('target_field', getattr(self.instance, 'target_field', ''))

        # is_done روی RepairOrderDevice وجود ندارد → update_order_item_field بدون فیلد مجاز است
        VALID_ORDER_FIELDS = {'description', 'repair_fee', 'final_amount'}
        VALID_ITEM_FIELDS = set()

        if action_type == 'update_order_item_field':
            raise serializers.ValidationError(
                {'action_type': 'برای سفارش تعمیر آپدیت فیلد آیتم پشتیبانی نمی‌شود.'}
            )

        if action_type == 'update_order_field':
            if not target_field:
                raise serializers.ValidationError(
                    {'target_field': 'این فیلد برای این نوع اکشن الزامی است.'}
                )
            if target_field not in VALID_ORDER_FIELDS:
                raise serializers.ValidationError(
                    {'target_field': f'مقدار مجاز: {VALID_ORDER_FIELDS}'}
                )

        return attrs


# --- 2.c Stage ---
class RepairOrderStageListSerializer(serializers.ModelSerializer):
    employee_role_detail = EmployeeRoleListSerializer(source='employee_role', read_only=True)

    class Meta:
        model = RepairOrderStage
        fields = [
            'id', 'title', 'order', 'is_start', 'is_end',
            'employee_role', 'employee_role_detail'
        ]


class RepairOrderStageDetailSerializer(serializers.ModelSerializer):
    actions = serializers.SerializerMethodField()
    employee_role_detail = EmployeeRoleListSerializer(source='employee_role', read_only=True)

    class Meta:
        model = RepairOrderStage
        fields = [
            'id', 'category', 'title', 'description', 'order',
            'is_start', 'is_end',
            'employee_role', 'employee_role_detail',
            'actions', 'created_at', 'updated_at'
        ]

    @extend_schema_field(RepairOrderStageActionSerializer(many=True))
    def get_actions(self, obj):
        actions = obj.actions.filter(is_deleted=False)
        return RepairOrderStageActionSerializer(actions, many=True).data


# --- 2.d Nested (devices / logs) ---
class RepairOrderDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairOrderDevice
        fields = ['id', 'customer', 'repair_order', 'title', 'serial_number', 'created_at']


class RepairOrderActionLogSerializer(serializers.ModelSerializer):
    action_title = serializers.CharField(source='action.title', read_only=True)
    performed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = RepairOrderActionLog
        fields = ['id', 'action', 'action_title', 'performed_by', 'performed_by_name', 'note', 'created_at']

    def get_performed_by_name(self, obj) -> str:
        return _employee_name(obj.performed_by)


class RepairOrderStageLogSerializer(serializers.ModelSerializer):
    from_stage_title = serializers.CharField(source='from_stage.title', read_only=True)
    to_stage_title = serializers.CharField(source='to_stage.title', read_only=True)
    changed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = RepairOrderStageLog
        fields = [
            'id', 'from_stage', 'from_stage_title', 'to_stage', 'to_stage_title',
            'changed_by', 'changed_by_name', 'note', 'created_at'
        ]

    def get_changed_by_name(self, obj) -> str:
        return _employee_name(obj.changed_by)


# --- 2.e Worker panel ---
class RepairOrderStageQueueSerializer(serializers.ModelSerializer):
    category_id    = serializers.IntegerField(source='category.id', read_only=True)
    category_title = serializers.CharField(source='category.title', read_only=True)

    class Meta:
        model  = RepairOrderStage
        fields = ['id', 'title', 'order', 'category_id', 'category_title']


class RepairOrderCardSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    category_title = serializers.CharField(source='category.title', read_only=True)
    stage_title = serializers.CharField(source='stage.title', read_only=True)
    pending_actions_count = serializers.SerializerMethodField()

    class Meta:
        model = RepairOrder
        fields = [
            'id', 'customer_name', 'category_title', 'stage_title',
            'repair_fee', 'final_amount', 'pending_actions_count', 'created_at'
        ]

    def get_customer_name(self, obj) -> str:
        return obj.customer.user.full_name() if obj.customer else None

    def get_pending_actions_count(self, obj) -> int:
        if not obj.stage:
            return 0
        completed_ids = obj.action_logs.filter(
            action__stage=obj.stage
        ).values_list('action_id', flat=True)
        return obj.stage.actions.filter(
            is_required=True, is_deleted=False
        ).exclude(id__in=completed_ids).count()


class RepairOrderDetailSerializer(serializers.ModelSerializer):
    customer_detail = CustomerListSerializer(source='customer', read_only=True)
    category_detail = RepairOrderCategoryListSerializer(source='category', read_only=True)
    stage_detail = RepairOrderStageDetailSerializer(source='stage', read_only=True)
    devices = serializers.SerializerMethodField()
    action_logs = serializers.SerializerMethodField()
    stage_logs = serializers.SerializerMethodField()

    class Meta:
        model = RepairOrder
        fields = [
            'id', 'customer', 'customer_detail',
            'category', 'category_detail',
            'stage', 'stage_detail',
            'repair_fee', 'final_amount',
            'devices', 'action_logs', 'stage_logs',
            'created_at', 'updated_at'
        ]

    @extend_schema_field(RepairOrderDeviceSerializer(many=True))
    def get_devices(self, obj):
        qs = obj.devices.filter(is_deleted=False)
        return RepairOrderDeviceSerializer(qs, many=True).data

    @extend_schema_field(RepairOrderActionLogSerializer(many=True))
    def get_action_logs(self, obj):
        qs = obj.action_logs.filter(is_deleted=False).order_by('-created_at')
        return RepairOrderActionLogSerializer(qs, many=True).data

    @extend_schema_field(RepairOrderStageLogSerializer(many=True))
    def get_stage_logs(self, obj):
        qs = obj.stage_logs.filter(is_deleted=False).order_by('-created_at')
        return RepairOrderStageLogSerializer(qs, many=True).data


class RepairOrderActionSerializer(serializers.ModelSerializer):
    is_done = serializers.SerializerMethodField()

    class Meta:
        model = RepairOrderStageAction
        fields = [
            'id', 'title', 'action_type',
            'target_field', 'is_required',
            'order', 'is_done'
        ]

    def get_is_done(self, obj) -> bool:
        order_id = self.context.get('order_id')
        if not order_id:
            return False
        return RepairOrderActionLog.objects.filter(
            order_id=order_id, action=obj
        ).exists()


# =============================================================================
# SECTION 3 — PRODUCT ORDER
# =============================================================================

# --- 3.a Category ---
class ProductOrderCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOrderCategory
        fields = ['id', 'title', 'description']


class ProductOrderCategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOrderCategory
        fields = '__all__'


# --- 3.b Stage Action ---
class ProductOrderStageActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOrderStageAction
        fields = [
            'id', 'stage', 'title', 'action_type', 'description',
            'is_required', 'order', 'target_field'
        ]

    def validate(self, attrs):
        action_type = attrs.get('action_type', getattr(self.instance, 'action_type', None))
        target_field = attrs.get('target_field', getattr(self.instance, 'target_field', ''))

        # is_done روی ProductOrderItem وجود ندارد → update_order_item_field بدون فیلد مجاز است
        VALID_ORDER_FIELDS = {'description'}

        if action_type == 'update_order_item_field':
            raise serializers.ValidationError(
                {'action_type': 'برای سفارش محصول آپدیت فیلد آیتم پشتیبانی نمی‌شود.'}
            )

        if action_type == 'update_order_field':
            if not target_field:
                raise serializers.ValidationError(
                    {'target_field': 'این فیلد برای این نوع اکشن الزامی است.'}
                )
            if target_field not in VALID_ORDER_FIELDS:
                raise serializers.ValidationError(
                    {'target_field': f'مقدار مجاز: {VALID_ORDER_FIELDS}'}
                )

        return attrs


# --- 3.c Stage ---
class ProductOrderStageListSerializer(serializers.ModelSerializer):
    employee_role_detail = EmployeeRoleListSerializer(source='employee_role', read_only=True)

    class Meta:
        model = ProductOrderStage
        fields = [
            'id', 'title', 'order', 'is_start', 'is_end',
            'employee_role', 'employee_role_detail'
        ]


class ProductOrderStageDetailSerializer(serializers.ModelSerializer):
    actions = serializers.SerializerMethodField()
    employee_role_detail = EmployeeRoleListSerializer(source='employee_role', read_only=True)

    class Meta:
        model = ProductOrderStage
        fields = [
            'id', 'category', 'title', 'description', 'order',
            'is_start', 'is_end',
            'employee_role', 'employee_role_detail',
            'actions', 'created_at', 'updated_at'
        ]

    @extend_schema_field(ProductOrderStageActionSerializer(many=True))
    def get_actions(self, obj):
        actions = obj.actions.filter(is_deleted=False)
        return ProductOrderStageActionSerializer(actions, many=True).data


# --- 3.d Nested (items / logs) ---
class ProductOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOrderItem
        fields = ['id', 'product_order', 'product', 'title', 'unit_price', 'amount', 'created_at']


class ProductOrderActionLogSerializer(serializers.ModelSerializer):
    action_title = serializers.CharField(source='action.title', read_only=True)
    performed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ProductOrderActionLog
        fields = ['id', 'action', 'action_title', 'performed_by', 'performed_by_name', 'note', 'created_at']

    def get_performed_by_name(self, obj) -> str:
        return _employee_name(obj.performed_by)


class ProductOrderStageLogSerializer(serializers.ModelSerializer):
    from_stage_title = serializers.CharField(source='from_stage.title', read_only=True)
    to_stage_title = serializers.CharField(source='to_stage.title', read_only=True)
    changed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ProductOrderStageLog
        fields = [
            'id', 'from_stage', 'from_stage_title', 'to_stage', 'to_stage_title',
            'changed_by', 'changed_by_name', 'note', 'created_at'
        ]

    def get_changed_by_name(self, obj) -> str:
        return _employee_name(obj.changed_by)


# --- 3.e Worker panel ---
class ProductOrderStageQueueSerializer(serializers.ModelSerializer):
    category_id    = serializers.IntegerField(source='category.id', read_only=True)
    category_title = serializers.CharField(source='category.title', read_only=True)

    class Meta:
        model  = ProductOrderStage
        fields = ['id', 'title', 'order', 'category_id', 'category_title']


class ProductOrderCardSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    stage_title = serializers.CharField(source='stage.title', read_only=True)
    pending_actions_count = serializers.SerializerMethodField()

    class Meta:
        model = ProductOrder
        fields = [
            'id', 'customer_name', 'stage_title',
            'amount', 'pending_actions_count', 'created_at'
        ]

    def get_customer_name(self, obj) -> str:
        return obj.customer.user.full_name() if obj.customer else None

    def get_pending_actions_count(self, obj) -> int:
        if not obj.stage:
            return 0
        completed_ids = obj.action_logs.filter(
            action__stage=obj.stage
        ).values_list('action_id', flat=True)
        return obj.stage.actions.filter(
            is_required=True, is_deleted=False
        ).exclude(id__in=completed_ids).count()


class ProductOrderDetailSerializer(serializers.ModelSerializer):
    customer_detail = CustomerListSerializer(source='customer', read_only=True)
    stage_detail = ProductOrderStageDetailSerializer(source='stage', read_only=True)
    items = serializers.SerializerMethodField()
    action_logs = serializers.SerializerMethodField()
    stage_logs = serializers.SerializerMethodField()

    class Meta:
        model = ProductOrder
        fields = [
            'id', 'customer', 'customer_detail',
            'stage', 'stage_detail',
            'description', 'amount',
            'items', 'action_logs', 'stage_logs',
            'created_at', 'updated_at'
        ]

    @extend_schema_field(ProductOrderItemSerializer(many=True))
    def get_items(self, obj):
        qs = obj.items.filter(is_deleted=False)
        return ProductOrderItemSerializer(qs, many=True).data

    @extend_schema_field(ProductOrderActionLogSerializer(many=True))
    def get_action_logs(self, obj):
        qs = obj.action_logs.filter(is_deleted=False).order_by('-created_at')
        return ProductOrderActionLogSerializer(qs, many=True).data

    @extend_schema_field(ProductOrderStageLogSerializer(many=True))
    def get_stage_logs(self, obj):
        qs = obj.stage_logs.filter(is_deleted=False).order_by('-created_at')
        return ProductOrderStageLogSerializer(qs, many=True).data


class ProductOrderActionSerializer(serializers.ModelSerializer):
    is_done = serializers.SerializerMethodField()

    class Meta:
        model = ProductOrderStageAction
        fields = [
            'id', 'title', 'action_type',
            'target_field', 'is_required',
            'order', 'is_done'
        ]

    def get_is_done(self, obj) -> bool:
        order_id = self.context.get('order_id')
        if not order_id:
            return False
        return ProductOrderActionLog.objects.filter(
            order_id=order_id, action=obj
        ).exists()


# =============================================================================
# SHARED — Execute Action / Advance Stage input serializers
# =============================================================================
class ExecuteActionSerializer(serializers.Serializer):
    action_id = serializers.IntegerField()
    value = serializers.JSONField(required=False, allow_null=True)
    item_id = serializers.IntegerField(required=False, allow_null=True)
    note = serializers.CharField(required=False, allow_blank=True)


class AdvanceStageSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True)

