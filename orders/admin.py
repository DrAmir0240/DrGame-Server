from django.contrib import admin

from .models import (
    ProductOrderStage,
    ProductOrder,
    ProductOrderItem,
    RepairOrderStage,
    RepairOrderCategory,
    RepairOrder,
    RepairOrderDevice,
    SonyAccountOrderStage,
    SonyAccountOrderCategory,
    SonyAccountOrder,
    SonyAccountOrderConsole,
    SonyAccountOrderItem,
)


@admin.register(ProductOrderStage)
class ProductOrderStageAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_in_progress', 'is_in_waiting', 'employee_role', 'is_deleted', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('is_in_progress', 'is_in_waiting', 'is_deleted', 'employee_role')


@admin.register(ProductOrder)
class ProductOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'invoice', 'stage', 'amount', 'is_deleted', 'created_at')
    search_fields = ('customer__name', 'description')
    list_filter = ('is_deleted', 'stage')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ProductOrderItem)
class ProductOrderItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'product_order', 'quantity', 'unit_price', 'amount', 'is_deleted', 'created_at')
    search_fields = ('title', 'product_order__id')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(RepairOrderStage)
class RepairOrderStageAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_in_progress', 'is_in_waiting', 'employee_role', 'is_deleted', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('is_in_progress', 'is_in_waiting', 'is_deleted', 'employee_role')


@admin.register(RepairOrderCategory)
class RepairOrderCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'is_deleted', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('is_active', 'is_deleted')


@admin.register(RepairOrder)
class RepairOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'invoice', 'stage', 'category', 'repair_fee', 'final_amount', 'is_deleted', 'created_at')
    search_fields = ('customer__name',)
    list_filter = ('is_deleted', 'stage', 'category')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(RepairOrderDevice)
class RepairOrderDeviceAdmin(admin.ModelAdmin):
    list_display = ('title', 'serial_number', 'customer', 'repair_order', 'is_deleted', 'created_at')
    search_fields = ('title', 'serial_number', 'customer__name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SonyAccountOrderStage)
class SonyAccountOrderStageAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_in_progress', 'is_in_waiting', 'employee_role', 'is_deleted', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('is_in_progress', 'is_in_waiting', 'is_deleted', 'employee_role')


@admin.register(SonyAccountOrderCategory)
class SonyAccountOrderCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'rent_time_days', 'account_capacity')
    search_fields = ('title',)
    list_filter = ('type', 'account_capacity')


@admin.register(SonyAccountOrder)
class SonyAccountOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'invoice', 'stage', 'category', 'source', 'type', 'amount', 'is_deleted', 'created_at')
    search_fields = ('customer__name',)
    list_filter = ('source', 'type', 'is_deleted', 'stage', 'category')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SonyAccountOrderConsole)
class SonyAccountOrderConsoleAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'customer', 'sony_account_order', 'is_deleted', 'created_at')
    search_fields = ('serial_number', 'customer__name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SonyAccountOrderItem)
class SonyAccountOrderItemAdmin(admin.ModelAdmin):
    list_display = ('sony_account_order', 'sony_account', 'employee', 'created_at')
    search_fields = ('sony_account_order__id', 'sony_account__id')
    list_filter = ('employee',)
    readonly_fields = ('created_at', 'updated_at')