from django.db import models

from accounting.models import Invoice
from crm.models import Customer
from hr.models import Employee, EmployeeRole
from psn.models import SonyAccount


# ================== Bases ==================
class BaseOrderStage(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    employee_role = models.ForeignKey(
        EmployeeRole, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    is_start = models.BooleanField(default=False)
    is_end = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['order']


class BaseOrderStageAction(models.Model):
    ACTION_TYPE_CHOICES = (
        ('update_order_field', 'آپدیت فیلد سفارش'),
        ('update_order_item_field', 'آپدیت فیلد آیتم سفارش'),
        ('manual_confirm', 'تایید دستی'),
        ('add_note', 'افزودن یادداشت'),
    )

    # فیلدهای Order که مجاز به آپدیت هستن
    ORDER_FIELD_CHOICES = (
        ('stage', 'مرحله سفارش'),
        ('description', 'توضیحات'),
    )

    # فیلدهای OrderItem که مجاز به آپدیت هستن — per order type
    SONY_ORDER_ITEM_FIELD_CHOICES = (
        ('sony_account', 'اکانت سونی'),
        ('is_done', 'انجام شد'),
    )

    title = models.CharField(max_length=100)
    action_type = models.CharField(max_length=50, choices=ACTION_TYPE_CHOICES)
    description = models.TextField(blank=True)
    is_required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    # فقط وقتی action_type == update_*  معنی دارن
    target_field = models.CharField(max_length=50, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['order']


class BaseOrderStageLog(models.Model):
    """کلاس پایه برای لاگ تغییر stage"""
    changed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class BaseOrderActionLog(models.Model):
    """کلاس پایه برای لاگ اکشن‌ها"""
    performed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    # آیتمی که اکشن روی آن اجرا شده (برای update_order_item_field)؛ برای بقیه null
    item_id = models.IntegerField(null=True, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


# ================== Product ==================
class ProductOrderCategory(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class ProductOrderStage(BaseOrderStage):
    category = models.ForeignKey(
        ProductOrderCategory,
        on_delete=models.CASCADE,
        related_name='stages'
    )

    class Meta(BaseOrderStage.Meta):
        verbose_name = 'مرحله سفارش محصول'
        unique_together = ('category', 'order')


class ProductOrderStageAction(BaseOrderStageAction):
    stage = models.ForeignKey(
        ProductOrderStage,
        on_delete=models.CASCADE,
        related_name='actions'
    )

    class Meta(BaseOrderStageAction.Meta):
        verbose_name = 'اکشن مرحله محصول'


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
    product_order = models.ForeignKey(ProductOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, help_text="موقت — بعد از آماده شدن مدل Product حذف می‌شه")
    unit_price = models.IntegerField(default=0)
    amount = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title}'


class ProductOrderStageLog(BaseOrderStageLog):
    order = models.ForeignKey(ProductOrder, on_delete=models.CASCADE, related_name='stage_logs')
    from_stage = models.ForeignKey(ProductOrderStage, on_delete=models.SET_NULL, null=True, related_name='+')
    to_stage = models.ForeignKey(ProductOrderStage, on_delete=models.SET_NULL, null=True, related_name='+')


class ProductOrderActionLog(BaseOrderActionLog):
    order = models.ForeignKey(ProductOrder, on_delete=models.CASCADE, related_name='action_logs')
    action = models.ForeignKey(ProductOrderStageAction, on_delete=models.CASCADE)


# ================== SonyAccount ==================
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
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title} ({self.get_type_display()})'


class SonyAccountOrderStage(BaseOrderStage):
    category = models.ForeignKey(
        SonyAccountOrderCategory,
        on_delete=models.CASCADE,
        related_name='stages'
    )

    class Meta(BaseOrderStage.Meta):
        verbose_name = 'مرحله سفارش اکانت سونی'
        unique_together = ('category', 'order')


class SonyAccountOrderStageAction(BaseOrderStageAction):
    stage = models.ForeignKey(
        SonyAccountOrderStage,
        on_delete=models.CASCADE,
        related_name='actions'
    )

    class Meta(BaseOrderStageAction.Meta):
        verbose_name = 'اکشن مرحله اکانت سونی'


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
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='sony_order_items')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sony_account_order} — {self.sony_account}'


class SonyAccountOrderStageLog(BaseOrderStageLog):
    order = models.ForeignKey(SonyAccountOrder, on_delete=models.CASCADE, related_name='stage_logs')
    from_stage = models.ForeignKey(SonyAccountOrderStage, on_delete=models.SET_NULL, null=True, related_name='+')
    to_stage = models.ForeignKey(SonyAccountOrderStage, on_delete=models.SET_NULL, null=True, related_name='+')


class SonyAccountOrderActionLog(BaseOrderActionLog):
    order = models.ForeignKey(SonyAccountOrder, on_delete=models.CASCADE, related_name='action_logs')
    action = models.ForeignKey(SonyAccountOrderStageAction, on_delete=models.CASCADE)


# ================== Repair ==================
class RepairOrderCategory(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title}'


class RepairOrderStage(BaseOrderStage):
    category = models.ForeignKey(
        RepairOrderCategory,
        on_delete=models.CASCADE,
        related_name='stages'
    )

    class Meta(BaseOrderStage.Meta):
        verbose_name = 'مرحله سفارش تعمیر'
        unique_together = ('category', 'order')


class RepairOrderStageAction(BaseOrderStageAction):
    stage = models.ForeignKey(
        RepairOrderStage,
        on_delete=models.CASCADE,
        related_name='actions'
    )

    class Meta(BaseOrderStageAction.Meta):
        verbose_name = 'اکشن مرحله تعمیر'


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


class RepairOrderStageLog(BaseOrderStageLog):
    order = models.ForeignKey(RepairOrder, on_delete=models.CASCADE, related_name='stage_logs')
    from_stage = models.ForeignKey(RepairOrderStage, on_delete=models.SET_NULL, null=True, related_name='+')
    to_stage = models.ForeignKey(RepairOrderStage, on_delete=models.SET_NULL, null=True, related_name='+')


class RepairOrderActionLog(BaseOrderActionLog):
    order = models.ForeignKey(RepairOrder, on_delete=models.CASCADE, related_name='action_logs')
    action = models.ForeignKey(RepairOrderStageAction, on_delete=models.CASCADE)
