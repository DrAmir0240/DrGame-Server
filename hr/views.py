from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from hr.models import Permission, EmployeeRole
from hr.permissions import employee_permission
from hr.serializers import PermissionSerializer, EmployeeRoleDetailSerializer, EmployeeRoleListSerializer
from hr.services.permission_service import get_employee_permissions


@extend_schema(tags=['HR — Permissions'])
class PermissionListView(generics.ListAPIView):
    """لیست تمام پرمیژن‌های تعریف‌شده در سیستم — فقط مدیر"""
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, employee_permission('hr', 'read')]
    queryset = Permission.objects.all().order_by('module', 'action')


@extend_schema(tags=['HR — Permissions'])
class MyPermissionsView(generics.GenericAPIView):
    """
    فرانت موقع لاگین این رو صدا میزنه
    GET /hr/my-permissions/
    """
    permission_classes = [IsAuthenticated]

    def get(self):
        if hasattr(self.request.user, 'employee'):
            perms = get_employee_permissions(self.request.user.employee)
            return Response(perms)
        return Response({})


class BaseRoleView:
    permission_classes = [IsAuthenticated, employee_permission('hr', 'read')]
    queryset = EmployeeRole.objects.filter(is_deleted=False).order_by('-created_at')


@extend_schema(tags=['HR — Roles'])
class EmployeeRoleListView(BaseRoleView, generics.ListAPIView):
    serializer_class = EmployeeRoleListSerializer


@extend_schema(tags=['HR — Roles'])
class EmployeeRoleCreateView(generics.CreateAPIView):
    serializer_class = EmployeeRoleDetailSerializer
    permission_classes = [IsAuthenticated, employee_permission('hr', 'write')]
    queryset = EmployeeRole.objects.filter(is_deleted=False)


@extend_schema(tags=['HR — Roles'])
class EmployeeRoleDetailView(BaseRoleView, generics.RetrieveAPIView):
    serializer_class = EmployeeRoleDetailSerializer


@extend_schema(tags=['HR — Roles'])
class EmployeeRoleUpdateView(generics.UpdateAPIView):
    serializer_class = EmployeeRoleDetailSerializer
    permission_classes = [IsAuthenticated, employee_permission('hr', 'write')]
    queryset = EmployeeRole.objects.filter(is_deleted=False)
    http_method_names = ['patch']


@extend_schema(tags=['HR — Roles'])
class EmployeeRoleDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, employee_permission('hr', 'write')]
    queryset = EmployeeRole.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])
