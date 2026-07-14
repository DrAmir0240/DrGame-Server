from rest_framework import serializers

from platform_settings.serializers import SoftDeleteSerializerMixin
from inventory.models import (
    InventoryMovement,
    Product,
    ProductCategory,
    ProductEntity,
    ProductImage,
    Supplier,
)


class SupplierSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "is_deleted")


class InventoryStatsSerializer(serializers.Serializer):
    total_inventory_value = serializers.DecimalField(max_digits=30, decimal_places=5)
    green_count = serializers.IntegerField()
    yellow_count = serializers.IntegerField()
    red_count = serializers.IntegerField()


class ProductCategorySerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "is_deleted")


class ProductImageSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "is_deleted")


class ProductEntitySerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ProductEntity
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "is_deleted")


class ProductSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = (
            "created_at",
            "updated_at",
            "is_deleted",
            "units_sold",
            "stock",
        )


class SupplierDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ("id", "name")


class ProductCategoryDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ("id", "title")


class ProductDropdownSerializer(serializers.Serializer):
    suppliers = SupplierDropdownSerializer(many=True)
    categories = ProductCategoryDropdownSerializer(many=True)


class InventoryMovementSerializer(SoftDeleteSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = InventoryMovement
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "is_deleted")


class InventoryMovementDropdownSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()

    class Meta:
        model = InventoryMovement
        fields = ("id", "label", "direction")

    def get_label(self, obj) -> str:
        if obj.product_entity:
            return f"{obj.product_entity.uni_id} — {obj.product.title}"
        return obj.product.title
