from rest_framework import serializers

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