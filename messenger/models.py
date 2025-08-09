from django.db import models

from accounts.models import CustomUser


# Create your models here.
class ChatRoom(models.Model):
    CHAT_TYPES = (
        ('pv', 'Private'),
        ('group', 'Group'),
        ('channel', 'Channel'),
    )
    name = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=10, choices=CHAT_TYPES)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='owned_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField(CustomUser, related_name='chat_rooms', through='Membership')


class Membership(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='memberships')
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    is_muted = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'chat_room')


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    text = models.TextField(blank=True, null=True)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
