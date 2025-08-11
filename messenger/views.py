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


# --------------------
# Chat List
# --------------------
class ChatRoomListView(generics.ListAPIView):
    """
    لیست چت‌هایی که کاربر فعلی عضو آن است
    """
    serializer_class = ChatRoomSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        return ChatRoom.objects.filter(users=self.request.user)


# --------------------
# New Chat
# --------------------
class ChatRoomCreateView(generics.CreateAPIView):
    """
    ایجاد چت جدید (فقط MainManager می‌تواند بسازد)
    """
    serializer_class = ChatRoomCreateSerializer
    permission_classes = [IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


# --------------------
# Employee List
# --------------------
class EmployeeListView(generics.ListAPIView):
    """
        لیست کارکنان برای افزودن به چت ی ایجاد چت (فقط MainManager دسترسی دارد)
        """
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.filter(has_access_to_chat=True)
    permission_classes = [IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


# --------------------
# Delete Chat
# --------------------
class ChatRoomDeleteView(generics.DestroyAPIView):
    queryset = ChatRoom.objects.all()
    permission_classes = [IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def perform_destroy(self, instance):
        user = self.request.user
        # فقط مالک (owner) اجازه حذف دارد
        if instance.owner != user:
            raise PermissionDenied("You do not have permission to delete this chat room.")
        instance.delete()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "chat successfully deleted"}, status=status.HTTP_200_OK)


# --------------------
# Chat Messages List
# --------------------
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
        chat = ChatRoom.objects.get(pk=chat_id)
        if not chat.users.filter(id=self.request.user.id).exists():
            raise PermissionDenied("You are not a member of this chat.")
        return chat.messages.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({
                "message": "هیچ پیامی در این "
                           "گفتگو وجود ندارد",
                "messages": []
            }, status=status.HTTP_200_OK)
        return super().list(request, *args, **kwargs)


# --------------------
# Chat Edit
# --------------------
class ChatRoomUpdateView(generics.UpdateAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomUpdateSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


# --------------------
# Add Member To Chat
# --------------------
class AddMember(generics.CreateAPIView):
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request, *args, **kwargs):
        chat_id = kwargs.get('chat_id')
        employee_id = request.data.get('employee_id')

        if not chat_id or not employee_id:
            return Response({"detail": "chat_id and employee_id are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            chat = ChatRoom.objects.get(id=chat_id)
        except ChatRoom.DoesNotExist:
            return Response({"detail": "Chat room not found."}, status=status.HTTP_404_NOT_FOUND)

        if chat.type not in ['group', 'channel']:
            return Response({"detail": "Members can be added only to group or channel chats."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            employee = Employee.objects.select_related('user').get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

        # چک کن اگر عضو هست قبلا
        if chat.users.filter(id=employee.user.id).exists():
            return Response({"detail": "User is already a member of the chat."}, status=status.HTTP_400_BAD_REQUEST)

        is_muted_flag = True if chat.type == 'channel' else False
        Membership.objects.create(user=employee.user, chat_room=chat, is_muted=is_muted_flag)

        return Response({"detail": "Member added successfully."}, status=status.HTTP_201_CREATED)


# --------------------
# remove Member From Chat
# --------------------
class RemoveMember(generics.DestroyAPIView):
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def delete(self, request, *args, **kwargs):
        chat_id = kwargs.get('chat_id')
        user_id = request.data.get('user_id')

        if not chat_id or not user_id:
            return Response({"detail": "chat_id and user_id are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            chat = ChatRoom.objects.get(id=chat_id)
        except ChatRoom.DoesNotExist:
            return Response({"detail": "Chat room not found."}, status=status.HTTP_404_NOT_FOUND)

        if chat.type not in ['group', 'channel']:
            return Response({"detail": "Members can be removed only from group or channel chats."},
                            status=status.HTTP_400_BAD_REQUEST)

        if chat.owner.id == int(user_id):
            return Response({"detail": "Cannot remove the owner of the chat."}, status=status.HTTP_400_BAD_REQUEST)

        # چک کن عضو هست
        try:
            membership = Membership.objects.get(chat_room=chat, user_id=user_id)
        except Membership.DoesNotExist:
            return Response({"detail": "User is not a member of this chat."}, status=status.HTTP_404_NOT_FOUND)

        membership.delete()
        return Response({"detail": "Member removed successfully."}, status=status.HTTP_204_NO_CONTENT)


# --------------------
# Send Message
# --------------------
class SendMessageView(generics.CreateAPIView):
    """
    ارسال پیام به یک چت (فقط اعضای چت)
    """
    serializer_class = MessageSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def perform_create(self, serializer):
        chat = serializer.validated_data['room']
        if not chat.users.filter(id=self.request.user.id).exists():
            raise PermissionDenied("You are not a member of this chat.")
        serializer.save(sender=self.request.user)


# --------------------
# Delete Message
# --------------------
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
        if message.sender != self.request.user:
            raise PermissionDenied("You can't delete this message.")
        serializer.instance.is_deleted = True
        serializer.instance.text = None
        serializer.save()


# --------------------
# Edit Message
# --------------------
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
        if message.sender != self.request.user:
            raise PermissionDenied("You can't edit this message.")
        serializer.save()
