from logging import lastResort

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from employees.models import Employee
from .models import ChatRoom, Membership, Message
from django.contrib.auth import get_user_model

User = get_user_model()


def user_display_name(user: User) -> str:
    """
    نام نمایشی کاربر بر اساس موجودیت‌های مرتبط.
    اگر main_manager دارد => name
    اگر employee دارد => first_name + last_name
    در غیر این صورت: username یا 'نامشخص'
    """
    if not user:
        return 'نامشخص'
    # getattr ایمن‌تر از hasattr برای دسترسی OneToOne
    mm = getattr(user, 'main_manager', None)
    if mm:
        return mm.name or 'نامشخص'
    emp = getattr(user, 'employee', None)
    if emp:
        full = f'{emp.first_name or ""} {emp.last_name or ""}'.strip()
        return full or (user or 'نامشخص')
    return 'نامشخص'


def employee_profile_url(user: User):
    """
    اگر کاربر employee دارد و عکس پروفایل دارد، URL بده.
    """
    emp = getattr(user, 'employee', None)
    if emp and getattr(emp, 'profile_picture', None):
        try:
            return emp.profile_picture.url
        except Exception:
            return None
    return None


class MembershipSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    member_type = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = ['user', 'is_admin', 'is_muted', 'joined_at', 'member_type', 'full_name', 'profile']
        read_only_fields = ['joined_at']

    def get_profile(self, obj: Membership):
        return employee_profile_url(obj.user)

    def get_member_type(self, obj: Membership):
        if getattr(obj.user, 'main_manager', None):
            return "main_manager"
        if getattr(obj.user, 'employee', None):
            return "employee"
        return "unknown"

    def get_full_name(self, obj: Membership):
        return user_display_name(obj.user)


class LastMessageSerializer(serializers.Serializer):
    # خروجی خلاصه‌ی آخرین پیام
    id = serializers.IntegerField()
    sender = serializers.CharField()
    text = serializers.CharField(allow_blank=True, allow_null=True)
    created_at = serializers.DateTimeField()


class ChatRoomSerializer(serializers.ModelSerializer):
    # توجه: related_name در مدل Membership برای chat_room => 'memberships' است.
    members = MembershipSerializer(source='memberships', many=True, read_only=True)
    owner_full_name = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            'id', 'name', 'display_name', 'type', 'owner',
            'owner_full_name', 'created_at', 'members', 'last_message'
        ]
        read_only_fields = ['owner', 'created_at']

    def get_owner_full_name(self, obj: ChatRoom):
        return user_display_name(obj.owner)

    def get_last_message(self, obj: ChatRoom):
        # به‌دلیل ordering=['-created_at']، آخرین پیام در QuerySet => first()
        msg = obj.messages.first()
        if not msg:
            return None
        return LastMessageSerializer({
            "id": msg.id,
            "sender": user_display_name(msg.sender),
            "text": (msg.text or '')[:200],  # امن در برابر None
            "created_at": msg.created_at,
        }).data

    def get_display_name(self, obj: ChatRoom):
        """
        برای pv نام «طرف مقابل» را نشان بده؛
        برای group/channel همان name را برگردان.
        """
        request = self.context.get('request')
        if not request:
            # اگر کانتکست نداریم، fallback
            return obj.name

        if not obj.is_private:
            return obj.name

        current_user = request.user
        # همه‌ی اعضا به جز خود کاربر
        other_members = obj.users.exclude(id=current_user.id)
        if other_members.exists():
            return user_display_name(other_members.first())
        # اگر تنها عضو مالک است:
        return user_display_name(current_user)


class ChatRoomCreateSerializer(serializers.ModelSerializer):
    member_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        write_only=True,
        help_text="لیست ID های Employee برای افزودن به چت"
    )

    class Meta:
        model = ChatRoom
        fields = ['name', 'type', 'member_ids']

    def validate(self, attrs):
        request = self.context['request']
        owner = request.user

        # فقط MainManager اجازه ساخت دارد (حتی اگر در permission هم چک شود، اینجا هم محافظت نرم می‌کنیم)
        if not getattr(owner, 'main_manager', None):
            raise serializers.ValidationError("Only Main Manager can create chat rooms.")

        chat_type = (attrs.get('type') or '').lower()
        if chat_type not in {ChatRoom.PV, ChatRoom.GROUP, ChatRoom.CHANNEL}:
            raise serializers.ValidationError("Invalid chat type.")

        member_ids = attrs.get('member_ids') or []
        # قانون 1: حداقل یک عضو
        if len(member_ids) == 0:
            raise serializers.ValidationError("You must add at least one Employee to the chat.")

        # یکتا کردن لیست برای جلوگیری از ارور unique_together
        attrs['member_ids'] = list(dict.fromkeys(member_ids))

        # قانون 2: pv فقط یک عضو
        if chat_type == ChatRoom.PV and len(attrs['member_ids']) != 1:
            raise serializers.ValidationError("Private chat (pv) must have exactly one Employee.")

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        member_ids = validated_data.pop('member_ids', [])
        request = self.context['request']
        owner = request.user

        chat_room = ChatRoom.objects.create(owner=owner, **validated_data)
        # مالک همیشه عضو و ادمین است
        Membership.objects.create(user=owner, chat_room=chat_room, is_admin=True, is_muted=False)

        # کارمندان مورد نظر را (با select_related برای کارایی) بیاور
        employees = Employee.objects.filter(id__in=member_ids).select_related('user')

        # اگر تعداد واقعی پیدا شده کمتر از درخواست بود، ID نامعتبر داریم
        if employees.count() != len(member_ids):
            raise serializers.ValidationError("One or more Employee IDs are invalid.")

        is_channel = chat_room.is_channel

        for emp in employees:
            # در channel اعضا به‌صورت پیش‌فرض mute می‌شوند
            Membership.objects.create(
                user=emp.user,
                chat_room=chat_room,
                is_muted=is_channel
            )

        # قانون 3: حداقل یک عضو غیر از owner
        non_owner_count = chat_room.users.exclude(id=owner.id).count()
        if non_owner_count == 0:
            raise serializers.ValidationError("Chat room must have at least one member besides the owner.")

        return chat_room


class ChatRoomUpdateSerializer(serializers.ModelSerializer):
    member_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        write_only=True,
        help_text="اگر بیاید، اعضای فعلی (غیر از owner) با این لیست جایگزین می‌شوند."
    )

    class Meta:
        model = ChatRoom
        fields = ['name', 'member_ids']

    @transaction.atomic
    def update(self, instance: ChatRoom, validated_data):
        request = self.context['request']
        user = request.user

        # فقط مالک اجازه‌ی ویرایش اعضا/نام را دارد
        if instance.owner_id != user.id:
            raise serializers.ValidationError("Only the owner can update the chat room.")

        member_ids = validated_data.pop('member_ids', None)

        if 'name' in validated_data:
            instance.name = (validated_data['name'] or '').strip()

        if member_ids is not None:
            # یکتا
            member_ids = list(dict.fromkeys(member_ids))
            # حذف همه‌ی اعضا به جز owner
            Membership.objects.filter(chat_room=instance).exclude(user=instance.owner).delete()

            employees = Employee.objects.filter(id__in=member_ids).select_related('user')
            if employees.count() != len(member_ids):
                raise serializers.ValidationError("One or more Employee IDs are invalid.")

            is_channel = instance.is_channel
            for emp in employees:
                Membership.objects.create(
                    user=emp.user,
                    chat_room=instance,
                    is_muted=is_channel
                )

            # چک حداقل یک عضو غیر owner
            member_count = instance.users.exclude(id=instance.owner_id).count()
            if member_count == 0:
                raise serializers.ValidationError("Chat room must have at least one member besides the owner.")

        instance.save()
        return instance


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    sender_profile = serializers.SerializerMethodField()
    # ورودی ساده برای reply: فقط id می‌گیریم
    reply_to_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'room', 'sender', 'sender_name', 'sender_profile', 'text',
            'reply_to_id', 'created_at', 'is_edited', 'is_deleted'
        ]
        read_only_fields = ['sender', 'created_at', 'is_edited', 'is_deleted']

    def get_sender_profile(self, obj: Message):
        return employee_profile_url(obj.sender)

    def get_sender_name(self, obj: Message):
        return user_display_name(obj.sender)

    def validate(self, attrs):
        """
        - مطمئن می‌شویم کاربر جاری عضو روم است.
        - اگر reply_to_id داشت، پیام هدف در همان روم باشد.
        """
        request = self.context['request']
        user = request.user

        room = attrs.get('room')  # به‌عنوان PrimaryKeyRelatedField می‌آید
        if not room:
            raise serializers.ValidationError("Room is required.")

        # عضو بودن کاربر
        if not room.users.filter(id=user.id).exists():
            raise serializers.ValidationError("You are not a member of this chat.")

        reply_to_id = self.initial_data.get('reply_to_id', None)
        if reply_to_id:
            try:
                reply_msg = Message.objects.get(pk=reply_to_id)
            except Message.DoesNotExist:
                raise serializers.ValidationError("reply_to message not found.")
            if reply_msg.room_id != room.id:
                raise serializers.ValidationError("reply_to message must be in the same room.")
            # ذخیره برای create
            attrs['reply_to'] = reply_msg

        return attrs

    def create(self, validated_data):
        """
        - sender را کاربر لاگین می‌گذاریم.
        - اگر reply_to در validate پر شده بود، استفاده می‌کنیم.
        """
        user = self.context['request'].user
        validated_data['sender'] = user
        # reply_to را اگر validate تنظیم کرده بودیم، همینجا بماند
        validated_data.pop('reply_to_id', None)  # اگر به هر دلیل در attrs مانده
        return super().create(validated_data)


class MessageEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['text']

    def update(self, instance: Message, validated_data):
        """
        ویرایش متن + ست کردن is_edited=True
        """
        instance.text = validated_data.get('text', instance.text)
        instance.is_edited = True
        instance.save()
        return instance
