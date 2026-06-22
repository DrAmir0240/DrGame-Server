from django.db import models

from hr.models import Employee


# Create your models here.
class PlanedTask(models.Model):
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
        ('in_progress', 'در حال انجام'),
        ('done', 'انجام شده')
    ))
    start_date = models.DateField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.employee}: {self.title}'


class DailyTask(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=True, blank=True)
    voice = models.FileField(upload_to='employee_files/tasks/voices', null=True, blank=True)
    type = models.CharField(max_length=20, choices=(
        ('Personal', 'شخصی'),
        ('Organize', 'سازمانی')
    ))
    description = models.TextField(max_length=5000, null=True, blank=True)
    is_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.employee}: {self.title}'
