# DrGame — Website App (Phase 2) + PSN App: Claude Code Implementation Guide

## Context

This is Phase 2. Phase 1 (customer home, product store, game store, carts) is already implemented
in `website/views.py`, `website/serializers.py`, `website/urls.py`, `website/services.py`, `website/filters.py`.

This file adds:
1. **Customer section** — Blog + Video (append to existing customer block)
2. **Employee section** — Home, Product Store, Game Store, Blog, Video (new block in same files)
3. **PSN app** — new app, employee-only

---

## Conventions (Same as Phase 1)

| Rule | Detail |
|---|---|
| Views | `rest_framework.generics.*` only |
| Schema | `@extend_schema(tags=[...], summary="...")` on every view |
| Employee permission | `IsEmployee` from `users.permissions` |
| Customer permission | `AllowAny` (no auth required for customer endpoints) |
| Serializers | Every view has its own serializer class |
| Services | Repeated logic → `services.py` |
| Filters | `django_filters.rest_framework.DjangoFilterBackend` |
| Search | `rest_framework.filters.SearchFilter` |
| No cache | Do not add caching |
| Clean code | No warnings, no unused imports, full type hints on service functions |

---

## Phase 2 — File Structure

### Website app (extend existing files)

```
website/
├── views.py        ← append new sections
├── serializers.py  ← append new serializers
├── urls.py         ← append new url patterns
├── filters.py      ← append new filtersets
├── services.py     ← append new service functions
```

### PSN app (new files)

```
psn/
├── views.py
├── serializers.py
├── urls.py
├── filters.py
└── services.py
```

---

## Part 1 — Website App: Customer Section Completion

Append inside the existing `# CUSTOMER SECTION` block.

---

### Section: Blog (Customer)

**Tag:** `"Website — Customer: Blog"`
**Permission:** `AllowAny`

---

#### `CustomerBlogCategoryListView`

- **URL:** `GET /blog/categories/`
- **View:** `ListAPIView`
- **Model:** `store.BlogPostCategory`
- **Filter:** `is_deleted=False`
- **Serializer fields:** `id`, `title`, `description`
- **Schema:** `summary="List blog categories"`

---

#### `CustomerBlogListView`

- **URL:** `GET /blog/`
- **View:** `ListAPIView`
- **Model:** `store.BlogPost`
- **Filter backends:** `DjangoFilterBackend`
- **Filterset:** `CustomerBlogFilter` in `filters.py`
  - Filterable fields: `category` (exact), `status` (exact), `author` (exact)
- **Queryset filter:** `is_deleted=False`, `status="published"`
- **Serializer fields:** `id`, `title`, `slug`, `cover_image`, `category_id`, `category_title`, `author_id`, `author_name`, `published_at`
- **Schema:** `summary="List published blog posts"`

---

#### `CustomerBlogDetailView`

- **URL:** `GET /blog/<int:pk>/`
- **View:** `RetrieveAPIView`
- **Model:** `store.BlogPost`
- **Queryset filter:** `is_deleted=False`, `status="published"`
- **Serializer fields:** `id`, `title`, `slug`, `body`, `cover_image`, `category_id`, `category_title`, `author_id`, `author_name`, `published_at`
- **Schema:** `summary="Retrieve blog post detail"`

---

#### `CustomerBlogImageListView`

- **URL:** `GET /blog/<int:blog_pk>/images/`
- **View:** `ListAPIView`
- **Model:** `store.BlogPostImage`
- **Filter:** `post_id=blog_pk` from URL kwargs
- **Serializer fields:** `id`, `image`, `priority`, `post_id`
- **Schema:** `summary="List images for a blog post"`

---

### Section: Video (Customer)

**Tag:** `"Website — Customer: Video"`
**Permission:** `AllowAny`

---

#### `CustomerVideoListView`

- **URL:** `GET /videos/`
- **View:** `ListAPIView`
- **Model:** `store.Video`
- **Queryset filter:** `status="published"`
- **Ordering:** `priority`
- **Serializer fields:** `id`, `title`, `slug`, `description`, `duration`, `priority`, `status`
- **Note:** do NOT expose `video_file` in list — only in detail
- **Schema:** `summary="List published videos"`

---

#### `CustomerVideoDetailView`

- **URL:** `GET /videos/<int:pk>/`
- **View:** `RetrieveAPIView`
- **Model:** `store.Video`
- **Queryset filter:** `status="published"`
- **Serializer fields:** `id`, `title`, `slug`, `description`, `video_file`, `duration`, `priority`, `status`
- **Schema:** `summary="Retrieve video detail with file URL"`

---

## Part 2 — Website App: Employee Section

Add a new comment block in all files:

```python
# ============================================================
# EMPLOYEE SECTION
# ============================================================
```

All views use `permission_classes = [IsEmployee]`.
Import: `from users.permissions import IsEmployee`

---

### Section: Home (Employee)

**Tag:** `"Website — Employee: Home"`

Full CRUD for all home management models.

---

#### `EmployeeHomeBannerListCreateView`

- **URL:** `GET POST /employee/banners/`
- **View:** `ListCreateAPIView`
- **Model:** `store.HomeBanner`
- **Serializer fields:** `id`, `title`, `image`, `is_chosen`, `order`
- **Schema:** `summary="List or create home banners"`

---

#### `EmployeeHomeBannerDetailView`

- **URL:** `GET PUT PATCH DELETE /employee/banners/<int:pk>/`
- **View:** `RetrieveUpdateDestroyAPIView`
- **Model:** `store.HomeBanner`
- **Serializer fields:** `id`, `title`, `image`, `is_chosen`, `order`
- **Schema:** `summary="Retrieve, update or delete a home banner"`

---

#### `EmployeeHomeSectionListCreateView`

- **URL:** `GET POST /employee/sections/`
- **View:** `ListCreateAPIView`
- **Model:** `store.HomeSection`
- **Filter:** `is_deleted=False`
- **Serializer fields:** `id`, `title`, `model_content`
- **Schema:** `summary="List or create home sections"`

---

#### `EmployeeHomeSectionDetailView`

- **URL:** `GET PUT PATCH DELETE /employee/sections/<int:pk>/`
- **View:** `RetrieveUpdateDestroyAPIView`
- **Model:** `store.HomeSection`
- **Delete:** soft delete — set `is_deleted=True`, override `perform_destroy`
- **Serializer fields:** `id`, `title`, `model_content`
- **Schema:** `summary="Retrieve, update or delete a home section"`

---

#### `EmployeeHomeSectionItemListCreateView`

- **URL:** `GET POST /employee/section-items/`
- **View:** `ListCreateAPIView`
- **Model:** `store.HomeSectionItem`
- **Filter:** `is_deleted=False`
- **Query param (list):** `section_id` — filter by section
- **Serializer fields:** `id`, `section_id`, `item_id`, `is_active`
- **Schema:** `summary="List or create home section items"`

---

#### `EmployeeHomeSectionItemDetailView`

- **URL:** `GET PUT PATCH DELETE /employee/section-items/<int:pk>/`
- **View:** `RetrieveUpdateDestroyAPIView`
- **Model:** `store.HomeSectionItem`
- **Delete:** soft delete
- **Serializer fields:** `id`, `section_id`, `item_id`, `is_active`
- **Schema:** `summary="Retrieve, update or delete a home section item"`

---

#### `EmployeeAboutUsListCreateView`

- **URL:** `GET POST /employee/about-us/`
- **View:** `ListCreateAPIView`
- **Model:** `store.AboutUs`
- **Filter:** `is_deleted=False`
- **Serializer fields:** `id`, `title`, `logo`, `phone_number`, `email`, `address`, `e_namaad`, `e_namaad_url`, `is_active`
- **Schema:** `summary="List or create about-us entries"`

---

#### `EmployeeAboutUsDetailView`

- **URL:** `GET PUT PATCH DELETE /employee/about-us/<int:pk>/`
- **View:** `RetrieveUpdateDestroyAPIView`
- **Model:** `store.AboutUs`
- **Delete:** soft delete
- **Serializer fields:** `id`, `title`, `logo`, `phone_number`, `email`, `address`, `e_namaad`, `e_namaad_url`, `is_active`
- **Schema:** `summary="Retrieve, update or delete an about-us entry"`

---

### Section: Product Store (Employee)

**Tag:** `"Website — Employee: Product Store"`

---

#### `EmployeeStoreProductSearchView`

- **URL:** `GET /employee/products/search/`
- **View:** `ListAPIView`
- **Model:** `store.StoreProduct`
- **Filter backends:** `SearchFilter`
- **Search fields:** `title`, `product__title`, `product__description`, `product__category__title`
- **Filter:** `is_deleted=False`
- **Serializer fields:** `id`, `title`, `product_id`, `product_title`, `product_main_img`, `product_stock`
- **Schema:** `summary="Search store products (employee)"`

---

#### `EmployeeStoreProductCategoryListCreateView`

- **URL:** `GET POST /employee/product-categories/`
- **View:** `ListCreateAPIView`
- **Model:** `inventory.ProductCategory`
- **Serializer fields:** `id`, `title`
- **Schema:** `summary="List or create product categories"`

---

#### `EmployeeStoreProductCategoryDetailView`

- **URL:** `GET PUT PATCH DELETE /employee/product-categories/<int:pk>/`
- **View:** `RetrieveUpdateDestroyAPIView`
- **Model:** `inventory.ProductCategory`
- **Serializer fields:** `id`, `title`
- **Schema:** `summary="Retrieve, update or delete a product category"`

---

#### `EmployeeStoreProductListCreateView`

- **URL:** `GET POST /employee/products/`
- **View:** `ListCreateAPIView`
- **Model:** `store.StoreProduct`
- **Filter backends:** `DjangoFilterBackend`
- **Filterset:** `EmployeeStoreProductFilter` in `filters.py`
  - Same fields as customer filter + add `is_deleted` (boolean)
- **Queryset:** all (no `is_deleted` pre-filter — employee sees everything, use filterset)
- **Serializer fields:** `id`, `title`, `product_id`, `product_title`, `product_main_img`, `product_price`, `product_stock`, `is_deleted`
- **Schema:** `summary="List or create store products (employee)"`

---

#### `EmployeeStoreProductDetailView`

- **URL:** `GET PUT PATCH DELETE /employee/products/<int:pk>/`
- **View:** `RetrieveUpdateDestroyAPIView`
- **Model:** `store.StoreProduct`
- **Delete:** soft delete
- **Serializer fields:** `id`, `title`, `product_id`
- **Schema:** `summary="Retrieve, update or delete a store product"`

---

#### `EmployeeProductEntityListView`

- **URL:** `GET /employee/products/<int:store_product_pk>/entities/`
- **View:** `ListAPIView`
- **Model:** `inventory.ProductEntity`
- **Logic:** filter by `product_id` from the related `StoreProduct`:
  - First get `StoreProduct` by `store_product_pk` → raise `NotFound` if missing
  - Then filter `ProductEntity` by `product_id=store_product.product_id`, `is_deleted=False`
- **Service function:** `get_entities_for_store_product(store_product_pk: int) -> QuerySet` in `services.py`
- **Serializer fields:** `id`, `uni_id`, `product_id`, `color`, `main_img`
- **Schema:** `summary="List product entities for a store product"`

---

#### `EmployeeStoreProductImageListCreateView`

- **URL:** `GET POST /employee/products/<int:store_product_pk>/images/`
- **View:** `ListCreateAPIView`
- **Model:** `store.StoreProductImage`
- **Filter:** `product_id=store_product_pk`, `is_deleted=False`
- **Create:** set `product_id=store_product_pk` in `perform_create`
- **Serializer fields:** `id`, `img`, `product_id`
- **Schema:** `summary="List or create images for a store product"`

---

#### `EmployeeStoreProductImageDetailView`

- **URL:** `GET PUT PATCH DELETE /employee/products/<int:store_product_pk>/images/<int:pk>/`
- **View:** `RetrieveUpdateDestroyAPIView`
- **Model:** `store.StoreProductImage`
- **Delete:** soft delete
- **Serializer fields:** `id`, `img`, `product_id`
- **Schema:** `summary="Retrieve, update or delete a store product image"`

---

### Section: Game Store (Employee)

**Tag:** `"Website — Employee: Game Store"`

---

#### `EmployeeGameSearchView`

- **URL:** `GET /employee/games/search/`
- **View:** `ListAPIView`
- **Model:** `store.Game`
- **Filter backends:** `SearchFilter`
- **Search fields:** `title`, `description`, `category__title`
- **Filter:** `is_deleted=False`
- **Serializer fields:** `id`, `title`, `main_img`, `category_id`, `category_title`, `volume`, `units_sold`
- **Schema:** `summary="Search games (employee)"`

---

#### `EmployeeGameCategoryListCreateView`

- **URL:** `GET POST /employee/game-categories/`
- **View:** `ListCreateAPIView`
- **Model:** `store.GameCategory`
- **Filter:** `is_deleted=False`
- **Serializer fields:** `id`, `title`, `description`
- **Schema:** `summary="List or create game categories"`

---

#### `EmployeeGameCategoryDetailView`

- **URL:** `GET PUT PATCH DELETE /employee/game-categories/<int:pk>/`
- **View:** `RetrieveUpdateDestroyAPIView`
- **Model:** `store.GameCategory`
- **Delete:** soft delete
- **Serializer fields:** `id`, `title`, `description`
- **Schema:** `summary="Retrieve, update or delete a game category"`

---

#### `EmployeeGameListCreateView`

- **URL:** `GET POST /employee/games/`
- **View:** `ListCreateAPIView`
- **Model:** `store.Game`
- **Filter backends:** `DjangoFilterBackend`
- **Filterset:** `EmployeeGameFilter` in `filters.py`
  - Same as customer + add `is_deleted` (boolean)
- **Serializer fields:** `id`, `title`, `main_img`, `description`, `volume`, `units_sold`, `category_id`, `is_deleted`
- **Schema:** `summary="List or create games (employee)"`

---

#### `EmployeeGameDetailView`

- **URL:** `GET PUT PATCH DELETE /employee/games/<int:pk>/`
- **View:** `RetrieveUpdateDestroyAPIView`
- **Model:** `store.Game`
- **Delete:** soft delete
- **Business logic (service):** reuse `get_game_account_stock(game_id)` from Phase 1
- **Serializer fields:** `id`, `title`, `main_img`, `description`, `volume`, `units_sold`, `category_id`, `account_stock`, `is_deleted`
- **Schema:** `summary="Retrieve, update or delete a game (employee)"`

---

#### `EmployeeGameImageListCreateView`

- **URL:** `GET POST /employee/games/<int:game_pk>/images/`
- **View:** `ListCreateAPIView`
- **Model:** `store.GameImage`
- **Filter:** `game_id=game_pk`, `is_deleted=False`
- **Create:** set `game_id=game_pk` in `perform_create`
- **Serializer fields:** `id`, `img`, `game_id`
- **Schema:** `summary="List or create game images"`

---

#### `EmployeeGameImageDetailView`

- **URL:** `GET PUT PATCH DELETE /employee/games/<int:game_pk>/images/<int:pk>/`
- **View:** `RetrieveUpdateDestroyAPIView`
- **Model:** `store.GameImage`
- **Delete:** soft delete
- **Serializer fields:** `id`, `img`, `game_id`
- **Schema:** `summary="Retrieve, update or delete a game image"`

---

### Section: Blog (Employee)

**Tag:** `"Website — Employee: Blog"`

---

#### `EmployeeBlogSearchView`

- **URL:** `GET /employee/blog/search/`
- **View:** `ListAPIView`
- **Filter backends:** `SearchFilter`
- **Search fields:** `title`, `body`, `slug`, `author__first_name`, `author__last_name`, `category__title`
- **Model:** `store.BlogPost`
- **Filter:** `is_deleted=False`
- **Serializer fields:** `id`, `title`, `slug`, `status`, `author_id`, `author_name`, `category_id`, `published_at`
- **Schema:** `summary="Search blog posts (employee)"`

---

#### `EmployeeBlogCategoryListCreateView`

- **URL:** `GET POST /employee/blog/categories/`
- **View:** `ListCreateAPIView`
- **Model:** `store.BlogPostCategory`
- **Filter backends:** `DjangoFilterBackend`
- **Filterset:** `BlogCategoryFilter` in `filters.py`
  - Filterable fields: `is_deleted` (boolean)
- **Serializer fields:** `id`, `title`, `description`, `is_deleted`
- **Schema:** `summary="List or create blog categories"`

---

#### `EmployeeBlogCategoryDetailView`

- **URL:** `GET PUT PATCH DELETE /employee/blog/categories/<int:pk>/`
- **View:** `RetrieveUpdateDestroyAPIView`
- **Model:** `store.BlogPostCategory`
- **Delete:** soft delete
- **Serializer fields:** `id`, `title`, `description`, `is_deleted`
- **Schema:** `summary="Retrieve, update or delete a blog category"`

---

#### `EmployeeBlogListCreateView`

- **URL:** `GET POST /employee/blog/`
- **View:** `ListCreateAPIView`
- **Model:** `store.BlogPost`
- **Filter backends:** `DjangoFilterBackend`
- **Filterset:** `EmployeeBlogFilter` in `filters.py`
  - Filterable fields: `category` (exact), `status` (exact), `author` (exact), `is_deleted` (boolean)
- **Create logic:** on `perform_create`, set `author=request.user.employee`
- **Serializer fields:** `id`, `title`, `slug`, `body`, `cover_image`, `category_id`, `author_id`, `status`, `published_at`, `is_deleted`
- **Schema:** `summary="List or create blog posts"`

---

#### `EmployeeBlogDetailView`

- **URL:** `GET PUT PATCH DELETE /employee/blog/<int:pk>/`
- **View:** `RetrieveUpdateDestroyAPIView`
- **Model:** `store.BlogPost`
- **Delete:** soft delete
- **Serializer fields:** `id`, `title`, `slug`, `body`, `cover_image`, `category_id`, `author_id`, `status`, `published_at`, `is_deleted`
- **Schema:** `summary="Retrieve, update or delete a blog post"`

---

#### `EmployeeBlogImageListCreateView`

- **URL:** `GET POST /employee/blog/<int:blog_pk>/images/`
- **View:** `ListCreateAPIView`
- **Model:** `store.BlogPostImage`
- **Filter:** `post_id=blog_pk`
- **Create:** set `post_id=blog_pk` in `perform_create`
- **Serializer fields:** `id`, `image`, `priority`, `post_id`
- **Schema:** `summary="List or create blog post images"`

---

#### `EmployeeBlogImageDetailView`

- **URL:** `GET PUT PATCH DELETE /employee/blog/<int:blog_pk>/images/<int:pk>/`
- **View:** `RetrieveUpdateDestroyAPIView`
- **Model:** `store.BlogPostImage`
- **Delete:** hard delete (no `is_deleted` on this model)
- **Serializer fields:** `id`, `image`, `priority`, `post_id`
- **Schema:** `summary="Retrieve, update or delete a blog post image"`

---

### Section: Video (Employee)

**Tag:** `"Website — Employee: Video"`

---

#### `EmployeeVideoSearchView`

- **URL:** `GET /employee/videos/search/`
- **View:** `ListAPIView`
- **Filter backends:** `SearchFilter`
- **Search fields:** `title`, `description`, `slug`
- **Model:** `store.Video`
- **Serializer fields:** `id`, `title`, `slug`, `status`, `duration`, `priority`
- **Schema:** `summary="Search videos (employee)"`

---

#### `EmployeeVideoListCreateView`

- **URL:** `GET POST /employee/videos/`
- **View:** `ListCreateAPIView`
- **Model:** `store.Video`
- **Filter backends:** `DjangoFilterBackend`
- **Filterset:** `EmployeeVideoFilter` in `filters.py`
  - Filterable fields: `status` (exact)
- **Ordering:** `priority`
- **Serializer fields:** `id`, `title`, `slug`, `description`, `video_file`, `status`, `duration`, `priority`
- **Schema:** `summary="List or create videos (employee)"`

---

#### `EmployeeVideoDetailView`

- **URL:** `GET PUT PATCH DELETE /employee/videos/<int:pk>/`
- **View:** `RetrieveUpdateDestroyAPIView`
- **Model:** `store.Video`
- **Delete:** hard delete (no `is_deleted` on this model)
- **Serializer fields:** `id`, `title`, `slug`, `description`, `video_file`, `status`, `duration`, `priority`
- **Schema:** `summary="Retrieve, update or delete a video"`

---

## Part 2 — Website URLs to Append

```python
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
path("employee/section-items/", views.EmployeeHomeSectionItemListCreateView.as_view()),
path("employee/section-items/<int:pk>/", views.EmployeeHomeSectionItemDetailView.as_view()),
path("employee/about-us/", views.EmployeeAboutUsListCreateView.as_view()),
path("employee/about-us/<int:pk>/", views.EmployeeAboutUsDetailView.as_view()),

# --- Employee: Product Store ---
path("employee/products/search/", views.EmployeeStoreProductSearchView.as_view()),
path("employee/product-categories/", views.EmployeeStoreProductCategoryListCreateView.as_view()),
path("employee/product-categories/<int:pk>/", views.EmployeeStoreProductCategoryDetailView.as_view()),
path("employee/products/", views.EmployeeStoreProductListCreateView.as_view()),
path("employee/products/<int:pk>/", views.EmployeeStoreProductDetailView.as_view()),
path("employee/products/<int:store_product_pk>/entities/", views.EmployeeProductEntityListView.as_view()),
path("employee/products/<int:store_product_pk>/images/", views.EmployeeStoreProductImageListCreateView.as_view()),
path("employee/products/<int:store_product_pk>/images/<int:pk>/", views.EmployeeStoreProductImageDetailView.as_view()),

# --- Employee: Game Store ---
path("employee/games/search/", views.EmployeeGameSearchView.as_view()),
path("employee/game-categories/", views.EmployeeGameCategoryListCreateView.as_view()),
path("employee/game-categories/<int:pk>/", views.EmployeeGameCategoryDetailView.as_view()),
path("employee/games/", views.EmployeeGameListCreateView.as_view()),
path("employee/games/<int:pk>/", views.EmployeeGameDetailView.as_view()),
path("employee/games/<int:game_pk>/images/", views.EmployeeGameImageListCreateView.as_view()),
path("employee/games/<int:game_pk>/images/<int:pk>/", views.EmployeeGameImageDetailView.as_view()),

# --- Employee: Blog ---
path("employee/blog/search/", views.EmployeeBlogSearchView.as_view()),
path("employee/blog/categories/", views.EmployeeBlogCategoryListCreateView.as_view()),
path("employee/blog/categories/<int:pk>/", views.EmployeeBlogCategoryDetailView.as_view()),
path("employee/blog/", views.EmployeeBlogListCreateView.as_view()),
path("employee/blog/<int:pk>/", views.EmployeeBlogDetailView.as_view()),
path("employee/blog/<int:blog_pk>/images/", views.EmployeeBlogImageListCreateView.as_view()),
path("employee/blog/<int:blog_pk>/images/<int:pk>/", views.EmployeeBlogImageDetailView.as_view()),

# --- Employee: Video ---
path("employee/videos/search/", views.EmployeeVideoSearchView.as_view()),
path("employee/videos/", views.EmployeeVideoListCreateView.as_view()),
path("employee/videos/<int:pk>/", views.EmployeeVideoDetailView.as_view()),
```

---

## Part 3 — PSN App

New app: `psn/`
All views: `permission_classes = [IsEmployee]`
Import: `from users.permissions import IsEmployee`

**Tag prefix:** `"PSN — Employee"`

---

### `PSNSonyAccountListCreateView`

- **URL:** `GET POST /psn/accounts/`
- **View:** `ListCreateAPIView`
- **Model:** `psn.SonyAccount`
- **Filter backends:** `DjangoFilterBackend`, `SearchFilter`
- **Search fields:** `username`
- **Filterset:** `SonyAccountFilter` in `psn/filters.py`
  - Filterable fields: `status` (exact), `region` (exact), `plus` (boolean), `bank_account_status` (boolean), `employee` (exact), `is_deleted` (boolean)
- **Serializer fields (list):** `id`, `username`, `employee_id`, `employee_name`, `status_id`, `status_title`, `region`, `plus`, `price`, `is_deleted`
- **Serializer fields (create):** `username`, `password`, `employee`, `two_step`, `status`, `bank_account_status`, `bank_account`, `plus`, `region`, `price`, `sell_method`
- **Note:** Use two separate serializers — `SonyAccountListSerializer` and `SonyAccountCreateSerializer`. Override `get_serializer_class` to return the right one based on `self.request.method`.
- **Schema:** `summary="List or create Sony accounts"`

---

### `PSNSonyAccountDetailView`

- **URL:** `GET PUT PATCH DELETE /psn/accounts/<int:pk>/`
- **View:** `RetrieveUpdateDestroyAPIView`
- **Model:** `psn.SonyAccount`
- **Delete:** soft delete
- **Serializer fields:** `id`, `username`, `password`, `employee_id`, `two_step`, `status_id`, `bank_account_status`, `bank_account_id`, `plus`, `region`, `price`, `sell_method`, `two_step_enabled`, `is_deleted`
- **Schema:** `summary="Retrieve, update or delete a Sony account"`

---

### `PSNSonyAccountGameListCreateView`

- **URL:** `GET POST /psn/accounts/<int:account_pk>/games/`
- **View:** `ListCreateAPIView`
- **Model:** `psn.SonyAccountGame`
- **Filter:** `sony_account_id=account_pk`, `is_deleted=False`
- **Create logic (service):** `bulk_add_games_to_account(account_pk: int, game_ids: list[int]) -> list[SonyAccountGame]`
  - Accepts a list of `game_ids` in the request body
  - For each `game_id`:
    - Skip if `SonyAccountGame` already exists for this account+game (no error, just skip)
    - Create `SonyAccountGame(sony_account_id=account_pk, game_id=game_id)`
  - Return all created records
- **Serializer (list):** `id`, `game_id`, `game_title`, `game_main_img`, `is_deleted`
- **Serializer (create input):** `game_ids` (list of int, required)
- **Serializer (create output):** list of `{ id, game_id, game_title }`
- **Note:** Use `get_serializer_class` to switch between list and create serializers
- **Schema:** `summary="List or bulk-add games to a Sony account"`

---

### `PSNSonyAccountGameDetailView`

- **URL:** `GET DELETE /psn/accounts/<int:account_pk>/games/<int:pk>/`
- **View:** `RetrieveDestroyAPIView`
- **Model:** `psn.SonyAccountGame`
- **Filter:** `sony_account_id=account_pk`
- **Delete:** soft delete
- **Serializer fields:** `id`, `game_id`, `game_title`, `game_main_img`, `is_deleted`
- **Schema:** `summary="Retrieve or remove a game from a Sony account"`

---

### `PSNGameListView`

- **URL:** `GET /psn/games/`
- **View:** `ListAPIView`
- **Model:** `store.Game`
- **Filter:** `is_deleted=False`
- **Filter backends:** `SearchFilter`
- **Search fields:** `title`
- **Serializer fields:** `id`, `title`, `main_img`
- **Note:** Lightweight — only id, title, image. Used for game picker UI.
- **Schema:** `summary="List games (lightweight — id, title, image only)"`

---

### `PSNSonyAccountStatusListCreateView`

- **URL:** `GET POST /psn/account-statuses/`
- **View:** `ListCreateAPIView`
- **Model:** `psn.SonyAccountStatus`
- **Serializer fields:** `id`, `title`
- **Schema:** `summary="List or create Sony account statuses"`

---

### `PSNSonyAccountStatusDetailView`

- **URL:** `GET PUT PATCH DELETE /psn/account-statuses/<int:pk>/`
- **View:** `RetrieveUpdateDestroyAPIView`
- **Model:** `psn.SonyAccountStatus`
- **Serializer fields:** `id`, `title`
- **Schema:** `summary="Retrieve, update or delete a Sony account status"`

---

### `PSNSonyAccountCategoryListView`

- **URL:** `GET /psn/account-categories/`
- **View:** `ListAPIView`
- **Model:** `orders.SonyAccountOrderCategory`
- **Filter:** `is_deleted=False`
- **Serializer fields:** `id`, `title`, `type`, `rent_time_days`, `account_capacity`, `base_price`
- **Schema:** `summary="List Sony account order categories"`

---

### PSN URLs (`psn/urls.py`)

```python
from django.urls import path
from . import views

urlpatterns = [
    path("accounts/", views.PSNSonyAccountListCreateView.as_view()),
    path("accounts/<int:pk>/", views.PSNSonyAccountDetailView.as_view()),
    path("accounts/<int:account_pk>/games/", views.PSNSonyAccountGameListCreateView.as_view()),
    path("accounts/<int:account_pk>/games/<int:pk>/", views.PSNSonyAccountGameDetailView.as_view()),
    path("games/", views.PSNGameListView.as_view()),
    path("account-statuses/", views.PSNSonyAccountStatusListCreateView.as_view()),
    path("account-statuses/<int:pk>/", views.PSNSonyAccountStatusDetailView.as_view()),
    path("account-categories/", views.PSNSonyAccountCategoryListView.as_view()),
]
```

---

## PSN services.py

```python
from __future__ import annotations
from psn.models import SonyAccountGame

def bulk_add_games_to_account(account_pk: int, game_ids: list[int]) -> list[SonyAccountGame]: ...
```

---

## Important Notes for Claude Code

1. **Soft delete pattern** — override `perform_destroy` on every view that needs it:
   ```python
   def perform_destroy(self, instance) -> None:
       instance.is_deleted = True
       instance.save()
   ```

2. **Nested URL kwargs** — for views with `store_product_pk`, `game_pk`, `blog_pk`, `account_pk` in URL,
   override `get_queryset` to filter by the parent pk from `self.kwargs`.

3. **`BlogPostImage`** has no `is_deleted` — use hard delete for employee image endpoints.

4. **`Video`** has no `is_deleted` — use hard delete for employee video endpoint.

5. **`SonyAccountStatus`** — confirm this model exists in `psn/models.py` as a standalone model
   (referenced as FK on `SonyAccount.status`). If it's missing, create a minimal model with just `title`.

6. **`PSNSonyAccountListCreateView`** — two serializers, one method:
   ```python
   def get_serializer_class(self):
       if self.request.method == "POST":
           return SonyAccountCreateSerializer
       return SonyAccountListSerializer
   ```

7. **Bulk game add** — the service must use `SonyAccountGame.objects.get_or_create` to avoid
   `unique_together` integrity errors. Do NOT use `bulk_create` with `ignore_conflicts` here
   because we need the created instances returned.

8. **`EmployeeGameDetailView`** — reuse `get_game_account_stock(game_id)` service from Phase 1
   (`website/services.py`). Import it directly — do not duplicate.

9. **`EmployeeBlogListCreateView`** — `author` field should be read-only in response
   (set from `request.user.employee`, not from request body).

10. **`inventory.ProductCategory`** — confirm the import path is `from inventory.models import ProductCategory`.
    If `StoreProductCategory` in `store` is a separate model, use that instead and note the distinction.

11. **PyCharm warnings** — ensure all `perform_create` methods have correct return type hint `-> None`.