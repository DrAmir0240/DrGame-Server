from django.contrib import admin
from django.utils import timezone

from support.models import Ticket, TicketMessage


class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 0
    readonly_fields = ["created_at"]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "customer",
        "category",
        "status",
        "priority",
        "assigned_to",
        "created_at",
    ]
    list_filter = ["status", "priority", "category"]
    search_fields = ["title", "customer__user__phone"]
    list_editable = ["status", "assigned_to"]
    inlines = [TicketMessageInline]
    readonly_fields = ["created_at", "updated_at", "closed_at"]

    def save_model(self, request, obj, form, change):
        if "status" in form.changed_data and obj.status == "closed":
            obj.closed_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ["id", "ticket", "sender_type", "is_internal", "created_at"]
    list_filter = ["sender_type", "is_internal"]
    readonly_fields = ["created_at"]
