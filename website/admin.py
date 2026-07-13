from django.contrib import admin

from website import models


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


@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_deleted', 'created_at']


@admin.register(models.CartItem)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'product', 'quantity', 'is_deleted', 'updated_at', ]


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


@admin.register(models.BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'slug', 'title', 'author', 'status', 'created_at']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(models.AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'subtitle', 'content', 'created_at', ]

    def has_add_permission(self, request):
        return not models.AboutUs.objects.exists()


@admin.register(models.ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ['id', 'address', 'phone', 'email', 'opening_hours', 'instagram_url', 'created_at']

    def has_add_permission(self, request):
        return not models.ContactUs.objects.exists()


@admin.register(models.ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'phone', 'subject', 'message_preview', 'user', 'is_deleted']

    def message_preview(self, obj):
        return obj.message[:100] + '...' if len(obj.subject) > 10 else obj.message

    message_preview.short_description = 'Message'


@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'slug', 'description', 'price', 'status', 'created_at', 'updated_at', ]
    prepopulated_fields = {'slug': ('title',)}


@admin.register(models.Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'slug', 'description', 'status', 'course', 'duration', 'priority', 'created_at',
                    'updated_at', ]
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['priority']


@admin.register(models.HomeBanner)
class HomeBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_chosen', 'order')
    list_editable = ('is_chosen', 'order')
    list_filter = ('is_chosen',)
    search_fields = ('title',)
