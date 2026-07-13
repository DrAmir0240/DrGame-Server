from django.contrib import admin
from docs import models


# Register your models here.
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
