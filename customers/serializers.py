# customers/serializers.py
from rest_framework import serializers

from payments.serializers import OrderItemSerializer
from storage.serializers import ProductSerializer, GameSerializer
from customers.models import Customer
from payments.models import Order, GameOrder, RepairOrder, Transaction, CourseOrder, GameOrderItem


class CustomerProfileCreateSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.phone', max_length=11, read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'full_name', 'user', 'address', 'postal_code', 'profile_pic', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']

    def validate(self, data):
        request = self.context.get('request')
        user = request.user

        if Customer.objects.filter(user=user).exists():
            raise serializers.ValidationError('You are already a customer')

        if not data.get('full_name'):
            raise serializers.ValidationError('Please type your name')

        if not data.get('address'):
            raise serializers.ValidationError('Please type your address')

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        return Customer.objects.create(user=user, **validated_data)


class CustomerProfileSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.phone', max_length=11, read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'full_name', 'user', 'address', 'postal_code', 'profile_pic', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']

    def validate(self, data):
        if not data.get('full_name'):
            raise serializers.ValidationError('Please type your name')
        if not data.get('address'):
            raise serializers.ValidationError('Please type your address')

        return data


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"


class GameOrderItemSerializer(serializers.ModelSerializer):
    game = serializers.SlugRelatedField(slug_field='title', read_only=True)
    game_img = serializers.SerializerMethodField()

    class Meta:
        model = GameOrderItem
        fields = ['id', 'game', 'amount', 'game_img']

    def get_game_img(self, obj):
        if obj.game.main_img:
            return obj.game.main_img.url
        return None


class GameOrderSerializer(serializers.ModelSerializer):
    games = GameOrderItemSerializer(many=True, read_only=True)
    delivery_to_drgame = serializers.SerializerMethodField()
    delivery_to_customer = serializers.SerializerMethodField()

    class Meta:
        model = GameOrder
        fields = ['id', 'order_type', 'amount', 'status', 'payment_status', 'games', 'created_at', 'dead_line',
                  'delivery_to_drgame', 'delivery_to_customer']
        read_only_fields = fields

    def get_delivery_to_drgame(self, obj):
        if obj.delivery_to_drgame:
            return f'{obj.delivery_to_drgame.full_name} : {obj.delivery_to_drgame.phone_number}'
        return None

    def get_delivery_to_customer(self, obj):
        if obj.delivery_to_customer:
            return f'{obj.delivery_to_customer.full_name} : {obj.delivery_to_customer.phone_number}'
        return None


class RepairOrderSerializer(serializers.ModelSerializer):
    order_type = serializers.StringRelatedField()
    delivery_to_drgame = serializers.SerializerMethodField()
    delivery_to_customer = serializers.SerializerMethodField()

    class Meta:
        model = RepairOrder
        fields = ['id', 'order_type', 'amount', 'status', 'payment_status', 'created_at', 'dead_line',
                  'delivery_to_drgame', 'delivery_to_customer']
        read_only_fields = fields

    def get_delivery_to_drgame(self, obj):
        if obj.delivery_to_drgame:
            return f'{obj.delivery_to_drgame.full_name} : {obj.delivery_to_drgame.phone_number}'
        return None

    def get_delivery_to_customer(self, obj):
        if obj.delivery_to_customer:
            return f'{obj.delivery_to_customer.full_name} : {obj.delivery_to_customer.phone_number}'
        return None


class CourseOrderSerializer(serializers.ModelSerializer):
    course = serializers.StringRelatedField(source='course.title')

    class Meta:
        model = CourseOrder
        fields = ['id', 'course', 'amount', 'payment_status', 'created_at', 'updated_at', ]
        read_only_fields = fields


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'amount',
                  'description', 'created_at']
        read_only_fields = fields
