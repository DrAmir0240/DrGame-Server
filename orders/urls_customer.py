from django.urls import path

from orders import views_customer

urlpatterns = [
    path(
        "", views_customer.CustomerOrderListView.as_view(), name="customer-order-list"
    ),
    path(
        "products/",
        views_customer.CustomerProductOrderListView.as_view(),
        name="customer-order-product-list",
    ),
    path(
        "products/<int:pk>/",
        views_customer.CustomerProductOrderDetailView.as_view(),
        name="customer-order-product-detail",
    ),
    path(
        "products/create/",
        views_customer.CustomerProductOrderCreateView.as_view(),
        name="customer-order-product-create",
    ),
    path(
        "sony/",
        views_customer.CustomerSonyOrderListView.as_view(),
        name="customer-order-sony-list",
    ),
    path(
        "sony/<int:pk>/",
        views_customer.CustomerSonyOrderDetailView.as_view(),
        name="customer-order-sony-detail",
    ),
    path(
        "sony/create/",
        views_customer.CustomerSonyOrderCreateView.as_view(),
        name="customer-order-sony-create",
    ),
    path(
        "repair/",
        views_customer.CustomerRepairOrderListView.as_view(),
        name="customer-order-repair-list",
    ),
    path(
        "repair/<int:pk>/",
        views_customer.CustomerRepairOrderDetailView.as_view(),
        name="customer-order-repair-detail",
    ),
    path(
        "repair/create/",
        views_customer.CustomerRepairOrderCreateView.as_view(),
        name="customer-order-repair-create",
    ),
]
