from rest_framework import serializers

from inventory.models import DocCategory, DocSubCategory, Document


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
