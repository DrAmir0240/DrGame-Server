from django.db import models

from DrGame import settings
from users.models import CustomUser


# Create your models here.

class ChatRoom(models.Model):
    # Chat types
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
        blank=True,  # for pv, the display name may come from the other member
    )
    type = models.CharField(
        max_length=10,
        choices=CHAT_TYPES,  # restrict to the defined types
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_rooms',  # all rooms the user owns
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Participants: M2M via Membership
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Membership',
        related_name='chat_rooms'  # all rooms the user is a member of
    )

    class Meta:
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']  # newer rooms first

    def __str__(self):
        # readable display in the admin
        base = self.name or f'Room-{self.pk}'
        return f'{base} ({self.type})'

    # more readable helpers
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
    # mapping of user to room
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='memberships',  # all memberships of the user
    )
    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='memberships',  # all memberships of a room
    )
    is_admin = models.BooleanField(default=False)   # room admin?
    is_muted = models.BooleanField(default=False)   # muted (usually True for channels)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'chat_room')  # each user only once per room
        indexes = [
            models.Index(fields=['chat_room', 'user']),
        ]

    def __str__(self):
        return f'{self.user_id} in room {self.chat_room_id}'


class Message(models.Model):
    # messages of a room
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages',  # messages of a room
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,  # keep the message but null the sender if the user is deleted
        related_name='sent_messages',
    )
    text = models.TextField(
        blank=True,
        null=True,  # null the text for soft delete
    )
    reply_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies',  # messages that replied to this one
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']  # newest messages first
        indexes = [
            models.Index(fields=['room', 'created_at']),
        ]

    def __str__(self):
        return f'Msg {self.pk} in room {self.room_id}'
