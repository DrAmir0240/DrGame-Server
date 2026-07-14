from django.urls import path

from inventory import views

urlpatterns = [
    # Supplier
    path("suppliers/", views.SupplierListCreateView.as_view(), name="supplier-list-create"),
    path("suppliers/<int:pk>/", views.SupplierRetrieveUpdateDestroyView.as_view(), name="supplier-detail"),

    # ProductCategory
    path("categories/", views.ProductCategoryListCreateView.as_view(), name="category-list-create"),
    path("categories/<int:pk>/", views.ProductCategoryRetrieveUpdateDestroyView.as_view(), name="category-detail"),

    # Product
    path("products/stats/", views.ProductStatsView.as_view(), name="product-stats"),
    path("products/search/", views.ProductSearchView.as_view(), name="product-search"),
    path("products/", views.ProductListCreateView.as_view(), name="product-list-create"),
    path("products/<int:pk>/", views.ProductRetrieveUpdateDestroyView.as_view(), name="product-detail"),
    path("products/choices/", views.ProductDropdownView.as_view(), name="product-choices"),

    # ProductEntity (nested under product)
    path("products/<int:product_id>/entities/", views.ProductEntityListCreateView.as_view(), name="entity-list-create"),
    path("products/<int:product_id>/entities/<int:pk>/", views.ProductEntityRetrieveUpdateDestroyView.as_view(),
         name="entity-detail"),

    # ProductImage (nested under product)
    path("products/<int:product_id>/images/", views.ProductImageListCreateView.as_view(), name="image-list-create"),
    path("products/<int:product_id>/images/<int:pk>/", views.ProductImageRetrieveUpdateDestroyView.as_view(),
         name="image-detail"),

    # InventoryMovement
    path("movements/", views.InventoryMovementListCreateView.as_view(), name="movement-list-create"),
    path("movements/<int:pk>/", views.InventoryMovementRetrieveUpdateDestroyView.as_view(), name="movement-detail"),
    path("movements/dropdown/", views.InventoryMovementDropdownView.as_view(), name="movement-dropdown"),
]
