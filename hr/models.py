from django.db import models
from users.models import CustomUser


# Create your models here.
class PermissionModule(models.TextChoices):
    DASHBOARD = 'dashboard', 'داشبورد'
    TASK_MANAGER = 'task_manager', 'مدیریت وظایف'
    ACCOUNTING = 'accounting', 'حسابداری'
    INVENTORY = 'inventory', 'انبار'
    ORDERS = 'orders', 'سفارشات'
    ACCOUNT_ORDERS = 'account_orders', 'سفارشات حساب'
    REPAIRS = 'repairs', 'تعمیرات'
    HR = 'hr', 'منابع انسانی'
    SITE = 'site', 'سایت'
    BRANCH = 'branch', 'شعبه'
    DOCS = 'docs', 'اسناد'
    SETTINGS = 'settings', 'تنظیمات'
    MESSENGER = 'messenger', 'پیام‌رسان'


class PermissionAction(models.TextChoices):
    ACCESS = 'access', 'دسترسی'
    READ = 'read', 'خواندن'
    WRITE = 'write', 'نوشتن'


class Permission(models.Model):
    """
    هر رکورد = یه permission اتمیک
    مثال: module='accounting', action='read'
    """

    module = models.CharField(max_length=50, choices=PermissionModule)
    action = models.CharField(max_length=20, choices=PermissionAction)
    extra_flag = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        unique_together = ('module', 'action', 'extra_flag')

    def __str__(self):
        return f'{self.module}:{self.action}' + (f':{self.extra_flag}' if self.extra_flag else '')


class EmployeeRole(models.Model):
    role_name = models.CharField(max_length=100)
    description = models.TextField(max_length=5000, blank=True)
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='roles'
    )
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'نقش'
        verbose_name_plural = 'نقش‌ها'

    def __str__(self):
        return self.role_name


class Employee(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employee')
    profile_picture = models.ImageField(null=True, blank=True, upload_to='profile_pictures/hr/')
    roles = models.ManyToManyField(EmployeeRole, blank=True, related_name='employees')
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    national_code = models.CharField(max_length=10, null=True, unique=True)
    birth_date = models.DateField(null=True, blank=True)
    employee_id = models.CharField(max_length=11, null=True, unique=True, blank=True)
    balance = models.DecimalField(max_digits=15, decimal_places=0, default=0)
    has_commission = models.BooleanField(default=False)
    commission_amount = models.DecimalField(max_digits=15, decimal_places=0, default=0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'کارمند'
        verbose_name_plural = 'کارمندان'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class EmployeeFile(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='files')
    title = models.CharField(max_length=100, null=True, blank=True)
    file = models.FileField(upload_to='employee_files/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.employee}: {self.title}'


class EmployeeRequestType(models.Model):
    title = models.CharField(max_length=100)
    needs_approval = models.BooleanField(default=False)
    description = models.TextField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title}'


class EmployeeRequest(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='requests')
    title = models.CharField(max_length=100)
    request_type = models.ForeignKey(EmployeeRequestType, on_delete=models.CASCADE)
    description = models.TextField(max_length=5000)
    status = models.CharField(max_length=20, choices=(
        ('waiting', 'در انتظار بررسی'),
        ('accepted', 'تایید شده'),
        ('rejected', 'رد شده')
    ), default='waiting')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.employee}: {self.title}'


class EmploymentResume(models.Model):
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    national_code = models.CharField(max_length=10, null=True)
    birth_date = models.DateField()
    resume_file = models.FileField(upload_to='hire/resume_files/', null=True, blank=True)
    phone_number = models.CharField(max_length=11)
    description = models.TextField(max_length=5000)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='resumes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class EmployeeArrival(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.employee}: {self.created_at}'


class EmployeeOvertime(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='overtimes')
    date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=1)
    description = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='approved_overtimes')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.employee}: {self.date}'
