from django.contrib import admin
from hr import models


# Register your models here.
@admin.register(models.Permission)
class PermissionAdmin(admin.ModelAdmin):
    class Meta:
        fields = '__all__'
        search_fields = '__all__'


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


@admin.register(models.EmployeeFile)
class EmployeeFileAdmin(admin.ModelAdmin):
    class Meta:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.EmployeeRequestType)
class EmployeeRequestTypeAdmin(admin.ModelAdmin):
    class Meta:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.EmployeeRequest)
class EmployeeRequestAdmin(admin.ModelAdmin):
    class Meta:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.EmploymentResume)
class EmploymentResumeAdmin(admin.ModelAdmin):
    class Meta:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.EmployeeArrival)
class EmployeeArrivalAdmin(admin.ModelAdmin):
    class Meta:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.EmployeeOvertime)
class EmployeeOvertimeAdmin(admin.ModelAdmin):
    class Meta:
        fields = '__all__'
        search_fields = '__all__'
