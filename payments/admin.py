from django.contrib import admin
from payments.models import Transaction, Order, RepairOrder, GameOrder, \
    RepairOrderType


# Register your models here.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(GameOrder)
class GameOrderAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(RepairOrderType)
class RepairOrderTypeAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(RepairOrder)
class RepairOrderAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'
