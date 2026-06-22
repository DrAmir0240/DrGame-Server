from rest_framework import serializers


class SoftDeleteSerializerMixin:
    def destroy(self, instance):
        instance.is_deleted = True
        instance.save()
        return instance


class EmployeeStatusChoicesSerializer(serializers.Serializer):
    value = serializers.CharField(max_length=50)
    label = serializers.CharField(max_length=100)