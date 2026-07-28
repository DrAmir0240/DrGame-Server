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
    # --- Customer: Blog ---
    path("blog/categories/", views.CustomerBlogCategoryListView.as_view()),
    path("blog/", views.CustomerBlogListView.as_view()),
    path("blog/<int:pk>/", views.CustomerBlogDetailView.as_view()),
    path("blog/<int:blog_pk>/images/", views.CustomerBlogImageListView.as_view()),
    # --- Customer: Video ---
    path("videos/", views.CustomerVideoListView.as_view()),
    path("videos/<int:pk>/", views.CustomerVideoDetailView.as_view()),
    # --- Employee: Home ---
    path("employee/banners/", views.EmployeeHomeBannerListCreateView.as_view()),
    path("employee/banners/<int:pk>/", views.EmployeeHomeBannerDetailView.as_view()),
    path("employee/sections/", views.EmployeeHomeSectionListCreateView.as_view()),
    path("employee/sections/<int:pk>/", views.EmployeeHomeSectionDetailView.as_view()),
    path(
        "employee/section-items/", views.EmployeeHomeSectionItemListCreateView.as_view()
    ),
    path(
        "employee/section-items/<int:pk>/",
        views.EmployeeHomeSectionItemDetailView.as_view(),
    ),
    path("employee/about-us/", views.EmployeeAboutUsListCreateView.as_view()),
    path("employee/about-us/<int:pk>/", views.EmployeeAboutUsDetailView.as_view()),
    # --- Employee: Product Store ---
    path("employee/products/search/", views.EmployeeStoreProductSearchView.as_view()),
    path(
        "employee/product-categories/",
        views.EmployeeStoreProductCategoryListCreateView.as_view(),
    ),
    path(
        "employee/product-categories/<int:pk>/",
        views.EmployeeStoreProductCategoryDetailView.as_view(),
    ),
    path("employee/products/", views.EmployeeStoreProductListCreateView.as_view()),
    path("employee/products/<int:pk>/", views.EmployeeStoreProductDetailView.as_view()),
    path(
        "employee/products/<int:store_product_pk>/entities/",
        views.EmployeeProductEntityListView.as_view(),
    ),
    path(
        "employee/products/<int:store_product_pk>/images/",
        views.EmployeeStoreProductImageListCreateView.as_view(),
    ),
    path(
        "employee/products/<int:store_product_pk>/images/<int:pk>/",
        views.EmployeeStoreProductImageDetailView.as_view(),
    ),
    # --- Employee: Game Store ---
    path("employee/games/search/", views.EmployeeGameSearchView.as_view()),
    path(
        "employee/game-categories/", views.EmployeeGameCategoryListCreateView.as_view()
    ),
    path(
        "employee/game-categories/<int:pk>/",
        views.EmployeeGameCategoryDetailView.as_view(),
    ),
    path("employee/games/", views.EmployeeGameListCreateView.as_view()),
    path("employee/games/<int:pk>/", views.EmployeeGameDetailView.as_view()),
    path(
        "employee/games/<int:game_pk>/images/",
        views.EmployeeGameImageListCreateView.as_view(),
    ),
    path(
        "employee/games/<int:game_pk>/images/<int:pk>/",
        views.EmployeeGameImageDetailView.as_view(),
    ),
    # --- Employee: Blog ---
    path("employee/blog/search/", views.EmployeeBlogSearchView.as_view()),
    path(
        "employee/blog/categories/", views.EmployeeBlogCategoryListCreateView.as_view()
    ),
    path(
        "employee/blog/categories/<int:pk>/",
        views.EmployeeBlogCategoryDetailView.as_view(),
    ),
    path("employee/blog/", views.EmployeeBlogListCreateView.as_view()),
    path("employee/blog/<int:pk>/", views.EmployeeBlogDetailView.as_view()),
    path(
        "employee/blog/<int:blog_pk>/images/",
        views.EmployeeBlogImageListCreateView.as_view(),
    ),
    path(
        "employee/blog/<int:blog_pk>/images/<int:pk>/",
        views.EmployeeBlogImageDetailView.as_view(),
    ),
    # --- Employee: Video ---
    path("employee/videos/search/", views.EmployeeVideoSearchView.as_view()),
    path("employee/videos/", views.EmployeeVideoListCreateView.as_view()),
    path("employee/videos/<int:pk>/", views.EmployeeVideoDetailView.as_view()),
]
