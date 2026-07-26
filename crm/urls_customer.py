from django.urls import path

from crm import views

urlpatterns = [
    # Profile
    path("profile/", views.CustomerProfileView.as_view(), name="customer-profile"),
    path(
        "profile/pic/",
        views.CustomerProfilePicView.as_view(),
        name="customer-profile-pic",
    ),
    # Wallet
    path("wallet/", views.CustomerWalletView.as_view(), name="customer-wallet"),
    path(
        "wallet/transactions/",
        views.CustomerWalletTransactionsView.as_view(),
        name="customer-wallet-transactions",
    ),
    path(
        "wallet/charge/",
        views.CustomerWalletChargeView.as_view(),
        name="customer-wallet-charge",
    ),
    # Wishlist
    path(
        "wishlist/",
        views.CustomerWishlistListView.as_view(),
        name="customer-wishlist-list",
    ),
    path(
        "wishlist/add/",
        views.CustomerWishlistAddView.as_view(),
        name="customer-wishlist-add",
    ),
    path(
        "wishlist/remove/<int:pk>/",
        views.CustomerWishlistRemoveView.as_view(),
        name="customer-wishlist-remove",
    ),
    path(
        "wishlist/toggle/",
        views.CustomerWishlistToggleView.as_view(),
        name="customer-wishlist-toggle",
    ),
]
