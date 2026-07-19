import django_filters
from django_filters import rest_framework as filters

from task_manager.models import PlannedTask
from hr.models import (
    EmployeeRequest,
    Employee,
    EmployeeOvertime,
    EmployeeArrival,
)


class EmployeeTaskFilter(filters.FilterSet):
    type = filters.ChoiceFilter(choices=PlannedTask._meta.get_field('type').choices)
    status = filters.ChoiceFilter(choices=PlannedTask._meta.get_field('status').choices)
    deadline = filters.DateFilter(field_name='deadline', lookup_expr='exact')
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')

    class Meta:
        model = PlannedTask
        fields = ['type', 'status', 'deadline', 'title']


class EmployeeRequestFilter(filters.FilterSet):
    employee = django_filters.NumberFilter(field_name='employee__id')
    status = django_filters.ChoiceFilter(choices=EmployeeRequest._meta.get_field('status').choices)
    request_type = django_filters.NumberFilter(field_name='request_type__id')

    class Meta:
        model = EmployeeRequest
        fields = ['employee', 'status', 'request_type']


class EmployeeFilter(django_filters.FilterSet):
    role = django_filters.NumberFilter(field_name='roles__id')
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    national_code = django_filters.CharFilter(lookup_expr='exact')
    employee_id = django_filters.CharFilter(lookup_expr='exact')

    class Meta:
        model = Employee
        fields = ['role', 'first_name', 'last_name', 'national_code', 'employee_id']


class EmployeeOvertimeFilter(django_filters.FilterSet):
    employee = django_filters.NumberFilter(field_name='employee__id')
    date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    is_approved = django_filters.BooleanFilter()

    class Meta:
        model = EmployeeOvertime
        fields = ['employee', 'date_from', 'date_to', 'is_approved']


class EmployeeArrivalFilter(django_filters.FilterSet):
    employee = django_filters.NumberFilter(field_name='employee__id')
    date_from = django_filters.DateFilter(field_name='check_in', lookup_expr='date__gte')
    date_to = django_filters.DateFilter(field_name='check_in', lookup_expr='date__lte')

    class Meta:
        model = EmployeeArrival
        fields = ['employee', 'date_from', 'date_to']