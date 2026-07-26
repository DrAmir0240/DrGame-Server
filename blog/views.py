from rest_framework import generics
from rest_framework.permissions import AllowAny

from blog.models import BlogPost, BlogPostCategory
from blog.serializers import (
    BlogPostListSerializer,
    BlogPostDetailSerializer,
    BlogPostCategorySerializer,
)


class BlogPostListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = BlogPostListSerializer

    def get_queryset(self):
        qs = BlogPost.objects.filter(
            is_deleted=False, status="published"
        ).select_related("category", "author")
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category_id=category)
        return qs.order_by("-published_at")


class BlogPostDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = BlogPostDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return BlogPost.objects.filter(
            is_deleted=False, status="published"
        ).select_related("category", "author")


class BlogCategoryListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = BlogPostCategorySerializer
    queryset = BlogPostCategory.objects.filter(is_deleted=False)
