import json

import requests
from django.core.exceptions import ValidationError
from django.db import models

from employees.models import Employee
from home.models import Course
from storage.models import CustomerConsole, Product, Game, SonyAccount
from accounts.models import CustomUser
from customers.models import Customer
from django.conf import settings


# Create your models here.
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order_type = models.CharField(max_length=30, choices=(
        ('customer', 'سفارش از طریق مشتری'),
        ('employee', 'سفارش از طریق کارمند')
    ), default='customer')
    amount = models.DecimalField(max_digits=12, decimal_places=3)
    description = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'سفارش {self.customer.full_name}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=3)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f'{self.product.title} x {self.quantity}'


class GameOrderType(models.Model):
    title = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=3, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class GameOrder(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    account_setter = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True,
                                       related_name='account_setter')
    data_uploader = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True,
                                      related_name='data_uploader')
    order_type = models.ForeignKey(GameOrderType, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=3)
    product = models.ForeignKey(CustomerConsole, on_delete=models.SET_NULL, null=True)
    games = models.ManyToManyField(Game, blank=True)
    games_count = models.IntegerField(default=0, null=True, blank=True)
    selected_games_count = models.IntegerField(default=0, null=True, blank=True)
    status = models.CharField(max_length=50, choices=(
        ('waiting', 'در انتظار پرداخت'), ('payed', 'پرداخت شده'), ('in_progress', 'در حال انجام'),
        ('data', 'دیتا ریختن'), ('done', 'اتمام'), ('delivered', 'تحویل شده')), null=True)
    sony_accounts = models.ManyToManyField(SonyAccount, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'سفارش {self.customer.full_name} بابت {self.order_type.title}'


class RepairOrderType(models.Model):
    title = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class RepairOrder(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order_type = models.ForeignKey(RepairOrderType, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=3)
    product = models.ForeignKey(CustomerConsole, on_delete=models.SET_NULL, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'سفارش {self.customer.full_name} بابت {self.order_type.title}'


class CourseOrder(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='orders')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order #{self.id} - {self.customer} - {self.course}'


class Transaction(models.Model):
    payer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='payer')
    payer_str = models.CharField(max_length=100, null=True, blank=True)
    receiver = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='receiver')
    receiver_str = models.CharField(max_length=100, null=True, blank=True)
    amount = models.PositiveIntegerField()
    authority = models.CharField(max_length=100, blank=True)
    ref_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, default='pending')
    game_order = models.OneToOneField(GameOrder, on_delete=models.SET_NULL, blank=True, null=True,
                                      related_name='game_order')
    repair_order = models.OneToOneField(RepairOrder, on_delete=models.SET_NULL, blank=True, null=True,
                                        related_name='repair_order')
    course_order = models.OneToOneField(CourseOrder, on_delete=models.SET_NULL, blank=True, null=True,
                                        related_name='course_order')
    order = models.OneToOneField(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='order')
    description = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def request_payment(self):
        if self.status != 'pending':
            raise ValidationError("این تراکنش قبلاً پردازش شده است.")

        headers = {
            'accept': 'application/json',
            'content-type': 'application/json'
        }

        data = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": int(self.amount),
            "currency": "IRT",
            "description": self.description or "پرداخت",
            "callback_url": settings.ZARINPAL_CALLBACK_URL,
            "metadata": {
                "mobile": str(self.payer.phone) if self.payer and self.payer.phone else "",
                "order_id": str(self.id)
            }
        }

        try:
            response = requests.post(
                settings.ZARINPAL_REQUEST_URL, json=data, headers=headers
            )
            result = response.json()

            if response.status_code == 200 and result.get("data", {}).get("code") == 100:
                self.authority = result["data"]["authority"]
                self.status = "waiting"
                self.save()
                return {
                    "status": "success",
                    "payment_url": f"{settings.ZARINPAL_START_PAY_URL}{self.authority}",
                    "authority": self.authority
                }
            else:
                self.status = "failed"
                self.save()
                return {
                    "status": "error",
                    "message": result.get("errors") or result.get("data", {}).get("message", "خطای ناشناخته")
                }

        except requests.RequestException as e:
            self.status = "failed"
            self.save()
            return {
                "status": "error",
                "message": str(e)
            }

    def verify_payment(self):
        if not self.authority:
            return {"status": "error", "message": "authority وجود ندارد."}

        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }

        data = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": int(self.amount),
            "authority": self.authority
        }

        try:
            response = requests.post(settings.ZARINPAL_VERIFY_URL, json=data, headers=headers)
            result = response.json()

            code = result.get("data", {}).get("code")
            if code in [100, 101]:
                self.status = "paid"
                self.ref_id = result["data"]["ref_id"]
                self.save()

                return {
                    "status": "success",
                    "ref_id": self.ref_id,
                    "message": result["data"].get("message", "پرداخت موفق بود.")
                }

            else:
                self.status = "failed"
                self.save()
                return {
                    "status": "error",
                    "code": code,
                    "message": result.get("data", {}).get("message", "تراکنش ناموفق بود.")
                }

        except requests.RequestException as e:
            self.status = "failed"
            self.save()
            return {
                "status": "error",
                "message": str(e)
            }

    def save(self, *args, **kwargs):
        if self.payer and self.payer_str:
            raise ValueError("فقط یکی از payer یا payer_str باید مقدار داشته باشد.")
        if self.receiver and self.receiver_str:
            raise ValueError("فقط یکی از receiver یا receiver_str باید مقدار داشته باشد.")

        super().save(*args, **kwargs)

    def __str__(self):
        if self.payer:
            payer = self.payer
        else:
            payer = self.payer_str

        if self.receiver:
            receiver = self.receiver
        else:
            receiver = self.receiver_str

        return f'تراکنش {payer} به {receiver}'
