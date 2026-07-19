from django.contrib import admin
from hr import models


# Register your models here.
@admin.register(models.EmployeeRole)
class EmployeeRoleAdmin(admin.ModelAdmin):
    class Meta:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.Employee)
class EmployeeAdmin(admin.ModelAdmin):
    class Meta:
        fields = '__all__'
        search_fields = '__all__'


# NOTE: models.Repairman does not exist in hr.models — registration removed to
# unblock Django startup. Restore once the Repairman model is added.
# @admin.register(models.Repairman)
# class RepairmanAdmin(admin.ModelAdmin):
#     class Meta:
#         fields = '__all__'
#         search_fields = '__all__'


@admin.register(models.EmployeeFile)
class EmployeeFileAdmin(admin.ModelAdmin):
    class Meta:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.EmployeeRequest)
class EmployeeRequestAdmin(admin.ModelAdmin):
    class Meta:
        fields = '__all__'
        search_fields = '__all__'
