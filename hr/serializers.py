from rest_framework import serializers

from accounting.models import Transaction, RepairOrder
from accounting.serializers import DeliveryManSerializer
from hr.models import Employee, Repairman, EmployeeFile, EmployeeRequest, EmployeeHire
from platform_settings.serializers import SoftDeleteSerializerMixin
from users.models import CustomUser


class EmployeeFileSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = EmployeeFile
        exclude = ["employee"]


class EmployeeSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='phone',
        queryset=CustomUser.objects.all()
    )
    files = EmployeeFileSerializer(many=True, required=False)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = "__all__"

    def get_full_name(self, obj):
        return obj.first_name + " " + obj.last_name

    def create(self, validated_data):
        files_data = validated_data.pop('files', [])
        validated_data.pop('file_ids_to_delete', None)  # برای اطمینان

        employee = Employee.objects.create(**validated_data)

        for file_data in files_data:
            EmployeeFile.objects.create(employee=employee, **file_data)

        return employee

    def update(self, instance, validated_data):
        files_data = validated_data.pop('files', None)
        file_ids_to_delete = validated_data.pop('file_ids_to_delete', [])

        # آپدیت فیلدهای خود Employee
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # اضافه کردن فایل‌های جدید
        if files_data:
            for file_data in files_data:
                EmployeeFile.objects.create(employee=instance, **file_data)

        # حذف فایل‌ها
        if file_ids_to_delete:
            EmployeeFile.objects.filter(id__in=file_ids_to_delete, employee=instance).delete()

        return instance


class EmployeeHireSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeHire
        fields = "__all__"
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


class SendSmsToEmployeeSerializer(serializers.Serializer):
    message = serializers.CharField()
    employee_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False
    )
    send_time = serializers.DateTimeField(required=False)


class RepairmanSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='phone',
        queryset=CustomUser.objects.all()
    )

    class Meta:
        model = Repairman
        fields = "__all__"


class RepairManRepairOrderSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    order_type = serializers.SlugRelatedField(slug_field='title', read_only=True)
    delivery_to_drgame = DeliveryManSerializer(read_only=True)
    delivery_to_customer = DeliveryManSerializer(read_only=True)

    class Meta:
        model = RepairOrder
        fields = "__all__"
        read_only_fields = ['is_deleted', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        request = self.context.get("request")
        user = request.user

        new_status = validated_data.get("status", instance.status)

        # شرط 1: اگه سفارش تو صف پذیرش باشه و تعمیرکار بخواد آپدیتش کنه → ست بشه روی repair_man
        if instance.status == "in_accepting_queue" and new_status == "waiting_for_repairman_fee":
            instance.repair_man = user.repairman

        # شرط 2: اگه وضعیت از waiting_for_repairman_fee → waiting_for_amount تغییر کنه
        if instance.status == "waiting_for_repairman_fee" and new_status == "waiting_for_amount":
            repairman_fee = validated_data.get("repairman_fee")
            if not repairman_fee:
                raise serializers.ValidationError({
                    "repairman_fee": "برای تغییر وضعیت به 'waiting_for_amount' باید مبلغ تعمیرکار را وارد کنید."
                })
        # شرط 3: اگه وضعیت از waiting_for_amount → waiting_for_customer_to_accept تغییر کنه
        if instance.status == "waiting_for_amount" and new_status == "waiting_for_customer_to_accept":
            amount = validated_data.get("amount")
            if not amount:
                raise serializers.ValidationError({
                    "amount": "برای تغییر وضعیت به 'waiting_for_amount' باید مبلغ تعمیرکار را وارد کنید."
                })
        # شرط 4: اگه وضعیت شد in_progress → کم کردن مبلغ از موجودی مشتری
        if new_status == "in_progress" and instance.status != "in_progress":
            amount = instance.amount or validated_data.get("amount")
            customer = instance.customer

            if not amount:
                raise serializers.ValidationError({
                    "amount": "برای شروع سفارش باید مبلغ مشخص شده باشد."
                })
            customer.balance -= amount
            customer.save()

        if "amount" in validated_data:
            new_amount = validated_data.get("amount")
            if instance.amount != new_amount and instance.amount != 0:
                customer = instance.customer
                if instance.amount:
                    customer.balance += instance.amount

                customer.wallet_balance -= new_amount
                customer.save()

        if new_status == 'done' and instance.status == 'in_progress':
            instance.repair_man.balance += instance.repairman_fee
            instance.repair_man.save()

        return super().update(instance, validated_data)

    def create(self, validated_data):

        # وضعیت رو دیفالت دومین مقدار choices می‌ذاریم
        status_default = "in_accepting_queue"

        # ساخت سفارش
        order = RepairOrder.objects.create(
            customer=validated_data['customer'],
            console=validated_data['console'],
            description=validated_data['description'],
            status=status_default,  # دومی از choices
        )
        return order

    def get_customer_name(self, obj):
        if obj.customer:
            return obj.customer.full_name
        return None


class RepairManTransactionSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['amount', 'created_at', 'description']
        read_only_fields = fields


class EmployeeRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EmployeeRequest
        fields = ['id', 'title', 'request_type', 'description', 'status', 'employee', 'employee_name', 'created_at']
        read_only_fields = ['id', 'created_at', 'employee']

    def get_employee_name(self, obj):
        return obj.employee.__str__()


class EmployeeSearchSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'role', 'type']

    def get_full_name(self, obj):
        return f"{obj.first_name or ''} {obj.last_name or ''}".strip()

    def get_type(self, obj):
        return "employee"
