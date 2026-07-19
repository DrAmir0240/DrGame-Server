from crm.models import Customer, B2BProfile
from django.contrib import admin


# Register your models here.

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    class Meta:
        fields = "__all__"
        search_fields = "__all__"


@admin.register(B2BProfile)
class B2BProfileAdmin(admin.ModelAdmin):
    class Meta:
        fields = "__all__"
        search_fields = "__all__"