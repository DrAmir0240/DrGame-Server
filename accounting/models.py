from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from hr.models import Employee
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
        ("customer", "مشتری"),
        ("employee", "کارمند"),
        ("supplier", "تامین‌کننده"),
        ("other", "سایر"),
    )

    name = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    # Generic FK — indicates which model this points to
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Related model type (Customer, Employee, Supplier)",
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        if self.content_object:
            return str(self.content_object)
        if self.name:
            return self.name
        return f"{self.get_type_display()} #{self.object_id}"


class InvoiceCategory(models.Model):
    DIRECTION_CHOICES = (
        ("in", "ورودی"),
        ("out", "خروجی"),
    )

    title = models.CharField(max_length=100)
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.get_direction_display()})"


class Invoice(models.Model):
    STATUS_CHOICES = (
        ("draft", "پیش‌نویس"),
        ("primary", "صادر شده"),
        ("finalize", "نهایی"),
    )

    PAYMENT_STATUS_CHOICES = (
        ("unpaid", "پرداخت نشده"),
        ("partial", "پرداخت جزئی"),
        ("paid", "پرداخت شده"),
    )

    account_side = models.ForeignKey(
        AccountSide, on_delete=models.CASCADE, related_name="invoices"
    )
    category = models.ForeignKey(
        InvoiceCategory, on_delete=models.CASCADE, related_name="invoices"
    )
    discount = models.IntegerField(default=0)
    amount = models.IntegerField()
    paid_amount = models.IntegerField(
        default=0, help_text="Total paid amount — updated from Celery"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="unpaid"
    )
    is_payroll = models.BooleanField(
        default=False, help_text="Is this invoice a payroll slip?"
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    @property
    def remaining_amount(self):
        return max(0, self.amount - self.discount - self.paid_amount)

    def __str__(self):
        return f"Invoice #{self.id} - {self.account_side}"


class InvoiceItem(models.Model):
    """
    Invoice items — can link to any model:
    - SonyAccountOrder
    - RepairOrder
    - ProductOrder
    - or any other model
    """

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    title = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    unit_price = models.IntegerField()
    discount = models.IntegerField(default=0)

    # Generic FK — indicates which order/entity this item belongs to
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Related model type (SonyAccountOrder, RepairOrder, ProductOrder, ...)",
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    @property
    def total_price(self):
        return (self.unit_price * self.quantity) - self.discount

    def __str__(self):
        return f"{self.title} × {self.quantity}"


class PayrollDetail(models.Model):
    """
    Payroll details — only meaningful when invoice.is_payroll=True
    """

    invoice = models.OneToOneField(
        Invoice,
        on_delete=models.CASCADE,
        related_name="payroll_detail",
        limit_choices_to={"is_payroll": True},
    )

    # Income
    base_salary = models.IntegerField(default=0, help_text="Base salary")
    overtime_amount = models.IntegerField(default=0, help_text="Overtime")
    bonus = models.IntegerField(default=0, help_text="Bonus")
    housing_allowance = models.IntegerField(default=0, help_text="Housing allowance")
    food_allowance = models.IntegerField(default=0, help_text="Food allowance")
    transportation_allowance = models.IntegerField(
        default=0, help_text="Transportation allowance"
    )

    # Deductions
    insurance_deduction = models.IntegerField(default=0, help_text="Insurance deduction")
    tax_deduction = models.IntegerField(default=0, help_text="Tax deduction")
    loan_deduction = models.IntegerField(default=0, help_text="Loan installment deduction")
    other_deductions = models.IntegerField(default=0, help_text="Other deductions")

    work_days = models.IntegerField(default=0, help_text="Work days")
    overtime_hours = models.IntegerField(default=0, help_text="Overtime hours")
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
        return f"Payroll slip for invoice #{self.invoice_id}"


class Transaction(models.Model):
    DIRECTION_CHOICES = (
        ("in", "دریافت"),
        ("out", "پرداخت"),
    )

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    account_side = models.ForeignKey(
        AccountSide, on_delete=models.CASCADE, related_name="transactions"
    )
    bank_account = models.ForeignKey(
        BankAccount, on_delete=models.CASCADE, related_name="transactions"
    )
    amount = models.IntegerField()
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_direction_display()} {self.amount} — {self.account_side}"


class Wallet(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="wallet"
    )
    balance = models.BigIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.full_name()}: {self.balance:,} T"


class WalletTransaction(models.Model):
    TYPE_CHOICES = (
        ("charge_admin", "شارژ توسط ادمین"),
        ("charge_gateway", "شارژ آنلاین"),
        ("debit_order", "کسر بابت سفارش"),
        ("refund", "برگشت وجه"),
    )
    STATUS_CHOICES = (
        ("pending", "در انتظار"),
        ("success", "موفق"),
        ("failed", "ناموفق"),
        ("cancelled", "لغو شده"),
    )

    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="transactions"
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.PositiveBigIntegerField(help_text="Amount in Toman")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    description = models.CharField(max_length=300, blank=True)
    gateway_ref = models.CharField(
        max_length=100, blank=True, null=True, help_text="Gateway payment ID"
    )
    gateway_name = models.CharField(
        max_length=50, blank=True, null=True, help_text="Example: zarinpal"
    )
    order_content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True
    )
    order_object_id = models.PositiveIntegerField(null=True, blank=True)
    performed_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Only for charge_admin",
    )
    balance_before = models.PositiveBigIntegerField(help_text="Balance before transaction")
    balance_after = models.PositiveBigIntegerField(help_text="Balance after transaction")
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
