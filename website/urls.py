from django.urls import path

from . import views

urlpatterns = [
    # --- Home ---
    path("banners/", views.HomeBannerListView.as_view(), name="banners-list"),
    path("sections/", views.HomeSectionListView.as_view(), name="sections-list"),
    path(
        "section-items/<int:section_id>/",
        views.HomeSectionItemListView.as_view(),
        name="section-items-list",
    ),
    path("about-us/", views.AboutUsListView.as_view(), name="about-us-list"),
    # --- Product Store ---
    path(
        "products/search/",
        views.StoreProductSearchView.as_view(),
        name="products-search",
    ),
    path("products/", views.StoreProductListView.as_view(), name="products-list"),
    path(
        "products/<int:pk>/",
        views.StoreProductDetailView.as_view(),
        name="products-detail",
    ),
    path(
        "products/images/",
        views.StoreProductImageListView.as_view(),
        name="products-images-list",
    ),
    # --- Game Store ---
    path("games/search/", views.GameSearchView.as_view(), name="games-search"),
    path("games/", views.GameListView.as_view(), name="games-list"),
    path("games/<int:pk>/", views.GameDetailView.as_view(), name="games-detail"),
    path(
        "games/images/",
        views.GameImageListView.as_view(),
        name="games-images-list",
    ),
    # --- Product Cart ---
    path(
        "cart/product/",
        views.ProductCartDetailView.as_view(),
        name="cart-product-detail",
    ),
    path(
        "cart/product/items/",
        views.ProductCartItemListView.as_view(),
        name="cart-product-items-list",
    ),
    path(
        "cart/product/add/",
        views.ProductCartAddItemView.as_view(),
        name="cart-product-add",
    ),
    path(
        "cart/product/remove/",
        views.ProductCartRemoveItemView.as_view(),
        name="cart-product-remove",
    ),
    # --- Game Cart ---
    path(
        "cart/game/",
        views.GameCartDetailView.as_view(),
        name="cart-game-detail",
    ),
    path(
        "cart/game/matched-accounts/",
        views.MatchedSonyAccountListView.as_view(),
        name="cart-game-matched-accounts",
    ),
    path(
        "cart/game/volume/",
        views.GameCartVolumeView.as_view(),
        name="cart-game-volume",
    ),
    path(
        "cart/game/add/",
        views.GameCartAddItemView.as_view(),
        name="cart-game-add",
    ),
    path(
        "cart/game/remove/",
        views.GameCartRemoveItemView.as_view(),
        name="cart-game-remove",
    ),
]
