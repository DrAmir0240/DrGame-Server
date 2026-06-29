from rest_framework import serializers

from hr.models import Employee
from hr.serializers import EmployeeSerializer
from task_manager.models import PlannedTask, DailyTask


class TaskStatsSerializer(serializers.Serializer):
    not_started = serializers.IntegerField()
    in_progress = serializers.IntegerField()
    done = serializers.IntegerField()
    expired = serializers.IntegerField()


class TaskManagerPermissionSerializer(serializers.Serializer):
    can_read_task_manager = serializers.BooleanField()
    can_write_task_manager = serializers.BooleanField()


class TaskManagerDashboardSerializer(serializers.Serializer):
    permissions = TaskManagerPermissionSerializer()
    my_tasks = TaskStatsSerializer()
    all_tasks = TaskStatsSerializer(allow_null=True)


class TaskChoicesSerializer(serializers.Serializer):
    """سریالایزر برای انتخابات و فیلدهای وابسته تسک"""
    employees = serializers.SerializerMethodField()
    status_choices = serializers.SerializerMethodField()
    priority_choices = serializers.SerializerMethodField()
    type_choices = serializers.SerializerMethodField()

    # noinspection PyMethodMayBeStatic
    def get_employees(self, _obj):
        return [
            {"id": emp.id, "title": str(emp)}
            for emp in Employee.objects.filter(is_deleted=False)
        ]

    # noinspection PyMethodMayBeStatic
    def get_status_choices(self, _obj):
        return [{"value": k, "label": v} for k, v in PlannedTask._meta.get_field("status").choices]

    # noinspection PyMethodMayBeStatic
    def get_priority_choices(self, _obj):
        return [{"value": k, "label": v} for k, v in PlannedTask._meta.get_field("priority").choices]

    # noinspection PyMethodMayBeStatic
    def get_type_choices(self, _obj):
        return [{"value": k, "label": v} for k, v in PlannedTask._meta.get_field("type").choices]


class PlannedTaskListSerializer(serializers.ModelSerializer):
    """سریالایزر سبک برای لیست تسک‌ها"""
    employee_name = serializers.CharField(source="employee.__str__", read_only=True)

    class Meta:
        model = PlannedTask
        fields = [
            "id", "employee", "employee_name", "title", "type",
            "status", "priority", "has_reward", "reward_amount",
            "approved", "start_date", "deadline", "created_at",
        ]


class PlannedTaskDetailSerializer(serializers.ModelSerializer):
    """سریالایزر کامل برای جزئیات / ایجاد / ویرایش تسک"""
    employee_name = serializers.CharField(source="employee.__str__", read_only=True)

    class Meta:
        model = PlannedTask
        fields = [
            "id", "employee", "employee_name", "title", "voice", "type",
            "description", "status", "priority", "has_reward",
            "reward_amount", "approved", "start_date", "deadline",
            "is_deleted", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "approved", "is_deleted", "created_at", "updated_at"]


class PersonalTaskCreateSerializer(serializers.ModelSerializer):
    """سریالایزر ایجاد/ویرایش تسک شخصی — employee از request.user گرفته می‌شود"""

    class Meta:
        model = PlannedTask
        fields = [
            "id", "title", "voice", "description", "status",
            "priority", "start_date", "deadline",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        employee = self.context["request"].user.employee
        return PlannedTask.objects.create(
            **validated_data,
            employee=employee,
            type="Personal",
        )

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class OrganizeTaskCreateSerializer(serializers.ModelSerializer):
    """سریالایزر ایجاد تسک سازمانی توسط مدیر"""

    class Meta:
        model = PlannedTask
        fields = [
            "id", "employee", "title", "voice", "description",
            "status", "priority", "has_reward", "reward_amount",
            "start_date", "deadline",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        return PlannedTask.objects.create(**validated_data, type="Organize")


class PendingApprovalSerializer(serializers.ModelSerializer):
    """سریالایزر تسک‌های منتظر تأیید (پاداش‌دار و انجام‌شده)"""
    employee_name = serializers.CharField(source="employee.__str__", read_only=True)

    class Meta:
        model = PlannedTask
        fields = [
            "id", "employee", "employee_name", "title", "type",
            "priority", "has_reward", "reward_amount", "approved",
            "start_date", "deadline", "created_at",
        ]
        read_only_fields = fields


class ApproveRejectSerializer(serializers.Serializer):
    """بدنه درخواست تأیید یا رد تسک (برای نمایش در سواگر)"""
    task_id = serializers.IntegerField(help_text="شناسه تسک")


class TaskSearchSerializer(serializers.ModelSerializer):
    """سریالایزر نتایج جستجو"""
    employee_name = serializers.CharField(source="employee.__str__", read_only=True)

    class Meta:
        model = PlannedTask
        fields = [
            "id", "employee", "employee_name", "title", "type",
            "status", "priority", "start_date", "deadline",
        ]


class DailyTaskSearchSerializer(serializers.ModelSerializer):
    employee_names = serializers.SerializerMethodField()
    employees = EmployeeSerializer(many=True, read_only=True)

    class Meta:
        model = DailyTask
        fields = [
            "id", "employees", "employee_names", "title", "type",
            "created_at",
        ]

    # noinspection PyMethodMayBeStatic
    def get_employee_names(self, obj):
        return [str(emp) for emp in obj.employees.all()]


class DailyTaskListSerializer(serializers.ModelSerializer):
    employee_names = serializers.SerializerMethodField()
    employees = EmployeeSerializer(many=True, read_only=True)

    class Meta:
        model = DailyTask
        fields = (
            "id",
            "employees",
            "employee_names",
            "title",
            "type",
            "created_at",
        )

    # noinspection PyMethodMayBeStatic
    def get_employee_names(self, obj):
        return [str(emp) for emp in obj.employees.all()]


class PersonalDailyTaskSerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.filter(is_deleted=False),
        write_only=True,
    )

    class Meta:
        model = DailyTask
        fields = (
            "id",
            "employee",
            "title",
            "description",
        )
        read_only_fields = ("id",)

    def create(self, validated_data):
        employee = validated_data.pop("employee")
        task = DailyTask.objects.create(
            type="Personal",
            **validated_data,
        )
        task.employees.add(employee)
        return task


class OrganizeDailyTaskSerializer(serializers.ModelSerializer):
    employees = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.filter(is_deleted=False),
        many=True,
    )

    class Meta:
        model = DailyTask
        fields = (
            "id",
            "employees",
            "title",
            "description",
        )
        read_only_fields = ("id",)

    def create(self, validated_data):
        employees = validated_data.pop("employees")
        task = DailyTask.objects.create(
            type="Organize",
            **validated_data,
        )
        task.employees.set(employees)  # noqa: PyUnresolvedReferences
        return task
