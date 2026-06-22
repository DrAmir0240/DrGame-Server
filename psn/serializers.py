from rest_framework import serializers

from inventory.models import SonyAccountBank, SonyAccountStatus, SonyAccount, SonyAccountGame
from platform_settings.serializers import SoftDeleteSerializerMixin


class EmployeeSonyAccountBankSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = SonyAccountBank
        fields = "__all__"


class EmployeeSonyAccountStatusSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = SonyAccountStatus
        fields = "__all__"


class EmployeeSonyAccountSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    games = serializers.SlugRelatedField(many=True, read_only=True, slug_field='title')
    status_title = serializers.SerializerMethodField()
    game_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = SonyAccount
        fields = "__all__"
        read_only_fields = ['is_deleted', 'created_at', 'updated_at']

    def get_employee_name(self, obj):
        if obj.employee:
            return f"{obj.employee.first_name} {obj.employee.last_name}"
        return None

    def get_status_title(self, obj):
        if obj.status:
            return obj.status.title
        return None

    def update(self, instance, validated_data):
        game_ids = validated_data.pop("game_ids", None)

        # آپدیت فیلدهای معمولی
        instance = super().update(instance, validated_data)

        if game_ids is not None:
            from django.db import transaction
            with transaction.atomic():
                # همه‌ی بازی‌های قبلی این اکانت پاک میشن
                SonyAccountGame.objects.filter(sony_account=instance).delete()

                # بازی‌های جدید ست میشن
                for game_id in game_ids:
                    SonyAccountGame.objects.create(
                        sony_account=instance,
                        game_id=game_id
                    )

        return instance



class SonyAccountSearchSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = SonyAccount
        fields = ['id', 'username', 'region', 'type']

    def get_type(self, obj):
        return "sony_account"
