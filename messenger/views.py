from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from accounts.auth import CustomJWTAuthentication
from employees.models import Employee
from employees.serializers import EmployeeSerializer
from messenger.models import ChatRoom, Message, Membership
from messenger.serializers import (
    ChatRoomSerializer, ChatRoomCreateSerializer,
    MessageSerializer, MessageEditSerializer, ChatRoomUpdateSerializer
)
from accounts.permissions import IsMainManager, IsEmployee
class ChatRoomListView(generics.ListAPIView):
    """
    لیست چت‌هایی که کاربر فعلی عضو آن است
    """
    serializer_class = ChatRoomSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        # related_name درست: memberships__user یا users
        return ChatRoom.objects.filter(memberships__user=self.request.user).distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response(
                {"message": "کاربر گفت‌وگویی ندارد"},
                status=status.HTTP_200_OK
            )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChatRoomCreateView(generics.CreateAPIView):
    """
    ایجاد چت جدید (فقط MainManager می‌تواند بسازد)
    group, channel, pv
    """
    serializer_class = ChatRoomCreateSerializer
    permission_classes = [IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class EmployeeListView(generics.ListAPIView):
    """
    لیست کارکنان برای افزودن به چت یا ایجاد چت (فقط MainManager)
    """
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.filter(has_access_to_messenger=True)
    permission_classes = [IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class ChatRoomDeleteView(generics.DestroyAPIView):
    queryset = ChatRoom.objects.all()
    permission_classes = [IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def perform_destroy(self, instance: ChatRoom):
        user = self.request.user
        # فقط مالک اجازه حذف دارد
        if instance.owner_id != user.id:
            raise PermissionDenied("You do not have permission to delete this chat room.")
        instance.delete()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "chat successfully deleted"}, status=status.HTTP_200_OK)


class ChatMessagesListView(generics.ListAPIView):
    """
    لیست پیام‌های یک چت خاص (فقط اعضای چت دسترسی دارند)
    اگر پیام وجود نداشت پیام اطلاع‌رسانی می‌دهد
    """
    serializer_class = MessageSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        chat_id = self.kwargs['pk']
        chat = get_object_or_404(ChatRoom, pk=chat_id)
        if not chat.users.filter(id=self.request.user.id).exists():
            raise PermissionDenied("You are not a member of this chat.")
        return chat.messages.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({
                "message": "هیچ پیامی در این گفتگو وجود ندارد",
                "messages": []
            }, status=status.HTTP_200_OK)
        return super().list(request, *args, **kwargs)


class ChatRoomUpdateView(generics.UpdateAPIView):
    """
    ویرایش نام/اعضا. فقط مالک اجازه دارد.
    """
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomUpdateSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def get_serializer_context(self):
        # برای دسترسی به request در serializer
        ctx = super().get_serializer_context()
        return ctx


class AddMember(generics.CreateAPIView):
    """
    افزودن یک Employee به روم (فقط برای group/channel)
    """
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request, *args, **kwargs):
        chat_id = kwargs.get('chat_id')
        employee_id = request.data.get('employee_id')

        if not chat_id or not employee_id:
            return Response({"detail": "chat_id and employee_id are required."}, status=status.HTTP_400_BAD_REQUEST)

        chat = get_object_or_404(ChatRoom, id=chat_id)

        if chat.is_private:
            return Response({"detail": "Members can be added only to group or channel chats."},
                            status=status.HTTP_400_BAD_REQUEST)

        # فقط owner اجازه‌ی افزودن دارد (اگر سیاست شما متفاوت است، این خط را تغییر بده)
        if chat.owner_id != request.user.id:
            raise PermissionDenied("Only the owner can add members to this chat.")

        try:
            employee = Employee.objects.select_related('user').get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

        # عضو بودن قبلی؟
        if chat.users.filter(id=employee.user_id).exists():
            return Response({"detail": "User is already a member of the chat."}, status=status.HTTP_400_BAD_REQUEST)

        is_muted_flag = True if chat.is_channel else False
        Membership.objects.create(user=employee.user, chat_room=chat, is_muted=is_muted_flag)

        return Response({"detail": "Member added successfully."}, status=status.HTTP_201_CREATED)


class RemoveMember(generics.DestroyAPIView):
    """
    حذف عضو از روم (فقط برای group/channel)
    """
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def delete(self, request, *args, **kwargs):
        chat_id = kwargs.get('chat_id')
        user_id = request.data.get('user_id')

        if not chat_id or not user_id:
            return Response({"detail": "chat_id and user_id are required."}, status=status.HTTP_400_BAD_REQUEST)

        chat = get_object_or_404(ChatRoom, id=chat_id)

        if chat.is_private:
            return Response({"detail": "Members can be removed only from group or channel chats."},
                            status=status.HTTP_400_BAD_REQUEST)

        # مالک را نمی‌توان حذف کرد
        if chat.owner_id == int(user_id):
            return Response({"detail": "Cannot remove the owner of the chat."}, status=status.HTTP_400_BAD_REQUEST)

        # فقط owner اجازه‌ی حذف دارد (در صورت سیاست دیگر، تغییر بده)
        if chat.owner_id != request.user.id:
            raise PermissionDenied("Only the owner can remove members from this chat.")

        membership = Membership.objects.filter(chat_room=chat, user_id=user_id).first()
        if not membership:
            return Response({"detail": "User is not a member of this chat."}, status=status.HTTP_404_NOT_FOUND)

        membership.delete()
        # 200 بر می‌گردانیم چون بدنه داریم (نه 204)
        return Response({"detail": "Member removed successfully."}, status=status.HTTP_200_OK)


class SendMessageView(generics.CreateAPIView):
    """
    ارسال پیام به یک چت (فقط اعضای چت)
    """
    serializer_class = MessageSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def perform_create(self, serializer):
        # validate در Serializer قبلاً عضویت را چک کرده است
        serializer.save(sender=self.request.user)


class DeleteMessageView(generics.UpdateAPIView):
    """
    حذف پیام (Soft Delete) فقط توسط فرستنده پیام
    """
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def perform_update(self, serializer):
        message = self.get_object()
        if message.sender_id != self.request.user.id:
            raise PermissionDenied("You can't delete this message.")
        serializer.instance.is_deleted = True
        serializer.instance.text = None
        serializer.save()


class EditMessageView(generics.UpdateAPIView):
    """
    ویرایش پیام فقط توسط فرستنده پیام
    """
    serializer_class = MessageEditSerializer
    queryset = Message.objects.all()
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def perform_update(self, serializer):
        message = self.get_object()
        if message.sender_id != self.request.user.id:
            raise PermissionDenied("You can't edit this message.")
        serializer.save()