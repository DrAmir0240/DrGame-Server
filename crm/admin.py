from django.contrib import admin

from accounting.models import Wallet
from crm.models import Customer, B2BProfile, CustomerWishlist


class B2BProfileInline(admin.TabularInline):
    model = B2BProfile
    extra = 0


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "get_phone",
        "get_full_name",
        "get_wallet_balance",
        "is_deleted",
    )
    list_filter = ("is_deleted",)
    search_fields = ("user__phone", "user__first_name", "user__last_name")
    readonly_fields = ("created_at", "updated_at")
    inlines = [B2BProfileInline]

    def get_phone(self, obj):
        return obj.user.phone

    get_phone.short_description = "Phone"

    def get_full_name(self, obj):
        return obj.user.full_name()

    get_full_name.short_description = "Full Name"

    def get_wallet_balance(self, obj):
        try:
            return f"{obj.user.wallet.balance:,} T"
        except Wallet.DoesNotExist:
            return "\u2014"

    get_wallet_balance.short_description = "Wallet Balance"


@admin.register(B2BProfile)
class B2BProfileAdmin(admin.ModelAdmin):
    list_display = (
        "customer",
        "business_title",
        "debt_amount_max",
        "discount",
        "is_deleted",
    )
    search_fields = ("business_title", "customer__user__phone")
    list_filter = ("is_deleted",)


@admin.register(CustomerWishlist)
class CustomerWishlistAdmin(admin.ModelAdmin):
    list_display = ("customer", "content_type", "object_id", "created_at")
    list_filter = ("is_deleted",)
    search_fields = ("customer__user__phone",)
