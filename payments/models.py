import requests
from django.core.exceptions import ValidationError
from django.db import models
from employees.models import Employee, Repairman
from home.models import Course
from storage.models import Product, Game, SonyAccount
from accounts.models import CustomUser
from customers.models import Customer
from django.conf import settings


# Create your models here.
class PaymentMethod(models.Model):
    title = models.CharField(max_length=100)
    balance = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    is_online = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.is_online:
            qs = PaymentMethod.objects.filter(is_online=True, is_deleted=False)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError("فقط یک متود پرداخت می‌تواند آنلاین باشد.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Payment method #{self.title}'


class Transaction(models.Model):
    payer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='payer')
    payer_str = models.CharField(max_length=100, null=True, blank=True)
    receiver = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='receiver')
    receiver_str = models.CharField(max_length=100, null=True, blank=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='transactions')
    amount = models.PositiveIntegerField()
    authority = models.CharField(max_length=100, blank=True)
    ref_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, default='pending')
    in_out = models.BooleanField(default=True)
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
        payer = self.payer if self.payer else self.payer_str if self.payer_str else "نامشخص"
        receiver = self.receiver if self.receiver else self.receiver_str if self.receiver_str else "نامشخص"
        return f'تراکنش {payer} به {receiver}'


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    order_type = models.CharField(max_length=30, choices=(
        ('customer', 'سفارش از طریق مشتری'),
        ('employee', 'سفارش از طریق کارمند')
    ), default='customer')
    amount = models.DecimalField(max_digits=12, decimal_places=3)
    payment_status = models.CharField(max_length=30,
                                      choices=(
                                          ('paid', 'پرداخت شده'),
                                          ('unpaid', 'پرداخت نشده')),
                                      default='unpaid')
    transaction = models.OneToOneField(Transaction, on_delete=models.SET_NULL, null=True, related_name='order')
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


class DeliveryMan(models.Model):
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)

    def __str__(self):
        return self.full_name + ' ' + self.phone_number


GAME_ORDER_CONSOLE_TYPE = (
    ('online_ps4', 'online_ps4'),
    ('online_ps5', 'online_ps5'),
    ('offline_ps4', 'offline_ps4'),
    ('offline_ps5', 'offline_ps5'),
    ('data_ps4', 'data_ps4'),
    ('data_ps5', 'data_ps5'),
    ('xbox', 'xbox'),
    ('nintendo', 'nintendo'),
)
GAME_ORDER_STATUS = (
    ('waiting_for_delivery', 'پرداخت شده و در انتظار تحویل به دکتر گیم'),
    ('delivered_to_drgame_and_in_waiting_queue', 'تحویل شده به دکتر گیم و در لیست انتظار'),
    ('account_setting_in_progress', 'در حال ست شدن اکانت'),
    ('in_data_uploading_queue', 'در انتظار اپلود داده'),
    ('data_uploading_in_progress', 'در حال اپلود داده'),
    ('error_on_accounts', 'مشکل در اکانت ها'),
    ('done', 'انجام شده و در انتظار پیک'),
    ('delivered_to_customer', 'تحویل شده به مشتری'),
)


class GameOrder(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    recipient = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True,
                                  related_name='recipient')
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True,
                                 related_name='current_employee')
    amount = models.IntegerField(null=True, blank=True)
    order_type = models.CharField(max_length=30, choices=(
        ('customer', 'سفارش از طریق مشتری'),
        ('employee', 'سفارش از طریق کارمند')
    ), default='customer')
    order_console_type = models.CharField(max_length=30, choices=GAME_ORDER_CONSOLE_TYPE, null=True)
    console = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=50, choices=GAME_ORDER_STATUS,
                              default="delivered_to_drgame_and_in_waiting_queue")
    payment_status = models.CharField(max_length=30, choices=(
        ('paid', 'پرداخت شده'),
        ('unpaid', 'پرداخت نشده')
    ), default='unpaid')
    transaction = models.OneToOneField(Transaction, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='game_order')
    sony_accounts = models.ManyToManyField(SonyAccount, blank=True)
    delivery_to_drgame = models.OneToOneField(DeliveryMan, on_delete=models.SET_NULL, null=True,
                                              related_name='delivery_console_to_drgame', blank=True)
    dead_line = models.DateTimeField(null=True, blank=True)
    delivery_to_customer = models.OneToOneField(DeliveryMan, on_delete=models.SET_NULL, null=True,
                                                related_name='delivery_console_to_customer', blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'سفارش {self.customer.full_name}'


class GameOrderItem(models.Model):
    game_order = models.ForeignKey(GameOrder, on_delete=models.CASCADE, related_name='games')
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    account_setter = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True,
                                       related_name='account_setter')
    data_uploader = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True,
                                      related_name='data_uploader')
    amount = models.IntegerField(null=True, blank=True)
    account = models.BooleanField(default=False)
    data = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.game_order}: {self.game}"


class RepairOrderType(models.Model):
    title = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class RepairOrder(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    repair_man = models.ForeignKey(Repairman, on_delete=models.SET_NULL, null=True)
    order_type = models.ForeignKey(RepairOrderType, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=3, null=True)
    repairman_fee = models.IntegerField(null=True, blank=True)
    dead_line = models.DateTimeField(null=True, blank=True)
    console = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=50, choices=(
        ('waiting_for_delivery_to_drgame', 'در انتظار تحویل به دکترگیم'),
        ('in_accepting_queue', 'در انتظار قبول شدن توسط تعمیرکار'),
        ('waiting_for_repairman_fee', 'در انتظار تعیین مبلغ'),
        ('waiting_for_amount', 'در انتظار تعیین مبلغ توسط دکتر گیم'),
        ('waiting_for_customer_to_accept', 'در انتظار تایید توسط مشتری'),
        ('in_progress', 'در حال پردازش'),
        ('done', 'در انتظار تحویل به مشتری'),
        ('delivered_to_customer', 'تحویل شده به مشتری'),
    ), default='waiting_for_delivery_to_drgame')
    payment_status = models.CharField(max_length=30, choices=(
        ('پرداخت شده', 'paid'),
        ('پرداخت نشده', 'unpaid')
    ), default='unpaid')
    transaction = models.OneToOneField(Transaction, on_delete=models.SET_NULL, null=True, related_name='repair')
    delivery_to_drgame = models.OneToOneField(DeliveryMan, on_delete=models.SET_NULL, null=True,
                                              related_name='delivery_to_drgame')
    delivery_to_customer = models.OneToOneField(DeliveryMan, on_delete=models.SET_NULL, null=True,
                                                related_name='delivery_to_customer')
    description = models.TextField(null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'سفارش {self.customer.full_name} بابت {self.order_type}'


class CourseOrder(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=2000000)
    transaction = models.OneToOneField(Transaction, on_delete=models.SET_NULL, null=True, related_name='course_order')
    payment_status = models.CharField(max_length=30, choices=(
        ('پرداخت شده', 'paid'),
        ('پرداخت نشده', 'unpaid')
    ), default='unpaid')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order #{self.id} - {self.customer}'


class TelegramOrder(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)
    sony_account = models.ForeignKey(SonyAccount, on_delete=models.PROTECT)
    amount = models.IntegerField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Telegram Order #{self.id} - {self.employee}'
