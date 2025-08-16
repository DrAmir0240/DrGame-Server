from logging import lastResort

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from employees.models import Employee
from .models import ChatRoom, Membership, Message
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class MembershipSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    member_type = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = ['user', 'is_admin', 'is_muted', 'joined_at', 'member_type', 'full_name', 'profile']

    def get_profile(self, obj):
        if hasattr(obj.user, 'employee') and obj.user.employee:
            return obj.user.employee.profile_picture.url if obj.user.employee.profile_picture else None
        return None

    def get_member_type(self, obj):
        if hasattr(obj.user, 'main_manager') and obj.user.main_manager:
            return "main_manager"
        elif hasattr(obj.user, 'employee') and obj.user.employee:
            return "employee"
        return "unknown"

    def get_full_name(self, obj):
        user = obj.user
        if hasattr(user, 'main_manager') and user.main_manager:
            return user.main_manager.name
        elif hasattr(user, 'employee') and user.employee:
            return f"{user.employee.first_name} {user.employee.last_name}"
        return "نامشخص"

class ChatRoomSerializer(serializers.ModelSerializer):
    members = MembershipSerializer(source='membership_set', many=True, read_only=True)
    owner_full_name = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            'id', 'name', 'display_name', 'type', 'owner',
            'owner_full_name', 'created_at', 'members', 'last_message'
        ]

    def get_owner_full_name(self, obj):
        owner = obj.owner
        if hasattr(owner, 'main_manager') and owner.main_manager:
            return owner.main_manager.name
        elif hasattr(owner, 'employee') and owner.employee:
            return f"{owner.employee.first_name} {owner.employee.last_name}"
        return "نامشخص"

    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return {
                "id": last_message.id,
                "sender": self.get_user_display_name(last_message.sender),
                "text": last_message.text[:20],
                "created_at": last_message.created_at
            }
        return None

    def get_display_name(self, obj):
        request = self.context.get('request')
        if not request:
            return obj.name

        current_user = request.user

        # اگر گروه یا کانال است، نام اصلی را برگردان
        if obj.type.lower() != 'pv':
            return obj.name

        # اگر پیوی است، نام عضو مقابل را برگردان
        other_members = CustomUser.objects.filter(
            memberships__chat_room=obj
        ).exclude(id=current_user.id)

        if other_members.exists():
            return self.get_user_display_name(other_members.first())
        else:
            # فقط مالک در چت هست → نام خودش
            return self.get_user_display_name(current_user)

    def get_user_display_name(self, user):
        if not user:
            return "نامشخص"
        if hasattr(user, 'main_manager') and user.main_manager:
            return user.main_manager.name
        elif hasattr(user, 'employee') and user.employee:
            return f"{user.employee.first_name} {user.employee.last_name}"
        return "نامشخص"


class ChatRoomCreateSerializer(serializers.ModelSerializer):
    member_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        help_text="List of Employee IDs to be added as members"
    )

    class Meta:
        model = ChatRoom
        fields = ['name', 'type', 'member_ids']

    def create(self, validated_data):
        member_ids = validated_data.pop('member_ids', [])
        request = self.context['request']
        owner = request.user

        if not hasattr(owner, 'main_manager'):
            raise ValidationError("Only Main Manager can create chat rooms.")

        # قوانین چک کردن

        # قانون 1: باید حداقل یک کارمند اضافه شود
        if len(member_ids) == 0:
            raise ValidationError("You must add at least one Employee to the chat.")

        # قانون 2: اگر نوع pv هست، فقط یک کارمند می‌توان اضافه کرد
        chat_type = validated_data.get('type', '').lower()
        if chat_type == 'pv' and len(member_ids) > 1:
            raise ValidationError("Private chat (pv) can have only one Employee member.")

        # ساخت چت
        chat_room = ChatRoom.objects.create(owner=owner, **validated_data)
        Membership.objects.create(user=owner, chat_room=chat_room, is_admin=True)

        employees = Employee.objects.filter(id__in=member_ids).select_related('user')

        for emp in employees:
            is_muted_flag = True if chat_type == 'channel' else False
            Membership.objects.create(user=emp.user, chat_room=chat_room, is_muted=is_muted_flag)

        # قانون 3: بعد از ساخت، چک کن تعداد اعضا به غیر از owner حداقل یک باشه
        member_count = chat_room.users.exclude(id=owner.id).count()
        if member_count == 0:
            chat_room.delete()
            raise ValidationError("Chat room must have at least one member besides the owner.")

        return chat_room


class ChatRoomUpdateSerializer(serializers.ModelSerializer):
    member_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True,
        help_text="List of Employee IDs to replace current members"
    )

    class Meta:
        model = ChatRoom
        fields = ['name', 'member_ids']

    def update(self, instance, validated_data):
        member_ids = validated_data.pop('member_ids', None)

        if 'name' in validated_data:
            instance.name = validated_data['name']

        if member_ids is not None:
            # حذف همه اعضا به جز owner
            Membership.objects.filter(chat_room=instance).exclude(user=instance.owner).delete()

            employees = Employee.objects.filter(id__in=member_ids).select_related('user')
            chat_type = instance.type.lower()

            for emp in employees:
                is_muted_flag = True if chat_type == 'channel' else False
                Membership.objects.create(user=emp.user, chat_room=instance, is_muted=is_muted_flag)

            # چک حداقل یک عضو غیر owner
            member_count = instance.users.exclude(id=instance.owner.id).count()
            if member_count == 0:
                raise serializers.ValidationError("Chat room must have at least one member besides the owner.")

        instance.save()
        return instance


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    sender_profile = serializers.SerializerMethodField()
    reply_to_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Message
        fields = [
            'id', 'room', 'sender', 'sender_name', 'sender_profile', 'text',
            'reply_to_id', 'created_at', 'is_edited', 'is_deleted'
        ]
        read_only_fields = ['sender', 'created_at', 'is_edited', 'is_deleted']

    def create(self, validated_data):
        """ست کردن sender به کاربر لاگین شده"""
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)

    def get_sender_profile(self, obj):
        if hasattr(obj.sender, 'employee') and obj.sender.employee:
            return obj.sender.employee.profile_picture
        elif hasattr(obj.sender, 'main_manager') and obj.sender.main_manager:
            return None
        return None


class MessageEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['text']

    def update(self, instance, validated_data):
        """ویرایش پیام و ست کردن is_edited=True"""
        instance.text = validated_data.get('text', instance.text)
        instance.is_edited = True
        instance.save()
        return instance
