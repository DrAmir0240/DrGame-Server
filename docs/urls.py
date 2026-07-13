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

    # ==================== Real Assets ====================
    path("real-assets/", views.RealAssetsListAPIView.as_view(), name="real-asset-list"),
    path("real-assets/create/", views.RealAssetsCreateAPIView.as_view(), name="real-asset-create"),
    path("real-assets/<int:pk>/", views.RealAssetsDetailAPIView.as_view(), name="real-asset-detail"),
    path("real-assets/categories/", views.RealAssetsCategoryListAPIView.as_view(), name="real-asset-category-list"),
    path("real-assets/categories/create/", views.RealAssetsCategoryCreateAPIView.as_view(),
         name="real-asset-category-create"),
    path("real-assets/sub-categories/", views.RealAssetsSubCategoryListAPIView.as_view(),
         name="real-asset-sub-category-list"),
    path("real-assets/sub-categories/create/", views.RealAssetsSubCategoryCreateAPIView.as_view(),
         name="real-asset-sub-category-create"),

]
