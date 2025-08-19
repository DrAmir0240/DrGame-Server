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
        fields = ["id", "username", "region", "plus", "is_owned", "bank_account_status"]


class SonyAccountMatchedSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    games = serializers.SlugRelatedField(many=True, read_only=True, slug_field='title')
    matching_games_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = SonyAccount
        fields = ['id', 'username', 'games', 'matching_games_count', 'region', 'created_at', 'updated_at']
        read_only_fields = ['is_deleted', 'created_at', 'updated_at']


class GameOrderMatchedSerializer(serializers.ModelSerializer):
    matching_games_count = serializers.IntegerField(read_only=True)
    customer_name = serializers.CharField(source="customer.user.full_name", read_only=True)

    class Meta:
        model = GameOrder
        fields = [
            "id",
            "customer_name",
            "status",
            "created_at",
            "matching_games_count",
        ]


class SonyAccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SonyAccount
        fields = ['username', 'password']
