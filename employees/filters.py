import django_filters

from employees.models import EmployeeTask, EmployeeRequest
from django_filters import rest_framework as filters

from payments.models import Transaction, GameOrder, RepairOrder
from storage.models import SonyAccount


class EmployeeTaskFilter(filters.FilterSet):
    type = filters.ChoiceFilter(choices=EmployeeTask._meta.get_field('type').choices)
    status = filters.ChoiceFilter(choices=EmployeeTask._meta.get_field('status').choices)
    deadline = filters.DateFilter(field_name='deadline', lookup_expr='exact')
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')

    class Meta:
        model = EmployeeTask
        fields = ['type', 'status', 'deadline', 'title']


class EmployeeRequestFilter(filters.FilterSet):
    request_type = filters.ChoiceFilter(choices=EmployeeRequest._meta.get_field('request_type').choices)
    employee = filters.NumberFilter(field_name='employee__id')

    class Meta:
        model = EmployeeRequest
        fields = ['employee', 'request_type']


class GameOrderFilter(django_filters.FilterSet):
    order_type = django_filters.CharFilter(field_name='order_type', lookup_expr='exact')
    order_console_type = django_filters.CharFilter(field_name='order_console_type', lookup_expr='exact')
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
    payment_status = django_filters.CharFilter(field_name='payment_status', lookup_expr='exact')

    class Meta:
        model = GameOrder
        fields = ['order_type', 'order_console_type', 'status', 'payment_status']


class RepairOrderFilter(django_filters.FilterSet):
    order_type = django_filters.CharFilter(field_name='order_type', lookup_expr='exact')
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')

    class Meta:
        model = RepairOrder
        fields = ['order_type', 'status']


class TransactionFilter(filters.FilterSet):
    payer = filters.NumberFilter(field_name='payer__id')
    payer_str = filters.CharFilter(field_name='payer_str', lookup_expr='icontains')
    receiver = filters.NumberFilter(field_name='receiver__id')
    receiver_str = filters.CharFilter(field_name='receiver_str', lookup_expr='icontains')
    payment_method = filters.NumberFilter(field_name='payment_method__id')
    in_out = filters.BooleanFilter(field_name='in_out')
    order_type = filters.CharFilter(method='filter_by_order_type')

    created_at_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at_before = filters.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Transaction
        fields = [
            'payer', 'payer_str',
            'receiver', 'receiver_str',
            'payment_method', 'in_out',
            'created_at_after', 'created_at_before'
        ]

    def filter_by_order_type(self, queryset, name, value):
        if value == 'game':
            return queryset.filter(game_order__isnull=False)
        elif value == 'repair':
            return queryset.filter(repair_order__isnull=False)
        elif value == 'course':
            return queryset.filter(course_order__isnull=False)
        elif value == 'normal':
            return queryset.filter(order__isnull=False)
        return queryset


class SonyAccountFilter(filters.FilterSet):
    employee = filters.NumberFilter(field_name='employee__id')
    status = filters.NumberFilter(field_name='status__id')
    is_owned = filters.BooleanFilter(field_name='is_owned')

    class Meta:
        model = SonyAccount
        fields = ['employee', 'status', 'is_owned']


class SonyAccountPersonalFilter(filters.FilterSet):
    status = filters.NumberFilter(field_name='status__id')

    class Meta:
        model = SonyAccount
        fields = ['status']
