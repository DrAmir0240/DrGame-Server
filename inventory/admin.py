from django.contrib import admin
from inventory import models
from inventory.models import Supplier


# Register your models here.
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'phone', 'email', 'national_id', 'tax_id', 'is_active', 'is_deleted', 'created_at')
    search_fields = ('name', 'phone', 'email', 'national_id', 'tax_id', 'account_number', 'sheba')
    list_filter = ('type', 'is_active', 'is_deleted')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(models.ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.ProductEntity)
class ProductEntityAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'
