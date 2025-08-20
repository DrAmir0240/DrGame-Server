from rest_framework import serializers

from employees.serializers import SoftDeleteSerializerMixin
from payments.models import GameOrder
from storage.models import SonyAccount


class Set2FAURISerializer(serializers.Serializer):
    uri = serializers.CharField()  # URI کامل otpauth:// که از سونی میاد


class OTPSerializer(serializers.Serializer):
    code = serializers.CharField()
    remaining = serializers.IntegerField()


class SonyAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SonyAccount
        fields = ["id", "username", "password"]


class SonyAccountMatchedSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    games = serializers.SlugRelatedField(many=True, read_only=True, slug_field='title')
    matching_games_count = serializers.IntegerField(read_only=True)
    employee = serializers.SerializerMethodField

    class Meta:
        model = SonyAccount
        fields = ['id', 'username', 'games', 'matching_games_count', 'region', 'created_at', 'updated_at']
        read_only_fields = ['is_deleted', 'created_at', 'updated_at']

    def get_employee(self, obj):
        if obj.employee:
            return obj.employee.first_name + " " + obj.employee.last_name
        return None


class GameOrderMatchedSerializer(serializers.ModelSerializer):
    matching_games_count = serializers.IntegerField(read_only=True)
    customer_name = serializers.SerializerMethodField()
    employee = serializers.SerializerMethodField()

    class Meta:
        model = GameOrder
        fields = [
            "id",
            "customer_name",
            "employee",
            "status",
            "created_at",
            "matching_games_count",
        ]

    def get_customer_name(self, obj):
        if obj.customer:
            return obj.customer.full_name
        return None

    def get_employee(self, obj):
        if obj.employee:
            return obj.employee.first_name + " " + obj.employee.last_name
        return None


class SonyAccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SonyAccount
        fields = ['username', 'password']


class SonyAccountAddFromFileSerializer(serializers.Serializer):
    file = serializers.FileField()
