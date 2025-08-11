from rest_framework import serializers


class Set2FASecretSerializer(serializers.Serializer):
    secret = serializers.CharField(max_length=100)


class OTPSerializer(serializers.Serializer):
    code = serializers.CharField()
    remaining = serializers.IntegerField()
