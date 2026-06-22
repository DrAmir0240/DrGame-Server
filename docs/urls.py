from django.urls import path

from docs import views

urlpatterns = [
    # ==================== Docs ====================
    path("docs/", views.DocumentListAPIView.as_view(), name="doc-list"),
    path("docs/create/", views.DocumentCreateAPIView.as_view(), name="doc-create"),
    path("docs/<int:pk>/", views.DocumentDetailAPIView.as_view(), name="doc-detail"),
    path("docs/categories/", views.DocCategoryListAPIView.as_view(), name="doc-category-list"),
    path("docs/categories/create/", views.DocCategoryCreateAPIView.as_view(), name="doc-category-create"),
    path("docs/sub-categories/", views.DocSubCategoryListAPIView.as_view(), name="doc-sub-category-list"),
    path("docs/sub-categories/create/", views.DocSubCategoryCreateAPIView.as_view(), name="doc-sub-category-create"),

]
