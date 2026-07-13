from rest_framework import serializers

from docs.models import DocCategory, DocSubCategory, Document, RealAssetsCategory, RealAssetsSubCategory, RealAssets


class DocCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocCategory
        fields = ["id", "title", "description"]


class DocSubCategorySerializer(serializers.ModelSerializer):
    category_title = serializers.CharField(source="category.title", read_only=True)

    class Meta:
        model = DocSubCategory
        fields = [
            "id",
            "title",
            "description",
            "category",
            "category_title",
        ]


class DocumentSerializer(serializers.ModelSerializer):
    sub_category_title = serializers.CharField(source="category.title", read_only=True)
    main_category_id = serializers.IntegerField(source="category.category.id", read_only=True)
    main_category_title = serializers.CharField(source="category.category.title", read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "file",
            "category",
            "sub_category_title",
            "main_category_id",
            "main_category_title",
            "created_at",
        ]


class DocumentSearchSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['id', 'title', 'type']

    def get_type(self, obj):
        return "document"


class RealAssetsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RealAssetsCategory
        fields = ["id", "title", "description"]


class RealAssetsSubCategorySerializer(serializers.ModelSerializer):
    category_title = serializers.CharField(source="category.title", read_only=True)

    class Meta:
        model = RealAssetsSubCategory
        fields = [
            "id",
            "title",
            "description",
            "category",
            "category_title",
        ]


class RealAssetsSerializer(serializers.ModelSerializer):
    sub_category_title = serializers.CharField(source="category.title", read_only=True)

    main_category_id = serializers.IntegerField(
        source="category.category.id", read_only=True
    )
    main_category_title = serializers.CharField(
        source="category.category.title", read_only=True
    )
    employee_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = RealAssets
        fields = [
            "id",
            "title",
            "image",
            "price",
            "category",
            "sub_category_title",
            "main_category_id",
            "main_category_title",
            "created_at",
            "employee",
            "employee_name"
        ]

    def get_employee_name(self, obj):
        if obj.employee:
            return obj.employee.first_name + " " + obj.employee.last_name
        return ""


class RealAssetsSearchSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = RealAssets
        fields = ['id', 'title', 'price', 'type']

    def get_type(self, obj):
        return "real_asset"
