from django.urls import path
from messenger.views import (
    ChatRoomListView, ChatRoomCreateView,
    ChatMessagesListView, SendMessageView,
    DeleteMessageView, EditMessageView, ChatRoomDeleteView, RemoveMember, AddMember, EmployeeListView
)

urlpatterns = [
    # لیست چت‌های کاربر
    path('chats/', ChatRoomListView.as_view(), name='chat-list'),
    path('employee-list/', EmployeeListView.as_view(), name='employee-list'),

    # ایجاد چت جدید (فقط MainManager)
    path('chats/new/', ChatRoomCreateView.as_view(), name='chat-create'),

    # لیست پیام‌های یک چت
    path('chats/<int:pk>/', ChatMessagesListView.as_view(), name='chat-messages'),
    # لیست پیام‌های یک چت
    path('chats/<int:pk>/remove/', ChatRoomDeleteView.as_view(), name='chatroom-delete'),
    path('chats/<int:pk>/add-member/', AddMember.as_view(), name='chatroom-add-member'),
    path('chats/<int:pk>/remove-member/', RemoveMember.as_view(), name='chatroom-remove-member'),

    # ارسال پیام
    path('messages/send/', SendMessageView.as_view(), name='send-message'),

    # حذف پیام
    path('messages/<int:pk>/delete/', DeleteMessageView.as_view(), name='delete-message'),

    # ویرایش پیام
    path('messages/<int:pk>/edit/', EditMessageView.as_view(), name='edit-message'),
]
