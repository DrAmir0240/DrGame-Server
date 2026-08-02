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
        "repair/",
        views_customer.CustomerRepairOrderListView.as_view(),
        name="customer-order-repair-list",
    ),
    path(
        "repair/<int:pk>/",
        views_customer.CustomerRepairOrderDetailView.as_view(),
        name="customer-order-repair-detail",
    ),
]
