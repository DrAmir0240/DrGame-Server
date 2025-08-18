from django.db import models
from accounts.models import CustomUser


# Create your models here.

class Employee(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employee')
    profile_picture = models.ImageField(null=True, upload_to='profile_pictures/employees/')
    role = models.CharField(max_length=14, choices=(
        ('recipient', 'صندوق دار'),
        ('account_setter', 'اکانت ستر'),
        ('data_uploader', 'دیتا آپلودر'),
        ('manager', 'مدیر داخلی')
    ), null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    national_code = models.CharField(max_length=10, null=True)
    employee_id = models.CharField(max_length=11, null=True)
    balance = models.IntegerField(default=0)
    has_commission = models.BooleanField(default=False)
    commission_amount = models.IntegerField(default=0)
    has_access_to_orders = models.BooleanField(default=False)
    has_access_to_game_order = models.BooleanField(default=False)
    has_access_to_accounts = models.BooleanField(default=False)
    has_access_to_site = models.BooleanField(default=False)
    has_access_to_customers = models.BooleanField(default=False)
    has_access_to_employees = models.BooleanField(default=False)
    has_access_to_add_users = models.BooleanField(default=False)
    has_access_to_transactions = models.BooleanField(default=False)
    has_access_to_calls = models.BooleanField(default=False)
    has_access_to_chat = models.BooleanField(default=False)
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


class EmployeeTask(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=True, blank=True)
    voice = models.FileField(upload_to='employee_files/tasks/voices', null=True, blank=True)
    type = models.CharField(max_length=20, choices=(
        ('Personal', 'شخصی'),
        ('Organize', 'سازمانی')
    ), null=True, blank=True, default='Personal')
    description = models.TextField(max_length=5000, null=True, blank=True)
    status = models.CharField(max_length=20, choices=(
        ('planed', 'برنامه ریزی شده'),
        ('in progress', 'در حال انجام'),
        ('done', 'انجام شده')
    ))
    deadline = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.employee}: {self.title}'
