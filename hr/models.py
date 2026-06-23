from django.db import models
from users.models import CustomUser


# Create your models here.
class EmployeeRole(models.Model):
    # Base Info
    role_name = models.CharField(max_length=100)
    description = models.TextField(max_length=5000)
    # Permissions
    access_to_dashboard = models.BooleanField(default=False)
    can_read_task_manager = models.BooleanField(default=False)
    can_write_task_manager = models.BooleanField(default=False)
    can_read_accounting = models.BooleanField(default=False)
    can_write_accounting = models.BooleanField(default=False)
    can_read_inventory = models.BooleanField(default=False)
    can_write_inventory = models.BooleanField(default=False)
    access_to_all_inventory = models.BooleanField(default=False)
    can_read_orders = models.BooleanField(default=False)
    can_write_orders = models.BooleanField(default=False)
    can_read_account_orders = models.BooleanField(default=False)
    can_write_account_orders = models.BooleanField(default=False)
    access_to_all_accounts = models.BooleanField(default=False)
    is_account_employee = models.BooleanField(default=False)
    can_read_repairs = models.BooleanField(default=False)
    can_write_repairs = models.BooleanField(default=False)
    can_read_hr = models.BooleanField(default=False)
    can_write_hr = models.BooleanField(default=False)
    can_read_site = models.BooleanField(default=False)
    can_write_site = models.BooleanField(default=False)
    can_read_branch = models.BooleanField(default=False)
    can_write_branch = models.BooleanField(default=False)
    can_read_docs = models.BooleanField(default=False)
    can_write_docs = models.BooleanField(default=False)
    can_change_setting = models.BooleanField(default=False)
    access_to_messenger = models.BooleanField(default=False)
    can_start_chat = models.BooleanField(default=False)

    def __str__(self):
        return {self.role_name}


class Employee(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employee')
    profile_picture = models.ImageField(null=True, upload_to='profile_pictures/hr/')
    role = models.ForeignKey(EmployeeRole, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    national_code = models.CharField(max_length=10, null=True)
    employee_id = models.CharField(max_length=11, null=True)
    balance = models.IntegerField(default=0)
    has_commission = models.BooleanField(default=False, null=True, blank=True)
    commission_amount = models.IntegerField(default=0, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Repairman(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='repairman')
    profile_picture = models.ImageField(null=True, upload_to='profile_pictures/repairmen/')
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    national_code = models.CharField(max_length=10, null=True)
    balance = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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


class EmployeeRequest(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    request_type = models.CharField(max_length=20, choices=(
        ('leave', 'مرخصی'),
        ('favorable', 'مساعده'),
        ('miscellaneous', 'متفرقه')
    ))
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


class EmployeeHire(models.Model):
    full_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    resume_file = models.FileField(upload_to='hire/resume_files/', null=True, blank=True)
    phone_number = models.CharField(max_length=11)
    description = models.TextField(max_length=5000)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.full_name}'
