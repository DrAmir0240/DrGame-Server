from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction
from rest_framework import serializers

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

