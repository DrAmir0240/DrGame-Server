from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, APIKey, MainManager, OTP


# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['phone', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active']
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'password1', 'password2', 'is_staff', 'is_active', 'is_superuser')}
         ),
    )
    search_fields = ('phone',)
    ordering = ('phone',)
    filter_horizontal = ('groups', 'user_permissions',)


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'key', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('client_name', 'key')


@admin.register(MainManager)
class MainManagerAdmin(admin.ModelAdmin):
    class Meta:
        list_display = '__all__'
        search_fields = '__all__'


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    class Meta:
        list_display = '__all__'
        search_fields = '__all__'
