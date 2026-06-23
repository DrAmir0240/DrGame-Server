from django.contrib import admin

from task_manager import models


# Register your models here.
@admin.register(models.PlanedTask)
class PlanedTaskAdmin(admin.ModelAdmin):
    class Meta:
        fields = '__all__'
        search_fields = '__all__'
