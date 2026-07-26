from rest_framework import serializers

from orders.models import (
    ProductOrder,
    SonyAccountOrder,
    RepairOrder,
    SonyAccountOrderCategory,
    SonyAccountOrderStage,
    RepairOrderCategory,
    RepairOrderStage,
    ProductOrderCategory,
    ProductOrderStage,
)


class StageMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SonyAccountOrderStage
        fields = ["id", "title", "order", "is_end"]


class RepairStageMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairOrderStage
        fields = ["id", "title", "order", "is_end"]


class ProductStageMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOrderStage
        fields = ["id", "title", "order", "is_end"]


class SonyOrderCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SonyAccountOrderCategory
        fields = ["id", "title", "type", "account_capacity", "rent_time_days"]


class RepairOrderCategoryMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairOrderCategory
        fields = ["id", "title"]


class ProductOrderCategoryMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOrderCategory
        fields = ["id", "title"]


class StageLogSerializer(serializers.Serializer):
    from_stage_title = serializers.CharField()
    to_stage_title = serializers.CharField()
    created_at = serializers.DateTimeField()


class SonyOrderListSerializer(serializers.ModelSerializer):
    category = SonyOrderCategorySerializer(read_only=True)
    stage = StageMinimalSerializer(read_only=True)

    class Meta:
        model = SonyAccountOrder
        fields = ["id", "category", "stage", "source", "amount", "created_at"]


class SonyOrderDetailSerializer(serializers.ModelSerializer):
    category = SonyOrderCategorySerializer(read_only=True)
    stage = StageMinimalSerializer(read_only=True)
    stage_logs = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()

    class Meta:
        model = SonyAccountOrder
        fields = [
            "id",
            "category",
            "stage",
            "source",
            "amount",
            "created_at",
            "items",
            "stage_logs",
        ]

    def get_stage_logs(self, obj):
        logs = obj.stage_logs.filter(is_deleted=False).select_related(
            "from_stage", "to_stage"
        )
        return StageLogSerializer(
            [
                {
                    "from_stage_title": log.from_stage.title if log.from_stage else "—",
                    "to_stage_title": log.to_stage.title if log.to_stage else "—",
                    "created_at": log.created_at,
                }
                for log in logs
            ],
            many=True,
        ).data

    def get_items(self, obj):
        if obj.stage and obj.stage.is_end:
            from orders.serializers import SonyAccountOrderItemSerializer

            return SonyAccountOrderItemSerializer(
                obj.items.filter(is_deleted=False), many=True
            ).data
        return []


class ProductOrderListSerializer(serializers.ModelSerializer):
    stage = ProductStageMinimalSerializer(read_only=True)

    class Meta:
        model = ProductOrder
        fields = ["id", "stage", "total_amount", "created_at"]


class ProductOrderDetailSerializer(serializers.ModelSerializer):
    stage = ProductStageMinimalSerializer(read_only=True)
    stage_logs = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()

    class Meta:
        model = ProductOrder
        fields = ["id", "stage", "total_amount", "created_at", "items", "stage_logs"]

    def get_stage_logs(self, obj):
        logs = obj.stage_logs.filter(is_deleted=False).select_related(
            "from_stage", "to_stage"
        )
        return StageLogSerializer(
            [
                {
                    "from_stage_title": log.from_stage.title if log.from_stage else "—",
                    "to_stage_title": log.to_stage.title if log.to_stage else "—",
                    "created_at": log.created_at,
                }
                for log in logs
            ],
            many=True,
        ).data

    def get_items(self, obj):
        if obj.stage and obj.stage.is_end:
            return ProductOrderItemCustomerSerializer(
                obj.items.filter(is_deleted=False), many=True
            ).data
        return []


class ProductOrderItemCustomerSerializer(serializers.Serializer):
    product_title = serializers.CharField()
    quantity = serializers.IntegerField()
    unit_price = serializers.IntegerField()


class RepairOrderListSerializer(serializers.ModelSerializer):
    category = RepairOrderCategoryMinimalSerializer(read_only=True)
    stage = RepairStageMinimalSerializer(read_only=True)

    class Meta:
        model = RepairOrder
        fields = ["id", "category", "stage", "repair_fee", "final_amount", "created_at"]


class RepairOrderDetailSerializer(serializers.ModelSerializer):
    category = RepairOrderCategoryMinimalSerializer(read_only=True)
    stage = RepairStageMinimalSerializer(read_only=True)
    devices = serializers.SerializerMethodField()
    stage_logs = serializers.SerializerMethodField()

    class Meta:
        model = RepairOrder
        fields = [
            "id",
            "category",
            "stage",
            "repair_fee",
            "final_amount",
            "created_at",
            "devices",
            "stage_logs",
        ]

    def get_stage_logs(self, obj):
        logs = obj.stage_logs.filter(is_deleted=False).select_related(
            "from_stage", "to_stage"
        )
        return StageLogSerializer(
            [
                {
                    "from_stage_title": log.from_stage.title if log.from_stage else "—",
                    "to_stage_title": log.to_stage.title if log.to_stage else "—",
                    "created_at": log.created_at,
                }
                for log in logs
            ],
            many=True,
        ).data

    def get_devices(self, obj):
        return RepairDeviceCustomerSerializer(
            obj.devices.filter(is_deleted=False), many=True
        ).data


class RepairDeviceCustomerSerializer(serializers.Serializer):
    title = serializers.CharField()
    serial_number = serializers.CharField()


class CustomerOrderCreateSerializer(serializers.Serializer):
    order_type = serializers.ChoiceField(choices=["product", "sony", "repair"])
    category_id = serializers.IntegerField()
    description = serializers.CharField(required=False, allow_blank=True)
