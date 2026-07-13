from django.contrib import admin

from psn import models


# Register your models here.
@admin.register(models.SonyAccountStatus)
class SonyAccountStatusAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.SonyAccountBank)
class SonyAccountBankAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.SonyAccount)
class SonyAccountAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.SonyAccountGame)
class SonyAccountGameAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'
