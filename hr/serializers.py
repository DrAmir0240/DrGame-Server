from rest_framework import serializers
from hr.models import Permission, EmployeeRole


class PermissionSerializer(serializers.ModelSerializer):
    module_display = serializers.CharField(source='get_module_display', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = Permission
        fields = ['id', 'module', 'module_display', 'action', 'action_display', 'extra_flag']


class MyPermissionsSerializer(serializers.Serializer):
    """فرمت flat برای فرانت"""
    permissions = serializers.DictField()





class EmployeeRoleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeRole
        fields = ['id', 'role_name', 'description']


class EmployeeRoleDetailSerializer(serializers.ModelSerializer):
    permissions_detail = PermissionSerializer(source='permissions', many=True, read_only=True)
    permissions        = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(), many=True, write_only=True
    )

    class Meta:
        model = EmployeeRole
        fields = [
            'id', 'role_name', 'description',
            'permissions', 'permissions_detail',
            'created_at', 'updated_at'
        ]