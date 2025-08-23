from django.db import models

from DrGame import settings
from accounts.models import CustomUser


# Create your models here.

class ChatRoom(models.Model):
    # انواع چت
    PV = 'pv'
    GROUP = 'group'
    CHANNEL = 'channel'
    CHAT_TYPES = (
        (PV, 'Private'),
        (GROUP, 'Group'),
        (CHANNEL, 'Channel'),
    )

    name = models.CharField(
        max_length=100,
        blank=True,  # برای pv ممکن است نام نمایشی از عضو مقابل بیاید
    )
    type = models.CharField(
        max_length=10,
        choices=CHAT_TYPES,  # محدودسازی به انواع تعریف‌شده
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_rooms',  # همه‌ی روم‌هایی که کاربر مالک‌شان است
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # شرکت‌کنندگان: به‌صورت M2M از طریق Membership
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Membership',
        related_name='chat_rooms'  # همه‌ی روم‌هایی که کاربر عضو‌شان است
    )

    class Meta:
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']  # روم‌های تازه‌تر بالاتر

    def __str__(self):
        # نمایش خوانا در ادمین
        base = self.name or f'Room-{self.pk}'
        return f'{base} ({self.type})'

    # هلپرهای خواناتر
    @property
    def is_private(self):
        return self.type == self.PV

    @property
    def is_group(self):
        return self.type == self.GROUP

    @property
    def is_channel(self):
        return self.type == self.CHANNEL


class Membership(models.Model):
    # نگاشت کاربر به اتاق
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='memberships',  # همه‌ی عضویت‌های کاربر
    )
    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='memberships',  # همه‌ی عضویت‌های یک روم
    )
    is_admin = models.BooleanField(default=False)   # مدیر روم؟
    is_muted = models.BooleanField(default=False)   # ساکت (برای channel معمولاً True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'chat_room')  # هر کاربر در هر روم فقط یک بار
        indexes = [
            models.Index(fields=['chat_room', 'user']),
        ]

    def __str__(self):
        return f'{self.user_id} in room {self.chat_room_id}'


class Message(models.Model):
    # پیام‌های یک روم
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages',  # پیام‌های یک روم
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,  # اگر کاربر حذف شد، پیام بماند ولی sender نال
        related_name='sent_messages',
    )
    text = models.TextField(
        blank=True,
        null=True,  # برای Soft Delete متن را نال می‌کنیم
    )
    reply_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies',  # پیام‌هایی که به این پاسخ داده‌اند
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']  # پیام‌های تازه‌تر اول
        indexes = [
            models.Index(fields=['room', 'created_at']),
        ]

    def __str__(self):
        return f'Msg {self.pk} in room {self.room_id}'
