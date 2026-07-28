# DrGame — Website App: open Code Implementation Guide

## Project Context

You are implementing the `website` Django app for the DrGame ERP backend.
This app serves two audiences in a single set of files (`views.py`, `serializers.py`, `urls.py`),
separated by comment sections and `drf-spectacular` tags.

---

## Conventions (Non-Negotiable)

| Rule | Detail |
|---|---|
| Views | `rest_framework.generics.*` only — no `ModelViewSet`, no `APIView` |
| Schema | Every view must have `@extend_schema(tags=[...], summary="...")` |
| Permission | `IsCustomer` imported from `users.permissions` |
| Serializers | Every view has its own serializer — no reuse across different endpoints |
| Services | Any repeated business logic goes in `website/services.py` |
| Filters | Use `django_filters.rest_framework.DjangoFilterBackend` |
| Search | Use `rest_framework.filters.SearchFilter` |
| No cache | Do not add caching — it will be added later |
| Clean code | No warnings, no unused imports, full type hints on service functions |

---

## File Structure

```
website/
├── views.py
├── serializers.py
├── urls.py
├── services.py
├── filters.py
└── apps.py
```

---

## Implementation: Two Phases

---

## Phase 1 — Customer Section

All views in this phase use `permission_classes = [IsCustomer]`.

Inside `views.py` and `serializers.py`, wrap each section with a clear comment block:

```python
# ============================================================
# CUSTOMER SECTION — HOME / LANDING
# ============================================================
```

---

### Section 1: Home / Landing

**Tag:** `"Website — Customer: Home"`

---

#### 1.1 `HomeBannerListView`

- **URL:** `GET /banners/`
- **View:** `ListAPIView`
- **Model:** `store.HomeBanner`
- **Filter:** only `is_chosen=True`, ordered by `order`
- **Serializer fields:** `id`, `title`, `image`, `order`
- **Schema:** `summary="List active home banners"`

---

#### 1.2 `HomeSectionListView`

- **URL:** `GET /sections/`
- **View:** `ListAPIView`
- **Model:** `store.HomeSection`
- **Filter:** `is_deleted=False`
- **Serializer fields:** `id`, `title`, `model_content`
- **Schema:** `summary="List home sections"`

---

#### 1.3 `HomeSectionItemListView`

- **URL:** `GET /section-items/`
- **View:** `ListAPIView`
- **Model:** `store.HomeSectionItem`
- **Query param:** `section_id` (required — filter by `section_id`, raise `ValidationError` if missing)
- **Filter:** `is_deleted=False`, `is_active=True`
- **Business logic (service):** For each item, resolve the real object based on `section.model_content`:
  - `"game"` → fetch `store.Game` by `item.item_id`
  - `"product"` → fetch `store.StoreProduct` by `item.item_id`
  - `"blog"` → fetch `store.BlogPost` by `item.item_id`
  - Return fields: `item_id`, `item_title`, `item_description`, `item_image`, `item_type`
  - (These four commented fields in the model must be resolved dynamically from the related object)
- **Service function:** `resolve_section_items(items: QuerySet) -> list[dict]` in `services.py`
- **Serializer:** takes the resolved list from the service
- **Schema:** `summary="List items for a home section"`

---

#### 1.4 `AboutUsListView`

- **URL:** `GET /about-us/`
- **View:** `ListAPIView`
- **Model:** `store.AboutUs`
- **Filter:** `is_deleted=False`, `is_active=True`
- **Serializer fields:** `id`, `title`, `logo`, `phone_number`, `email`, `address`, `e_namaad`, `e_namaad_url`
- **Schema:** `summary="List AboutUs objects"`

---

### Section 2: Product Store

**Tag:** `"Website — Customer: Product Store"`

---

#### 2.1 `StoreProductSearchView`

- **URL:** `GET /products/search/`
- **View:** `ListAPIView`
- **Model:** `store.StoreProduct`
- **Filter backends:** `SearchFilter`
- **Search fields:** `title`, `product__title`, `product__description`, `product__category__title`
- **Filter:** `is_deleted=False`
- **Serializer fields:** `id`, `title`, `product_id`, `product_title`, `product_main_img`
- **Schema:** `summary="Search store products"`

---

#### 2.2 `StoreProductListView`

- **URL:** `GET /products/`
- **View:** `ListAPIView`
- **Model:** `store.StoreProduct`
- **Filter backends:** `DjangoFilterBackend`
- **Filterset:** `StoreProductFilter` in `filters.py`
  - Filterable fields: `product__category` (exact), `product__price` (range: `min_price`, `max_price`), `product__stock` (gt 0 as boolean `in_stock`)
- **Filter:** `is_deleted=False`
- **Serializer fields:** `id`, `title`, `product_id`, `product_title`, `product_main_img`, `product_price`, `product_stock`
- **Schema:** `summary="List store products with filters"`

---

#### 2.3 `StoreProductDetailView`

- **URL:** `GET /products/<int:pk>/`
- **View:** `RetrieveAPIView`
- **Model:** `store.StoreProduct`
- **Business logic (service):** `get_product_entity_info(product_id: int) -> dict`
  - Queries `inventory.ProductEntity` where `product_id=product.id`, `is_deleted=False`
  - Returns:
    - `stock_count`: total count of available entities
    - `available_colors`: distinct list of non-null `color` values
- **Serializer fields:**
  - From `StoreProduct`: `id`, `title`
  - From nested `Product`: `id`, `title`, `main_img`, `description`, `price`, `category_id`, `category_title`
  - From service: `stock_count`, `available_colors`
- **Schema:** `summary="Retrieve store product detail with stock and color info"`

---

#### 2.4 `StoreProductImageListView`

- **URL:** `GET /products/images/`
- **View:** `ListAPIView`
- **Model:** `store.StoreProductImage`
- **Query param:** `store_product_id` (required — raise `ValidationError` if missing)
- **Filter:** `is_deleted=False`, filtered by `product_id=store_product_id`
- **Serializer fields:** `id`, `img`, `product_id`
- **Schema:** `summary="List images for a store product"`

---

### Section 3: Game Store

**Tag:** `"Website — Customer: Game Store"`

---

#### 3.1 `GameSearchView`

- **URL:** `GET /games/search/`
- **View:** `ListAPIView`
- **Model:** `store.Game`
- **Filter backends:** `SearchFilter`
- **Search fields:** `title`, `description`, `category__title`
- **Filter:** `is_deleted=False`
- **Serializer fields:** `id`, `title`, `main_img`, `category_id`, `category_title`
- **Schema:** `summary="Search games"`

---

#### 3.2 `GameListView`

- **URL:** `GET /games/`
- **View:** `ListAPIView`
- **Model:** `store.Game`
- **Filter backends:** `DjangoFilterBackend`
- **Filterset:** `GameFilter` in `filters.py`
  - Filterable fields: `category` (exact), `volume` (range: `min_volume`, `max_volume`)
- **Filter:** `is_deleted=False`
- **Serializer fields:** `id`, `title`, `main_img`, `description`, `volume`, `units_sold`, `category_id`, `category_title`
- **Schema:** `summary="List games with filters"`

---

#### 3.3 `GameDetailView`

- **URL:** `GET /games/<int:pk>/`
- **View:** `RetrieveAPIView`
- **Model:** `store.Game`
- **Business logic (service):** `get_game_account_stock(game_id: int) -> int`
  - Queries `psn.SonyAccountGame` where `game_id=game_id`, `is_deleted=False`
  - Returns count of available sony accounts linked to this game
- **Serializer fields:** `id`, `title`, `main_img`, `description`, `volume`, `units_sold`, `category_id`, `category_title`, `account_stock`
- **Schema:** `summary="Retrieve game detail with sony account stock count"`

---

#### 3.4 `GameImageListView`

- **URL:** `GET /games/images/`
- **View:** `ListAPIView`
- **Model:** `store.GameImage`
- **Query param:** `game_id` (required — raise `ValidationError` if missing)
- **Filter:** `is_deleted=False`, filtered by `game_id`
- **Serializer fields:** `id`, `img`, `game_id`
- **Schema:** `summary="List images for a game"`

---

### Section 4: Product Cart

**Tag:** `"Website — Customer: Product Cart"`

All views in this section require an authenticated customer (`IsCustomer`).
The cart is always resolved via `ProductCart.objects.get_or_create(user=request.user.customer)`.

---

#### 4.1 `ProductCartDetailView`

- **URL:** `GET /cart/product/`
- **View:** `RetrieveAPIView`
- **Logic:** get or create `ProductCart` for the logged-in customer
- **Serializer fields:**
  - `id`, `created_at`
  - `items`: nested list — each item: `id`, `product_id`, `store_product_id`, `store_product_title`, `product_title`, `product_main_img`, `unit_price`, `quantity`, `total_item_price`, `color`
  - `total_price`: from `ProductCart.total_price` property
  - `item_count`: total number of items
- **Schema:** `summary="Get full product cart with totals"`

---

#### 4.2 `ProductCartItemListView`

- **URL:** `GET /cart/product/items/`
- **View:** `ListAPIView`
- **Logic:** filter `ProductCartItem` by `cart__user=request.user.customer`, `is_deleted=False`
- **Serializer fields:** `id`, `product_id`, `product_title`, `quantity`, `total_item_price`, `color`
- **Schema:** `summary="List items in the customer's product cart"`

---

#### 4.3 `ProductCartAddItemView`

- **URL:** `POST /cart/product/add/`
- **View:** `CreateAPIView` (override `create` method)
- **Body:** `store_product_id` (int, required), `color` (str, optional)
- **Business logic (service):** `add_product_to_cart(customer, store_product_id: int, color: str | None) -> ProductCartItem`
  - Get or create `ProductCart` for customer
  - Get `StoreProduct` by `store_product_id` — raise `NotFound` if missing or deleted
  - If `ProductCartItem` with that `product` already exists in cart:
    - increment `quantity` by 1, update `color` if provided
  - Else:
    - create new `ProductCartItem` with `quantity=1`
  - Return the item
- **Serializer:** input fields: `store_product_id`, `color` — output fields: `id`, `product_id`, `quantity`, `color`
- **Schema:** `summary="Add product to cart or increment quantity"`

---

#### 4.4 `ProductCartRemoveItemView`

- **URL:** `DELETE /cart/product/remove/`
- **View:** `DestroyAPIView` (override `destroy` method)
- **Query param:** `store_product_id` (int, required)
- **Business logic (service):** `remove_product_from_cart(customer, store_product_id: int) -> None`
  - Get `ProductCart` for customer — raise `NotFound` if none
  - Get `ProductCartItem` for that product — raise `NotFound` if none
  - If `quantity > 1`: decrement by 1
  - If `quantity == 1`: delete the item
- **Schema:** `summary="Remove product from cart or decrement quantity"`

---

### Section 5: Game Cart

**Tag:** `"Website — Customer: Game Cart"`

All views in this section require an authenticated customer (`IsCustomer`).
The cart is always resolved via `GameCart.objects.get_or_create(user=request.user.customer)`.

---

#### 5.1 `GameCartDetailView`

- **URL:** `GET /cart/game/`
- **View:** `RetrieveAPIView`
- **Logic:** get or create `GameCart` for the logged-in customer
- **Serializer fields:**
  - `id`, `created_at`
  - `games`: nested list — each item: `id`, `game_id`, `game_title`, `game_main_img`, `game_volume`
  - `total_volume`: sum of all `game.volume` values in the cart (in GB)
  - `volume_flag`: computed from `total_volume`:
    - `"< 500GB"` if total < 500
    - `"> 500GB"` if 500 ≤ total < 1024
    - `"> 1TB"` if total ≥ 1024
- **Schema:** `summary="Get full game cart with volume info"`

---

#### 5.2 `MatchedSonyAccountListView`

- **URL:** `GET /cart/game/matched-accounts/`
- **View:** `ListAPIView`
- **Business logic (service):** `get_matched_sony_accounts(customer) -> QuerySet`
  - Get all `game_id`s from the customer's `GameCart` items
  - If cart is empty, return empty queryset
  - Find `SonyAccount`s where:
    - `is_deleted=False`
    - They have **at least (total_games - 2)** matching games from the cart
    - Annotate each account with `match_count` = number of cart games found in their `games`
    - Filter: `match_count >= max(total_games - 2, 1)`
    - Order by `match_count` descending
- **Serializer fields:** `id`, `username`, `price`, `plus`, `region`, `status_id`, `status_title`, `match_count`
- **Schema:** `summary="List sony accounts matching customer game cart"`

---

#### 5.3 `GameCartVolumeView`

- **URL:** `GET /cart/game/volume/`
- **View:** `RetrieveAPIView` (override `get_object` to return computed dict)
- **Business logic (service):** `get_cart_volume_info(customer) -> dict`
  - Aggregate total volume of all games in the customer's `GameCart`
  - Compute flag:
    - `"< 500GB"` if total < 500
    - `"> 500GB"` if 500 ≤ total < 1024
    - `"> 1TB"` if total ≥ 1024
  - Return: `{ "total_volume": int, "volume_flag": str }`
- **Serializer fields:** `total_volume`, `volume_flag`
- **Schema:** `summary="Get total volume and size flag for game cart"`

---

#### 5.4 `GameCartAddItemView`

- **URL:** `POST /cart/game/add/`
- **View:** `CreateAPIView` (override `create`)
- **Body:** `game_id` (int, required)
- **Business logic (service):** `add_game_to_cart(customer, game_id: int) -> GameCartItem`
  - Get or create `GameCart` for customer
  - Get `Game` by `game_id` — raise `NotFound` if missing or deleted
  - If `GameCartItem` with that game already exists → raise `ValidationError("Game already in cart")`
  - Else: create `GameCartItem`
- **Serializer:** input: `game_id` — output: `id`, `game_id`, `game_title`
- **Schema:** `summary="Add game to game cart"`

---

#### 5.5 `GameCartRemoveItemView`

- **URL:** `DELETE /cart/game/remove/`
- **View:** `DestroyAPIView` (override `destroy`)
- **Query param:** `game_id` (int, required)
- **Business logic (service):** `remove_game_from_cart(customer, game_id: int) -> None`
  - Get `GameCart` for customer — raise `NotFound` if none
  - Get `GameCartItem` by `game_id` — raise `NotFound` if not in cart
  - Delete the item
- **Schema:** `summary="Remove game from game cart"`

---

## services.py — Full Function List

Implement all of these in `website/services.py` with full type hints:

```python
from __future__ import annotations
from django.db.models import QuerySet, Count

def resolve_section_items(items: QuerySet) -> list[dict]: ...
def get_product_entity_info(product_id: int) -> dict: ...
def get_game_account_stock(game_id: int) -> int: ...
def add_product_to_cart(customer, store_product_id: int, color: str | None): ...
def remove_product_from_cart(customer, store_product_id: int) -> None: ...
def get_matched_sony_accounts(customer) -> QuerySet: ...
def get_cart_volume_info(customer) -> dict: ...
def add_game_to_cart(customer, game_id: int): ...
def remove_game_from_cart(customer, game_id: int) -> None: ...
```

---

## filters.py — Filtersets

```python
# StoreProductFilter
# fields: product__category (exact), min_price / max_price (product__price range), in_stock (boolean → product__stock__gt=0)

# GameFilter
# fields: category (exact), min_volume / max_volume (volume range)
```

---

## urls.py Pattern

```python
from django.urls import path
from . import views

urlpatterns = [
    # --- Home ---
    path("banners/", views.HomeBannerListView.as_view()),
    path("sections/", views.HomeSectionListView.as_view()),
    path("section-items/", views.HomeSectionItemListView.as_view()),
    path("about-us/", views.AboutUsListView.as_view()),

    # --- Product Store ---
    path("products/search/", views.StoreProductSearchView.as_view()),
    path("products/", views.StoreProductListView.as_view()),
    path("products/<int:pk>/", views.StoreProductDetailView.as_view()),
    path("products/images/", views.StoreProductImageListView.as_view()),

    # --- Game Store ---
    path("games/search/", views.GameSearchView.as_view()),
    path("games/", views.GameListView.as_view()),
    path("games/<int:pk>/", views.GameDetailView.as_view()),
    path("games/images/", views.GameImageListView.as_view()),

    # --- Product Cart ---
    path("cart/product/", views.ProductCartDetailView.as_view()),
    path("cart/product/items/", views.ProductCartItemListView.as_view()),
    path("cart/product/add/", views.ProductCartAddItemView.as_view()),
    path("cart/product/remove/", views.ProductCartRemoveItemView.as_view()),

    # --- Game Cart ---
    path("cart/game/", views.GameCartDetailView.as_view()),
    path("cart/game/matched-accounts/", views.MatchedSonyAccountListView.as_view()),
    path("cart/game/volume/", views.GameCartVolumeView.as_view()),
    path("cart/game/add/", views.GameCartAddItemView.as_view()),
    path("cart/game/remove/", views.GameCartRemoveItemView.as_view()),
]
```
this urls must have name= field to 
---

## Important Notes for open Code

1. **Import paths:**
   - `from users.permissions import IsCustomer`
   - `from website.models import HomeBanner, HomeSection, HomeSectionItem, AboutUs, StoreProduct, StoreProductImage, Game, GameImage, GameCart, GameCartItem, ProductCart, ProductCartItem`
   - `from inventory.models import ProductEntity`
   - `from psn.models import SonyAccount, SonyAccountGame`

2. **`HomeSectionItem` resolution:** The four commented fields (`item_title`, `item_description`, `item_image`, `item_type`) are NOT on the model — they must be resolved by fetching the related object from `Game`, `StoreProduct`, or `BlogPost` based on `section.model_content`.

3. **`ProductCart.total_price`** is a property on the model — use it directly, do not recalculate.

4. **Matched accounts query** must use `annotate(match_count=Count(...))` with a filter on the annotated field — do not use Python-level filtering.

5. **Volume flag** logic is shared between `GameCartDetailView` and `GameCartVolumeView` — extract it into `get_cart_volume_info` service and call it from both views.

6. **No bare `except` clauses.** Use specific exceptions: `ObjectDoesNotExist`, `ValidationError`, `NotFound`.

7. **Every serializer** must be a standalone class — no inline serializers, no anonymous `serializers.Serializer()` instances.

8. **PyCharm warnings:** ensure all imports are used, all variables are assigned before use, and no shadowing of built-ins.