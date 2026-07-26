from django.urls import path

from blog import views

urlpatterns = [
    path("posts/", views.BlogPostListView.as_view(), name="blog-post-list"),
    path(
        "posts/<slug:slug>/",
        views.BlogPostDetailView.as_view(),
        name="blog-post-detail",
    ),
    path(
        "categories/",
        views.BlogCategoryListView.as_view(),
        name="blog-category-list",
    ),
]
