from rest_framework import serializers

from platform_settings.serializers import SoftDeleteSerializerMixin
from users.models import CustomUser


class RequestOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15, help_text="Phone number (e.g. 09123456789)")

class RequestOTPResponseSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=100, help_text="Success or error message")
    error = serializers.CharField(max_length=100, required=False, help_text="Error message (if any)")

class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15, help_text="Phone number (e.g. 09123456789)")
    code = serializers.CharField(max_length=8, help_text="OTP code (e.g. 12345678)")

class VerifyOTPResponseSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=100, help_text="Success or error message")
    error = serializers.CharField(max_length=100, required=False, help_text="Error message (if any)")

class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=500, help_text="Refresh token (taken from cookie)")

class RefreshTokenResponseSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=100, help_text="Success or error message")
    error = serializers.CharField(max_length=100, required=False, help_text="Error message (if any)")


class CustomUserSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['phone']
        read_only_fields = ['is_deleted', 'is_active', 'is_staff', 'is_superuser']