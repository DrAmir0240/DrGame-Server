import django_filters

from psn.models import SonyAccount


class SonyAccountFilter(django_filters.FilterSet):
    status = django_filters.NumberFilter(field_name="status", lookup_expr="exact")
    region = django_filters.CharFilter(field_name="region", lookup_expr="exact")
    plus = django_filters.BooleanFilter(field_name="plus")
    bank_account_status = django_filters.BooleanFilter(field_name="bank_account_status")
    employee = django_filters.NumberFilter(field_name="employee", lookup_expr="exact")
    is_deleted = django_filters.BooleanFilter(field_name="is_deleted")

    class Meta:
        model = SonyAccount
        fields = [
            "status",
            "region",
            "plus",
            "bank_account_status",
            "employee",
            "is_deleted",
        ]


class SonyAccountPersonalFilter(django_filters.FilterSet):
    status = django_filters.NumberFilter(field_name="status__id")

    class Meta:
        model = SonyAccount
        fields = ["status"]


class HrSonyAccountFilter(django_filters.FilterSet):
    employee = django_filters.NumberFilter(field_name="employee__id")
    status = django_filters.NumberFilter(field_name="status__id")
    is_owned = django_filters.BooleanFilter(field_name="is_owned")

    class Meta:
        model = SonyAccount
        fields = ["employee", "status", "is_owned"]
