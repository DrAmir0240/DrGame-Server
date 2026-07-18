from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from users.models import CustomUser


class BankAccount(models.Model):
    title = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    sheba = models.CharField(max_length=30, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class AccountSide(models.Model):
    TYPE_CHOICES = (
        ('customer', 'مشتری'),
        ('employee', 'کارمند'),
        ('supplier', 'تامین‌کننده'),
        ('other', 'سایر'),
    )

    name = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    # Generic FK — مشخص می‌کنه به کدوم مدل وصله
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="نوع مدل مرتبط (Customer، Employee، Supplier)"
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        if self.content_object:
            return str(self.content_object)
        if self.name:
            return self.name
        return f'{self.get_type_display()} #{self.object_id}'


class InvoiceCategory(models.Model):
    DIRECTION_CHOICES = (
        ('in', 'ورودی'),
        ('out', 'خروجی'),
    )

    title = models.CharField(max_length=100)
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title} ({self.get_direction_display()})'


class Invoice(models.Model):
    STATUS_CHOICES = (
        ('draft', 'پیش‌نویس'),
        ('primary', 'صادر شده'),
        ('finalize', 'نهایی'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('unpaid', 'پرداخت نشده'),
        ('partial', 'پرداخت جزئی'),
        ('paid', 'پرداخت شده'),
    )

    account_side = models.ForeignKey(AccountSide, on_delete=models.CASCADE, related_name='invoices')
    category = models.ForeignKey(InvoiceCategory, on_delete=models.CASCADE, related_name='invoices')
    discount = models.IntegerField(default=0)
    amount = models.IntegerField()
    paid_amount = models.IntegerField(default=0, help_text="مجموع مبلغ پرداخت‌شده — از Celery آپدیت می‌شه")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    is_payroll = models.BooleanField(default=False, help_text="آیا این فاکتور فیش حقوقیه؟")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    @property
    def remaining_amount(self):
        return max(0, self.amount - self.discount - self.paid_amount)

    def __str__(self):
        return f'فاکتور #{self.id} - {self.account_side}'


class InvoiceItem(models.Model):
    """
    آیتم‌های فاکتور — می‌تونه به هر مدلی وصل باشه:
    - SonyAccountOrder
    - RepairOrder
    - ProductOrder
    - یا هر مدل دیگه‌ای
    """
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    unit_price = models.IntegerField()
    discount = models.IntegerField(default=0)

    # Generic FK — مشخص می‌کنه این آیتم به کدوم سفارش/موجودیت وصله
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="نوع مدل مرتبط (SonyAccountOrder، RepairOrder، ProductOrder و...)"
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    @property
    def total_price(self):
        return (self.unit_price * self.quantity) - self.discount

    def __str__(self):
        return f'{self.title} × {self.quantity}'


class PayrollDetail(models.Model):
    """
    جزئیات فیش حقوقی — فقط وقتی invoice.is_payroll=True معنی داره
    """
    invoice = models.OneToOneField(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payroll_detail',
        limit_choices_to={'is_payroll': True}
    )

    # درآمدها
    base_salary = models.IntegerField(default=0, help_text="حقوق پایه")
    overtime_amount = models.IntegerField(default=0, help_text="اضافه‌کاری")
    bonus = models.IntegerField(default=0, help_text="پاداش")
    housing_allowance = models.IntegerField(default=0, help_text="حق مسکن")
    food_allowance = models.IntegerField(default=0, help_text="حق خوار و بار")
    transportation_allowance = models.IntegerField(default=0, help_text="حق ایاب و ذهاب")

    # کسورات
    insurance_deduction = models.IntegerField(default=0, help_text="کسر بیمه")
    tax_deduction = models.IntegerField(default=0, help_text="کسر مالیات")
    loan_deduction = models.IntegerField(default=0, help_text="کسر اقساط وام")
    other_deductions = models.IntegerField(default=0, help_text="سایر کسورات")

    work_days = models.IntegerField(default=0, help_text="روزهای کارکرد")
    overtime_hours = models.IntegerField(default=0, help_text="ساعات اضافه‌کاری")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def gross_salary(self):
        return (
                self.base_salary
                + self.overtime_amount
                + self.bonus
                + self.housing_allowance
                + self.food_allowance
                + self.transportation_allowance
        )

    @property
    def total_deductions(self):
        return (
                self.insurance_deduction
                + self.tax_deduction
                + self.loan_deduction
                + self.other_deductions
        )

    @property
    def net_salary(self):
        return self.gross_salary - self.total_deductions

    def __str__(self):
        return f'فیش حقوقی فاکتور #{self.invoice_id}'


class Transaction(models.Model):
    DIRECTION_CHOICES = (
        ('in', 'دریافت'),
        ('out', 'پرداخت'),
    )

    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    account_side = models.ForeignKey(AccountSide, on_delete=models.CASCADE, related_name='transactions')
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='transactions')
    amount = models.IntegerField()
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.get_direction_display()} {self.amount} — {self.account_side}'


class Wallet(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    balance = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.full_name()}: {self.balance}"
