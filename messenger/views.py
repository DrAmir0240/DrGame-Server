from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from users.auth import CustomJWTAuthentication
from hr.models import Employee
from hr.serializers import EmployeeSerializer
from messenger.models import ChatRoom, Message, Membership
from messenger.serializers import (
    ChatRoomSerializer,
    ChatRoomCreateSerializer,
    MessageSerializer,
    MessageEditSerializer,
    ChatRoomUpdateSerializer,
)
from users.permissions import IsMainManager, IsEmployee


class ChatRoomListView(generics.ListAPIView):
    """
    List of chats the current user is a member of
    """

    serializer_class = ChatRoomSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        # correct related_name: memberships__user or users
        return ChatRoom.objects.filter(memberships__user=self.request.user).distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response(
                {"message": "User has no conversations"}, status=status.HTTP_200_OK
            )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChatRoomCreateView(generics.CreateAPIView):
    """
    Create a new chat (only MainManager can create)
    group, channel, pv
    """

    serializer_class = ChatRoomCreateSerializer
    permission_classes = [IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class EmployeeListView(generics.ListAPIView):
    """
    List of employees to add to a chat or to create a chat (only MainManager)
    """

    serializer_class = EmployeeSerializer
    queryset = Employee.objects.filter()
    permission_classes = [IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class ChatRoomDeleteView(generics.DestroyAPIView):
    queryset = ChatRoom.objects.all()
    permission_classes = [IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def perform_destroy(self, instance: ChatRoom):
        user = self.request.user
        # only the owner may delete
        if instance.owner_id != user.id:
            raise PermissionDenied(
                "You do not have permission to delete this chat room."
            )
        instance.delete()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "chat successfully deleted"}, status=status.HTTP_200_OK
        )


class ChatMessagesListView(generics.ListAPIView):
    """
    List messages of a specific chat (only chat members have access)
    Returns a notification message if there are no messages
    """

    serializer_class = MessageSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        chat_id = self.kwargs["pk"]
        chat = get_object_or_404(ChatRoom, pk=chat_id)
        if not chat.users.filter(id=self.request.user.id).exists():
            raise PermissionDenied("You are not a member of this chat.")
        return chat.messages.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response(
                {"message": "There are no messages in this conversation", "messages": []},
                status=status.HTTP_200_OK,
            )
        return super().list(request, *args, **kwargs)


class ChatRoomUpdateView(generics.UpdateAPIView):
    """
    Edit name/members. Only the owner is allowed.
    """

    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomUpdateSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def get_serializer_context(self):
        # to access request in the serializer
        ctx = super().get_serializer_context()
        return ctx


class AddMember(generics.CreateAPIView):
    """
    Add an Employee to a room (only for group/channel)
    """

    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request, *args, **kwargs):
        chat_id = kwargs.get("chat_id")
        employee_id = request.data.get("employee_id")

        if not chat_id or not employee_id:
            return Response(
                {"detail": "chat_id and employee_id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        chat = get_object_or_404(ChatRoom, id=chat_id)

        if chat.is_private:
            return Response(
                {"detail": "Members can be added only to group or channel chats."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # only the owner may add (change this line if your policy differs)
        if chat.owner_id != request.user.id:
            raise PermissionDenied("Only the owner can add members to this chat.")

        try:
            employee = Employee.objects.select_related("user").get(id=employee_id)
        except Employee.DoesNotExist:
            return Response(
                {"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # already a member?
        if chat.users.filter(id=employee.user_id).exists():
            return Response(
                {"detail": "User is already a member of the chat."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        is_muted_flag = True if chat.is_channel else False
        Membership.objects.create(
            user=employee.user, chat_room=chat, is_muted=is_muted_flag
        )

        return Response(
            {"detail": "Member added successfully."}, status=status.HTTP_201_CREATED
        )


class RemoveMember(generics.DestroyAPIView):
    """
    Remove a member from a room (only for group/channel)
    """

    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def delete(self, request, *args, **kwargs):
        chat_id = kwargs.get("chat_id")
        user_id = request.data.get("user_id")

        if not chat_id or not user_id:
            return Response(
                {"detail": "chat_id and user_id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        chat = get_object_or_404(ChatRoom, id=chat_id)

        if chat.is_private:
            return Response(
                {"detail": "Members can be removed only from group or channel chats."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # the owner cannot be removed
        if chat.owner_id == int(user_id):
            return Response(
                {"detail": "Cannot remove the owner of the chat."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # only the owner may delete (change this if the policy differs)
        if chat.owner_id != request.user.id:
            raise PermissionDenied("Only the owner can remove members from this chat.")

        membership = Membership.objects.filter(chat_room=chat, user_id=user_id).first()
        if not membership:
            return Response(
                {"detail": "User is not a member of this chat."},
                status=status.HTTP_404_NOT_FOUND,
            )

        membership.delete()
        # return 200 because we have a body (not 204)
        return Response(
            {"detail": "Member removed successfully."}, status=status.HTTP_200_OK
        )


class SendMessageView(generics.CreateAPIView):
    """
    Send a message to a chat (chat members only)
    """

    serializer_class = MessageSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def perform_create(self, serializer):
        # the Serializer validate already checked membership
        serializer.save(sender=self.request.user)


class DeleteMessageView(generics.UpdateAPIView):
    """
    Delete a message (Soft Delete) only by the message sender
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
    Edit a message only by the message sender
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
