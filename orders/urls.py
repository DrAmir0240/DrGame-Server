from django.urls import path

from orders import views

urlpatterns = [
    # =========================================================================
    # SECTION 1 — SONY ACCOUNT ORDER
    # =========================================================================
    # --- Config (manager) ---
    path('sony-account/categories/', views.SonyAccountOrderCategoryListView.as_view(),
         name='sony-category-list'),
    path('sony-account/categories/create/', views.SonyAccountOrderCategoryCreateView.as_view(),
         name='sony-category-create'),
    path('sony-account/categories/<int:pk>/update/', views.SonyAccountOrderCategoryUpdateView.as_view(),
         name='sony-category-update'),
    path('sony-account/categories/<int:pk>/delete/', views.SonyAccountOrderCategoryDeleteView.as_view(),
         name='sony-category-delete'),

    path('sony-account/categories/<int:category_id>/stages/', views.SonyAccountOrderStageListView.as_view(),
         name='sony-stage-list'),
    path('sony-account/stages/create/', views.SonyAccountOrderStageCreateView.as_view(),
         name='sony-stage-create'),
    path('sony-account/stages/<int:pk>/', views.SonyAccountOrderStageDetailView.as_view(),
         name='sony-stage-detail'),
    path('sony-account/stages/<int:pk>/update/', views.SonyAccountOrderStageUpdateView.as_view(),
         name='sony-stage-update'),
    path('sony-account/stages/<int:pk>/delete/', views.SonyAccountOrderStageDeleteView.as_view(),
         name='sony-stage-delete'),

    path('sony-account/stage-actions/create/', views.SonyAccountOrderStageActionCreateView.as_view(),
         name='sony-stage-action-create'),
    path('sony-account/stage-actions/<int:pk>/update/', views.SonyAccountOrderStageActionUpdateView.as_view(),
         name='sony-stage-action-update'),
    path('sony-account/stage-actions/<int:pk>/delete/', views.SonyAccountOrderStageActionDeleteView.as_view(),
         name='sony-stage-action-delete'),

    # --- Worker (employee) ---
    path('sony-account/my-stages/', views.MySonyAccountStagesView.as_view(),
         name='sony-my-stages'),
    path('sony-account/orders/by-stage/<int:stage_id>/', views.SonyAccountOrderByStageView.as_view(),
         name='sony-orders-by-stage'),
    path('sony-account/orders/<int:pk>/', views.SonyAccountOrderDetailView.as_view(),
         name='sony-order-detail'),
    path('sony-account/orders/<int:order_id>/actions/', views.SonyAccountOrderActionsView.as_view(),
         name='sony-order-actions'),
    path('sony-account/orders/<int:order_id>/execute-action/', views.SonyAccountOrderExecuteActionView.as_view(),
         name='sony-order-execute-action'),
    path('sony-account/orders/<int:order_id>/advance-stage/', views.SonyAccountOrderAdvanceStageView.as_view(),
         name='sony-order-advance-stage'),

    # =========================================================================
    # SECTION 2 — REPAIR ORDER
    # =========================================================================
    # --- Config (manager) ---
    path('repair/categories/', views.RepairOrderCategoryListView.as_view(),
         name='repair-category-list'),
    path('repair/categories/create/', views.RepairOrderCategoryCreateView.as_view(),
         name='repair-category-create'),
    path('repair/categories/<int:pk>/update/', views.RepairOrderCategoryUpdateView.as_view(),
         name='repair-category-update'),
    path('repair/categories/<int:pk>/delete/', views.RepairOrderCategoryDeleteView.as_view(),
         name='repair-category-delete'),

    path('repair/categories/<int:category_id>/stages/', views.RepairOrderStageListView.as_view(),
         name='repair-stage-list'),
    path('repair/stages/create/', views.RepairOrderStageCreateView.as_view(),
         name='repair-stage-create'),
    path('repair/stages/<int:pk>/', views.RepairOrderStageDetailView.as_view(),
         name='repair-stage-detail'),
    path('repair/stages/<int:pk>/update/', views.RepairOrderStageUpdateView.as_view(),
         name='repair-stage-update'),
    path('repair/stages/<int:pk>/delete/', views.RepairOrderStageDeleteView.as_view(),
         name='repair-stage-delete'),

    path('repair/stage-actions/create/', views.RepairOrderStageActionCreateView.as_view(),
         name='repair-stage-action-create'),
    path('repair/stage-actions/<int:pk>/update/', views.RepairOrderStageActionUpdateView.as_view(),
         name='repair-stage-action-update'),
    path('repair/stage-actions/<int:pk>/delete/', views.RepairOrderStageActionDeleteView.as_view(),
         name='repair-stage-action-delete'),

    # --- Worker (employee) ---
    path('repair/my-stages/', views.MyRepairStagesView.as_view(),
         name='repair-my-stages'),
    path('repair/orders/by-stage/<int:stage_id>/', views.RepairOrderByStageView.as_view(),
         name='repair-orders-by-stage'),
    path('repair/orders/<int:pk>/', views.RepairOrderDetailView.as_view(),
         name='repair-order-detail'),
    path('repair/orders/<int:order_id>/actions/', views.RepairOrderActionsView.as_view(),
         name='repair-order-actions'),
    path('repair/orders/<int:order_id>/execute-action/', views.RepairOrderExecuteActionView.as_view(),
         name='repair-order-execute-action'),
    path('repair/orders/<int:order_id>/advance-stage/', views.RepairOrderAdvanceStageView.as_view(),
         name='repair-order-advance-stage'),

    # =========================================================================
    # SECTION 3 — PRODUCT ORDER
    # =========================================================================
    # --- Config (manager) ---
    path('product/categories/', views.ProductOrderCategoryListView.as_view(),
         name='product-category-list'),
    path('product/categories/create/', views.ProductOrderCategoryCreateView.as_view(),
         name='product-category-create'),
    path('product/categories/<int:pk>/update/', views.ProductOrderCategoryUpdateView.as_view(),
         name='product-category-update'),
    path('product/categories/<int:pk>/delete/', views.ProductOrderCategoryDeleteView.as_view(),
         name='product-category-delete'),

    path('product/categories/<int:category_id>/stages/', views.ProductOrderStageListView.as_view(),
         name='product-stage-list'),
    path('product/stages/create/', views.ProductOrderStageCreateView.as_view(),
         name='product-stage-create'),
    path('product/stages/<int:pk>/', views.ProductOrderStageDetailView.as_view(),
         name='product-stage-detail'),
    path('product/stages/<int:pk>/update/', views.ProductOrderStageUpdateView.as_view(),
         name='product-stage-update'),
    path('product/stages/<int:pk>/delete/', views.ProductOrderStageDeleteView.as_view(),
         name='product-stage-delete'),

    path('product/stage-actions/create/', views.ProductOrderStageActionCreateView.as_view(),
         name='product-stage-action-create'),
    path('product/stage-actions/<int:pk>/update/', views.ProductOrderStageActionUpdateView.as_view(),
         name='product-stage-action-update'),
    path('product/stage-actions/<int:pk>/delete/', views.ProductOrderStageActionDeleteView.as_view(),
         name='product-stage-action-delete'),

    # --- Worker (employee) ---
    path('product/my-stages/', views.MyProductStagesView.as_view(),
         name='product-my-stages'),
    path('product/orders/by-stage/<int:stage_id>/', views.ProductOrderByStageView.as_view(),
         name='product-orders-by-stage'),
    path('product/orders/<int:pk>/', views.ProductOrderDetailView.as_view(),
         name='product-order-detail'),
    path('product/orders/<int:order_id>/actions/', views.ProductOrderActionsView.as_view(),
         name='product-order-actions'),
    path('product/orders/<int:order_id>/execute-action/', views.ProductOrderExecuteActionView.as_view(),
         name='product-order-execute-action'),
    path('product/orders/<int:order_id>/advance-stage/', views.ProductOrderAdvanceStageView.as_view(),
         name='product-order-advance-stage'),
]
