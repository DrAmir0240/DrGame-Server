from django.contrib import admin

from website import models


@admin.register(models.BlogPostCategory)
class BlogPostCategoryAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'
@admin.register(models.BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'
@admin.register(models.BlogPostImage)
class BlogPostImageAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'
@admin.register(models.GameCategory)
class GameCategoryAdmin(admin.ModelAdmin):
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
@admin.register(models.StoreProductCategory)
class StoreProductCategoryAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'
@admin.register(models.StoreProduct)
class StoreProductAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'
@admin.register(models.StoreProductImage)
class StoreProductImageAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'
@admin.register(models.ProductCart)
class ProductCartAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'
@admin.register(models.ProductCartItem)
class ProductCartItemAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'
@admin.register(models.GameCart)
class GameCartAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'
@admin.register(models.GameCartItem)
class GameCartItemAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'
@admin.register(models.Video)
class VideoAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'
@admin.register(models.HomeBanner)
class HomeBannerAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'
@admin.register(models.HomeSection)
class HomeSectionAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'
@admin.register(models.HomeSectionItem)
class HomeSectionItemAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'
@admin.register(models.AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    class Media:
        fields = '__all__'
        search_fields = '__all__'
