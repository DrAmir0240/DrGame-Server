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


@admin.register(models.ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.ProductCompany)
class ProductCompanyAdmin(admin.ModelAdmin):
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


@admin.register(models.Game)
class GameAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.GameImage)
class GameImageAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.DocCategory)
class DocCategoryAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.DocSubCategory)
class DocSubCategoryAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.Document)
class DocumentAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.RealAssetsCategory)
class RealAssetsCategoryAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.RealAssetsSubCategory)
class RealAssetsSubCategoryAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'


@admin.register(models.RealAssets)
class RealAssetsAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'
