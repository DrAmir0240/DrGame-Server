from django.contrib import admin

from accounting.models import (
    BankAccount,
    AccountSide,
    InvoiceCategory,
    Invoice,
    InvoiceItem,
    PayrollDetail,
    Transaction,
    Wallet,
    WalletTransaction,
)


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ("title", "account_number", "sheba", "is_deleted", "created_at")
    search_fields = ("title", "account_number", "sheba")
    list_filter = ("is_deleted",)


@admin.register(AccountSide)
class AccountSideAdmin(admin.ModelAdmin):
    list_display = ("__str__", "type", "object_id", "is_deleted", "created_at")
    search_fields = ("name",)
    list_filter = ("type", "is_deleted")


@admin.register(InvoiceCategory)
class InvoiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "direction", "is_deleted", "created_at")
    search_fields = ("title",)
    list_filter = ("direction", "is_deleted")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "account_side",
        "category",
        "amount",
        "paid_amount",
        "remaining_amount",
        "status",
        "payment_status",
        "is_payroll",
        "is_deleted",
        "created_at",
    )
    search_fields = ("account_side__name", "description")
    list_filter = ("status", "payment_status", "is_payroll", "is_deleted", "category")
    readonly_fields = ("paid_amount", "created_at", "updated_at")


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "invoice",
        "quantity",
        "unit_price",
        "discount",
        "total_price",
        "is_deleted",
        "created_at",
    )
    search_fields = ("title", "invoice__id")
    list_filter = ("is_deleted",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(PayrollDetail)
class PayrollDetailAdmin(admin.ModelAdmin):
    list_display = (
        "invoice",
        "base_salary",
        "gross_salary",
        "total_deductions",
        "net_salary",
        "work_days",
        "overtime_hours",
        "created_at",
    )
    search_fields = ("invoice__id",)
    readonly_fields = (
        "gross_salary",
        "total_deductions",
        "net_salary",
        "created_at",
        "updated_at",
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "account_side",
        "invoice",
        "amount",
        "direction",
        "bank_account",
        "is_deleted",
        "created_at",
    )
    search_fields = ("account_side__name", "description", "invoice__id")
    list_filter = ("direction", "is_deleted", "bank_account")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "is_active", "created_at")
    search_fields = ("user__phone", "user__first_name", "user__last_name")
    list_filter = ("is_active", "is_deleted")
    readonly_fields = ("balance", "created_at", "updated_at")

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "wallet",
        "type",
        "amount",
        "status",
        "balance_before",
        "balance_after",
        "created_at",
    )
    list_filter = ("type", "status")
    search_fields = ("wallet__user__phone", "description")
    readonly_fields = [f.name for f in WalletTransaction._meta.fields]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False
