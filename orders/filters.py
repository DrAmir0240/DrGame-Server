"""
FilterSet classes for the orders workflow list endpoints.

هر نوع سفارش فیلتر جدا دارد. فیلدها بر اساس مدل واقعی هر سفارش تعریف شده‌اند:
- Sony: source, type, customer, بازه تاریخ
- Repair: customer, بازه تاریخ (مدل RepairOrder فیلد source/type ندارد)
- Product: customer, بازه تاریخ (مدل ProductOrder فیلد source/type/category ندارد)
"""

import django_filters

from orders.models import SonyAccountOrder, RepairOrder, ProductOrder


class SonyAccountOrderFilter(django_filters.FilterSet):
    source = django_filters.ChoiceFilter(choices=SonyAccountOrder.SOURCE_CHOICES)
    type = django_filters.ChoiceFilter(choices=SonyAccountOrder.TYPE_CHOICES)
    customer = django_filters.NumberFilter(field_name='customer__id')
    category = django_filters.NumberFilter(field_name='category__id')
    date_from = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    date_to = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte')

    class Meta:
        model = SonyAccountOrder
        fields = ['source', 'type', 'customer', 'category', 'date_from', 'date_to']


class RepairOrderFilter(django_filters.FilterSet):
    customer = django_filters.NumberFilter(field_name='customer__id')
    category = django_filters.NumberFilter(field_name='category__id')
    date_from = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    date_to = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte')

    class Meta:
        model = RepairOrder
        fields = ['customer', 'category', 'date_from', 'date_to']


class ProductOrderFilter(django_filters.FilterSet):
    customer = django_filters.NumberFilter(field_name='customer__id')
    date_from = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    date_to = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte')

    class Meta:
        model = ProductOrder
        fields = ['customer', 'date_from', 'date_to']
