# customers/serializers.py
from rest_framework import serializers

from storage.serializers import ProductSerializer
from .models import Customer, BusinessCustomer
from payments.models import Order, GameOrder, RepairOrder, Transaction, CourseOrder


class CustomerProfileCreateSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.phone', max_length=11, read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'full_name', 'user', 'address', 'profile_pic', 'created_at']
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
        fields = ['id', 'full_name', 'user', 'address', 'profile_pic', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']

    def validate(self, data):
        if not data.get('full_name'):
            raise serializers.ValidationError('Please type your name')
        if not data.get('address'):
            raise serializers.ValidationError('Please type your address')

        return data


class BusinessCustomerProfileSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.phone', max_length=11, read_only=True)

    class Meta:
        model = BusinessCustomer
        fields = ['id', 'full_name', 'user', 'license', 'address', 'profile_pic', 'created_at', ]
        read_only_fields = ['id', 'created_at', 'user', 'license']

    def validate(self, data):

        if 'license' in data and not data.get('license'):
            raise serializers.ValidationError('Please provide a license as a business customer')
        if not data.get('full_name'):
            raise serializers.ValidationError('Please type your name')

        if not data.get('address'):
            raise serializers.ValidationError('Please type your address')
        return data


class BusinessCustomerUpgradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessCustomer
        fields = ['full_name', 'license', 'address', 'profile_pic']
        extra_kwargs = {
            'license': {'required': True}
        }

    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        if BusinessCustomer.objects.filter(user=user).exists():
            raise serializers.ValidationError('You are already a business customer')

        if 'license' in data and not data.get('license'):
            raise serializers.ValidationError('Please provide a license as a business customer')

        if not data.get('full_name'):
            raise serializers.ValidationError('Please type your name')

        if not data.get('address'):
            raise serializers.ValidationError('Please type your address')

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        return BusinessCustomer.objects.create(user=user, **validated_data)


class OrderSerializer(serializers.ModelSerializer):
    order_type = serializers.StringRelatedField()
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_type','description', 'amount', 'product', 'created_at']
        read_only_fields = fields


class GameOrderSerializer(serializers.ModelSerializer):
    order_type = serializers.StringRelatedField()
    product = serializers.StringRelatedField()

    class Meta:
        model = GameOrder
        fields = ['id', 'order_type', 'amount', 'product', 'games_count',
                  'selected_games_count', 'created_at']
        read_only_fields = fields


class RepairOrderSerializer(serializers.ModelSerializer):
    order_type = serializers.StringRelatedField()
    product = serializers.StringRelatedField()

    class Meta:
        model = RepairOrder
        fields = ['id', 'order_type', 'amount', 'product', 'created_at']
        read_only_fields = fields


class CourseOrderSerializer(serializers.ModelSerializer):
    course = serializers.StringRelatedField(source='course.title')

    class Meta:
        model = CourseOrder
        fields = ['id', 'course', 'amount', 'created_at', 'updated_at', ]
        read_only_fields = fields


class TransactionSerializer(serializers.ModelSerializer):
    transaction_type = serializers.StringRelatedField()
    payer = serializers.StringRelatedField()
    receiver = serializers.StringRelatedField()

    class Meta:
        model = Transaction
        fields = ['id', 'transaction_type', 'amount',
                  'description', 'payer', 'receiver', 'created_at']
        read_only_fields = fields
