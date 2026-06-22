from django.urls import path

from inventory import views

urlpatterns = [
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

    # ==================== Product Views ====================
    path('products/', views.EmployeePanelProductList.as_view(), name='product-list'),
    path('products/<int:pk>/', views.EmployeePanelProductDetail.as_view(), name='product-detail'),
    path('products/add/', views.EmployeePanelAddProduct.as_view(), name='product-add'),
    path('products/choices', views.EmployeePanelProductChoices.as_view(), name='product-choices'),

]
