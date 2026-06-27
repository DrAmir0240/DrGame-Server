from django.contrib import admin

from task_manager import models


# Register your models here.
@admin.register(models.PlannedTask)
class PlanedTaskAdmin(admin.ModelAdmin):
    class Meta:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.DailyTask)
class DailyTaskAdmin(admin.ModelAdmin):
    class Meta:
        fields = '__all__'
        search_fields = '__all__'
