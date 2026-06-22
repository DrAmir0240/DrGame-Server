from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters
from rest_framework.response import Response

from hr.filters import EmployeeTaskFilter
from hr.models import EmployeeTask, Employee
from hr.serializers import EmployeeSerializer
from hr.views import EmployeeOrganizeTaskPagination
from task_manager.serializers import EmployeePersonalTaskSerializer, EmployeeOrganizeTaskSerializer
from users.auth import CustomJWTAuthentication
from users.permissions import IsEmployee, IsMainManager


# Create your views here.

# -------------------- tasks --------------------
class EmployeePanelTaskList(
    generics.ListAPIView):
    serializer_class = EmployeePersonalTaskSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]
    pagination_class = EmployeeOrganizeTaskPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = EmployeeTaskFilter
    ordering_fields = ['deadline', 'created_at']
    search_fields = ['title', 'description']

    def get_queryset(self):
        user = self.request.user
        try:
            employee = user.employee
            return EmployeeTask.objects.filter(employee=employee, is_deleted=False)
        except AttributeError:
            return Response(status=404)


class EmployeePanelTaskDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeePersonalTaskSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        user = self.request.user
        try:
            employee = user.employee
            return EmployeeTask.objects.filter(employee=employee)
        except AttributeError:
            return Response(status=404)


class EmployeePanelAddTask(generics.CreateAPIView):
    serializer_class = EmployeePersonalTaskSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        user = self.request.user
        try:
            employee = user.employee
            return EmployeeTask.objects.filter(employee=employee)
        except AttributeError:
            return Response(status=404)




# ==================== TaskManager Views ====================
class EmployeePanelOrganizeTaskListCreateView(generics.ListCreateAPIView):
    queryset = EmployeeTask.objects.filter(type='Organize')
    serializer_class = EmployeeOrganizeTaskSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    pagination_class = EmployeeOrganizeTaskPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EmployeeTaskFilter
    ordering_fields = ['created_at', 'dead_line']


class EmployeePanelOrganizeTaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EmployeeTask.objects.filter(type='Organize')
    serializer_class = EmployeeOrganizeTaskSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class EmployeePanelOrganizeTaskChoices(generics.ListAPIView):
    queryset = Employee.objects.filter(is_deleted=False)
    serializer_class = EmployeeSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

