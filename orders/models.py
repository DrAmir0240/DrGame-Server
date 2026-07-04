from django.db import models

from accounting.models import Invoice
from crm.models import Customer
from hr.models import Employee, EmployeeRole
from inventory.models import SonyAccount


class ProductOrderStage(models.Model):
    title = models.CharField(max_length=100)
    is_in_progress = models.BooleanField(default=False)
    is_in_waiting = models.BooleanField(default=False)
    employee_role = models.ForeignKey(EmployeeRole, on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class ProductOrder(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='product_orders')
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='product_orders',
        help_text="فاکتور خروجی مرتبط با این سفارش"
    )
    stage = models.ForeignKey(
        ProductOrderStage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='product_orders'
    )
    description = models.TextField(blank=True, null=True)
    amount = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'سفارش محصول #{self.id} - {self.customer}'


class ProductOrderItem(models.Model):
    """
    آیتم‌های سفارش محصول
    هر آیتم از طریق InvoiceItem (Generic FK) به فاکتور وصل می‌شه
    """
    product_order = models.ForeignKey(ProductOrder, on_delete=models.CASCADE, related_name='items')
    # FK به مدل Product در inventory — وقتی مدل Product آماده شد uncomment کن
    # product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, help_text="موقت — بعد از آماده شدن مدل Product حذف می‌شه")
    quantity = models.IntegerField(default=1)
    unit_price = models.IntegerField(default=0)
    amount = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title} × {self.quantity}'


class RepairOrderStage(models.Model):
    title = models.CharField(max_length=100)
    is_in_progress = models.BooleanField(default=False)
    is_in_waiting = models.BooleanField(default=False)
    employee_role = models.ForeignKey(EmployeeRole, on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class RepairOrderCategory(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class RepairOrder(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='repair_orders')
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='repair_orders',
        help_text="فاکتور خروجی مرتبط با این سفارش تعمیر"
    )
    stage = models.ForeignKey(
        RepairOrderStage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='repair_orders'
    )
    category = models.ForeignKey(
        RepairOrderCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='repair_orders'
    )
    repair_fee = models.IntegerField(blank=True, null=True, help_text="هزینه تعمیر")
    final_amount = models.IntegerField(blank=True, null=True, help_text="مبلغ نهایی")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'سفارش تعمیر #{self.id} - {self.customer}'


class RepairOrderDevice(models.Model):
    """دستگاه‌هایی که برای تعمیر آورده شدن"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='repair_devices')
    repair_order = models.ForeignKey(RepairOrder, on_delete=models.CASCADE, related_name='devices')
    title = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title} - {self.serial_number}'


class SonyAccountOrderStage(models.Model):
    title = models.CharField(max_length=100)
    is_in_progress = models.BooleanField(default=False)
    is_in_waiting = models.BooleanField(default=False)
    employee_role = models.ForeignKey(EmployeeRole, on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class SonyAccountOrderCategory(models.Model):
    ACCOUNT_CAPACITY_CHOICES = (
        ('1', 'Offline'),
        ('2', 'Online + Offline'),
        ('3', 'Online'),
    )
    TYPE_CHOICES = (
        ('buy', 'خرید'),
        ('rent', 'اجاره'),
    )

    title = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    rent_time_days = models.IntegerField(default=1, null=True, blank=True)
    account_capacity = models.CharField(max_length=10, choices=ACCOUNT_CAPACITY_CHOICES)

    def __str__(self):
        return f'{self.title} ({self.get_type_display()})'


class SonyAccountOrder(models.Model):
    SOURCE_CHOICES = (
        ('telegram', 'تلگرام'),
        ('website', 'سایت'),
        ('in_person', 'حضوری'),
    )
    TYPE_CHOICES = (
        ('by_customer', 'توسط مشتری'),
        ('by_employee', 'توسط کارمند'),
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='sony_account_orders')
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sony_account_orders',
        help_text="فاکتور خروجی مرتبط با این سفارش"
    )
    stage = models.ForeignKey(
        SonyAccountOrderStage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sony_account_orders'
    )
    category = models.ForeignKey(
        SonyAccountOrderCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sony_account_orders'
    )
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'سفارش اکانت سونی #{self.id} - {self.customer}'


class SonyAccountOrderConsole(models.Model):
    """کنسول‌های ثبت‌شده برای سفارش اکانت سونی"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='sony_consoles')
    sony_account_order = models.ForeignKey(
        SonyAccountOrder,
        on_delete=models.CASCADE,
        related_name='consoles',
        null=True,
        blank=True
    )
    serial_number = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.serial_number} - {self.customer}'


class SonyAccountOrderItem(models.Model):
    """اکانت‌های سونی که به یه سفارش اختصاص داده شدن"""
    sony_account_order = models.ForeignKey(SonyAccountOrder, on_delete=models.CASCADE, related_name='items')
    sony_account = models.ForeignKey(SonyAccount, on_delete=models.CASCADE, related_name='order_items')
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='sony_order_items')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.sony_account_order} — {self.sony_account}'