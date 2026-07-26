from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from crm.models import Customer
from hr.models import Employee


class Ticket(models.Model):
    STATUS_CHOICES = (
        ("open", "باز"),
        ("in_progress", "در حال بررسی"),
        ("waiting", "منتظر پاسخ مشتری"),
        ("closed", "بسته"),
    )
    PRIORITY_CHOICES = (
        ("low", "کم"),
        ("medium", "متوسط"),
        ("high", "زیاد"),
    )
    CATEGORY_CHOICES = (
        ("order", "مشکل سفارش"),
        ("payment", "مشکل پرداخت"),
        ("account", "مشکل اکانت"),
        ("general", "عمومی"),
    )

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="tickets"
    )
    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
    )
    title = models.CharField(max_length=200)
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default="general"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="medium"
    )
    order_content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True
    )
    order_object_id = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.pk} {self.title}"


class TicketMessage(models.Model):
    SENDER_TYPE_CHOICES = (
        ("customer", "مشتری"),
        ("employee", "کارمند"),
        ("system", "سیستم"),
    )

    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name="messages"
    )
    sender_type = models.CharField(max_length=10, choices=SENDER_TYPE_CHOICES)
    sender_customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True
    )
    sender_employee = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True
    )
    body = models.TextField()
    attachment = models.FileField(
        upload_to="tickets/attachments/", null=True, blank=True
    )
    is_internal = models.BooleanField(
        default=False, help_text="یادداشت داخلی — مشتری نمی‌بینه"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message #{self.pk} on Ticket #{self.ticket_id}"
