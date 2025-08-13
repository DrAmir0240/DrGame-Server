from rest_framework import serializers


class Set2FAURISerializer(serializers.Serializer):
    uri = serializers.CharField()  # URI کامل otpauth:// که از سونی میاد


class OTPSerializer(serializers.Serializer):
    code = serializers.CharField()
    remaining = serializers.IntegerField()
