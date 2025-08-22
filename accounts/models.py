import secrets
import uuid
from datetime import timedelta

import requests
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from DrGame import settings
from accounts.manager import CustomUserManager


# Create your models here.

class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=11, unique=True, verbose_name="phone")
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone


class MainManager(models.Model):
    id = models.IntegerField(primary_key=True, unique=True, default=1)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='main_manager')
    name = models.CharField(max_length=100, unique=True)
    access = models.CharField(max_length=1, choices=(('1', '1'),), unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    def __str__(self):
        return self.name


class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=5)  # برای OTP 8 رقمی
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return timezone.now() <= self.expires_at

    def send_otp(self, phone, otp_code):
        url = "https://edge.ippanel.com/v1/api/send"
        api_key = settings.FARAZ_API_KEY
        phone = '+98' + phone[1:]  # فرمت شماره تلفن
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
        print(phone)
        print(otp_code)
        message = f"به دکتر گیم خوش آمدید\ncode : {otp_code}\n\nبزرگترین مرجع نصب بازی‌های کنسول در ایران\nـــــــ"
        print(message)
        payload = {
            "sending_type": "webservice",
            "from_number": "+983000505",  # شماره فرستنده
            "message": message,
            "params": {
                "recipients": [phone, ]
            }
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {response.headers}")
            print(f"Response Body: {response.text}")

            try:
                response_json = response.json()
                print(f"Response JSON: {response_json}")

                # گرفتن status از داخل meta
                meta = response_json.get("meta", {})
                status_ok = meta.get("status") is True

                if status_ok:
                    print(f"OTP for {phone}: {otp_code}")
                    return True, "پیامک با موفقیت ارسال شد"
                else:
                    return False, f"خطا در ارسال پیامک: {meta.get('message', 'نامشخص')}"
            except ValueError:
                print("Response is not valid JSON")
                return False, "خطا در ارسال پیامک: پاسخ API معتبر نیست"
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {str(e)}")
            return False, f"خطا در ارتباط با سرویس پیامک: {str(e)}"


class APIKey(models.Model):
    key = models.CharField(max_length=70, unique=True)
    client_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client_name} - {self.key[:10]}..."

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_urlsafe(52)[:70]  # تولید رشته رندوم 70 کاراکتری
        super().save(*args, **kwargs)
