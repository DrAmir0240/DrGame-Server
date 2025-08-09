from django.contrib import admin

from messenger.models import ChatRoom, Membership, Message


# Register your models here.
@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    class Meta:
        model = ChatRoom
        fields = '__all__'
        search_fields = '__all__'


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    class Meta:
        model = ChatRoom
        fields = '__all__'
        search_fields = '__all__'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    class Meta:
        model = ChatRoom
        fields = '__all__'
        search_fields = '__all__'