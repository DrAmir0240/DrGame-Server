from rest_framework import serializers


class TaskStatsSerializer(serializers.Serializer):
    not_started = serializers.IntegerField()
    in_progress = serializers.IntegerField()
    done = serializers.IntegerField()
    expired = serializers.IntegerField()


class TaskManagerPermissionSerializer(serializers.Serializer):
    can_read_task_manger = serializers.BooleanField()
    can_write_task_manger = serializers.BooleanField()


class TaskManagerDashboardSerializer(serializers.Serializer):
    permissions = TaskManagerPermissionSerializer()
    my_tasks = TaskStatsSerializer()
    all_tasks = TaskStatsSerializer(allow_null=True)
