from django.db import models

from employees.models import Employee
from home.models import Course
from storage.models import CustomerConsole, Product, Game, SonyAccount
from accounts.models import CustomUser
from customers.models import Customer
from django.conf import settings


# Create your models here.

class OrderType(models.Model):
    title = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order_type = models.ForeignKey(OrderType, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=3)
    description = models.TextField(null=True, blank=True)
    product = models.ManyToManyField(Product, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'سفارش {self.customer.full_name} بابت {self.order_type.title}'


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
    amount = models.DecimalField(max_digits=12, decimal_places=3)
    game_order = models.ForeignKey(GameOrder, on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name='game_order')
    repair_order = models.ForeignKey(RepairOrder, on_delete=models.SET_NULL, blank=True, null=True,
                                     related_name='repair_order')
    course_order = models.ForeignKey(CourseOrder, on_delete=models.SET_NULL, blank=True, null=True,
                                     related_name='course_order')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='order')
    description = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
