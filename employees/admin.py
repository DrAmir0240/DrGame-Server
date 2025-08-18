from django.contrib import admin
from employees import models


# Register your models here.
@admin.register(models.Employee)
class EmployeeAdmin(admin.ModelAdmin):
    class Meta:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.Repairman)
class RepairmanAdmin(admin.ModelAdmin):
    class Meta:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.EmployeeFile)
class EmployeeFileAdmin(admin.ModelAdmin):
    class Meta:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.EmployeeTask)
class EmployeeTaskAdmin(admin.ModelAdmin):
    class Meta:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.EmployeeRequest)
class EmployeeRequestAdmin(admin.ModelAdmin):
    class Meta:
        fields = '__all__'
        search_fields = '__all__'
