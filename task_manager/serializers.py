from rest_framework import serializers

from hr.models import EmployeeTask
from platform_settings.serializers import SoftDeleteSerializerMixin


class EmployeePersonalTaskSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = EmployeeTask
        fields = ['id', 'title', 'voice', 'type', 'description', 'status', 'deadline', 'employee', 'created_at',
                  'updated_at']
        read_only_fields = ['employee', 'type', 'created_at', 'updated_at', 'is_deleted']

    def create(self, validated_data):
        employee = self.context['request'].user.employee
        validated_data['employee'] = employee
        validated_data['type'] = 'Personal'
        return super().create(validated_data)


class EmployeeOrganizeTaskSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = EmployeeTask
        fields = [
            'id', 'title', 'voice', 'type', 'description', 'status', 'deadline', 'employee',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['type', 'created_at', 'updated_at', 'is_deleted']

    def create(self, validated_data):
        validated_data['type'] = 'Organize'
        return super().create(validated_data)

class EmployeeTaskStatsSerializer(serializers.Serializer):
    planed = serializers.IntegerField(read_only=True)
    in_progress = serializers.IntegerField(read_only=True)
    done = serializers.IntegerField(read_only=True)
    all = serializers.IntegerField(read_only=True)

