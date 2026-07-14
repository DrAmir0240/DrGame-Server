from rest_framework import serializers


class SoftDeleteSerializerMixin:
    """
    Serializer-level mixin for soft delete.
    Marks instance as deleted and saves only the required field.
    """

    def destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=("is_deleted",))
        return instance




class EmployeeStatusChoicesSerializer(serializers.Serializer):
    value = serializers.CharField(max_length=50)
    label = serializers.CharField(max_length=100)