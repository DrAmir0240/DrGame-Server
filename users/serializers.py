from rest_framework import serializers

class RequestOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15, help_text="شماره موبایل (مثال: 09123456789)")

class RequestOTPResponseSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=100, help_text="پیام موفقیت یا خطا")
    error = serializers.CharField(max_length=100, required=False, help_text="پیام خطا (در صورت وجود)")

class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15, help_text="شماره موبایل (مثال: 09123456789)")
    code = serializers.CharField(max_length=8, help_text="کد OTP (مثال: 12345678)")

class VerifyOTPResponseSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=100, help_text="پیام موفقیت یا خطا")
    error = serializers.CharField(max_length=100, required=False, help_text="پیام خطا (در صورت وجود)")

class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=500, help_text="توکن رفرش (از کوکی گرفته می‌شود)")

class RefreshTokenResponseSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=100, help_text="پیام موفقیت یا خطا")
    error = serializers.CharField(max_length=100, required=False, help_text="پیام خطا (در صورت وجود)")