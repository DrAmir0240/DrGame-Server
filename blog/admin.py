from django.contrib import admin

from blog.models import BlogPost, BlogPostCategory, BlogPostImage


@admin.register(BlogPostCategory)
class BlogPostCategoryAdmin(admin.ModelAdmin):
    list_display = ["title", "created_at", "is_deleted"]
    search_fields = ["title"]


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "status", "published_at", "created_at"]
    list_filter = ["status", "category"]
    search_fields = ["title", "body"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["created_at", "updated_at"]


@admin.register(BlogPostImage)
class BlogPostImageAdmin(admin.ModelAdmin):
    list_display = ["post", "created_at"]
