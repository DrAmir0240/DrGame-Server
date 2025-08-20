from rest_framework import serializers

from home.models import CartItem, Cart, GAME_CART_TYPE
from payments.models import Order, Transaction, Product, OrderItem, GameOrder, DeliveryMan, RepairOrder, CourseOrder, \
    GameOrderItem, GAME_ORDER_CONSOLE_TYPE
from storage.serializers import GameSerializer


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
        read_only_fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'payer', 'receiver', 'amount', 'authority', 'ref_id', 'status', 'order', 'description',
                  'is_deleted', 'created_at', 'updated_at']
        read_only_fields = fields
