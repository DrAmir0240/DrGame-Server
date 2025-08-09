from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError
from employees.models import Employee
from .models import ChatRoom, Membership, Message
from accounts.models import MainManager
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class MembershipSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    member_type = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = ['user', 'is_admin', 'is_muted', 'joined_at', 'member_type', 'full_name']

    def get_member_type(self, obj):
        if hasattr(obj.user, 'main_manager'):
            return "main_manager"
        elif hasattr(obj.user, 'employee'):
            return "employee"
        return "unknown"

    def get_full_name(self, obj):
        user = obj.user
        # اگر user مربوط به mainmanager بود
        if hasattr(user, 'main_manager'):
            return f"{user.main_manager.name}"
        elif hasattr(user, 'employee'):
            return f"{user.employee.first_name} {user.employee.last_name}"
        return user.username  # fallback به username یا هر چیز دیگه


class ChatRoomSerializer(serializers.ModelSerializer):
    members = MembershipSerializer(source='membership_set', many=True, read_only=True)
    owner_full_name = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()  # نام نمایشی چت

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'display_name', 'type', 'owner', 'owner_full_name', 'created_at', 'members']

    def get_owner_full_name(self, obj):
        user = obj.owner
        if hasattr(user, 'main_manager'):
            return f"{user.mainmanager.name}"
        elif hasattr(user, 'employee'):
            return f"{user.employee.first_name} {user.employee.last_name}"
        return user.username

    def get_display_name(self, obj):
        request = self.context.get('request')
        if not request:
            return obj.name  # fallback

        current_user = request.user

        if obj.type.lower() != 'pv':
            # اگر پیوی نیست، همون نام اصلی رو برگردون
            return obj.name

        # اگر پیوی هست، اسم بر اساس مالک یا عضو مقابل تعیین میشه
        members = obj.users.exclude(id=current_user.id)
        if members.exists():
            # فرض کنیم فقط یک عضو دیگه هست (چون pv)
            other_user = members.first()

            if hasattr(other_user, 'mainmanager'):
                return f"{other_user.mainmanager.first_name} {other_user.mainmanager.last_name}"
            elif hasattr(other_user, 'employee'):
                return f"{other_user.employee.first_name} {other_user.employee.last_name}"
            else:
                return other_user.username
        else:
            # اگر فقط مالک هست، اسم خود مالک رو برگردون
            if hasattr(current_user, 'mainmanager'):
                return f"{current_user.mainmanager.first_name} {current_user.mainmanager.last_name}"
            elif hasattr(current_user, 'employee'):
                return f"{current_user.employee.first_name} {current_user.employee.last_name}"
            else:
                return current_user.username


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
                if emp.user.type and emp.user.type.lower() != 'none':
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
    reply_to_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Message
        fields = [
            'id', 'room', 'sender', 'sender_name', 'text',
            'reply_to_id', 'created_at', 'is_edited', 'is_deleted'
        ]
        read_only_fields = ['sender', 'created_at', 'is_edited', 'is_deleted']

    def create(self, validated_data):
        """ست کردن sender به کاربر لاگین شده"""
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


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
