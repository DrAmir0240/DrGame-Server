import django_filters

from task_manager.models import PlannedTask, DailyTask


class PlannedTaskFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    priority = django_filters.CharFilter(field_name="priority", lookup_expr="iexact")
    type = django_filters.CharFilter(field_name="type", lookup_expr="iexact")
    employee_id = django_filters.NumberFilter(field_name="employee__id")

    class Meta:
        model = PlannedTask
        fields = ["status", "priority", "type", "employee_id"]


class DailyTaskFilter(django_filters.FilterSet):
    employee = django_filters.NumberFilter(field_name="employee")
    type = django_filters.CharFilter(field_name="type")

    class Meta:
        model = DailyTask
        fields = (
            "employee",
            "type",
        )
