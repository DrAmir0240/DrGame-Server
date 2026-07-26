from rest_framework import serializers

from blog.models import BlogPost, BlogPostCategory


class BlogPostCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPostCategory
        fields = ["id", "title", "description"]


class BlogPostListSerializer(serializers.ModelSerializer):
    category_title = serializers.CharField(
        source="category.title", read_only=True, default=None
    )
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            "id",
            "title",
            "slug",
            "cover_image",
            "category",
            "category_title",
            "author_name",
            "published_at",
        ]

    def get_author_name(self, obj):
        if obj.author:
            return f"{obj.author.first_name} {obj.author.last_name}"
        return None


class BlogPostDetailSerializer(serializers.ModelSerializer):
    category = BlogPostCategorySerializer(read_only=True)
    images = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            "id",
            "title",
            "slug",
            "body",
            "cover_image",
            "category",
            "author_name",
            "images",
            "published_at",
            "created_at",
            "updated_at",
        ]

    def get_images(self, obj):
        return [
            {
                "id": img.id,
                "image": img.image.url if img.image else None,
            }
            for img in obj.images.all()
        ]

    def get_author_name(self, obj):
        if obj.author:
            return f"{obj.author.first_name} {obj.author.last_name}"
        return None
