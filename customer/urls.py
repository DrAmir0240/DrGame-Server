from django.urls import path, include

urlpatterns = [
    # Profile & Wishlist (crm app)
    path("", include("crm.urls_customer")),
    # Orders (orders app)
    path("orders/", include("orders.urls_customer")),
    # Tickets (support app)
    path("tickets/", include("support.urls_customer")),
]
