# DrGame — Customer Interface Implementation Tasks

> Based on `architecture-new-part.md` and `report.md`.
> Phase structure adapted from architecture doc §۱۳ with "what should be" decisions.

---

## Phase 0 — Fixes & Housekeeping

### 0.1 Fix `IsCustomer` Permission Bug
- **File:** `users/permissions.py`
- **What:** Fix logic to check `is_authenticated AND hasattr(request.user, 'customer') AND not request.user.customer.is_deleted`
- **Why:** Currently returns `True` for any authenticated user (even employees)

### 0.2 Enhance Wallet Model
- **File:** `accounting/models.py`
- **What:**
  - Change `balance` from `IntegerField` → `BigIntegerField`
  - Add `is_active = BooleanField(default=True)`
- **Why:** Align with architecture spec

### 0.3 URL Structure Refactoring
- **File:** `DrGame/urls.py` + per-app `urls.py`
- **What:** Restructure URLs so each app has separate prefixes:
  - `/{app_name}/` for customer/public-facing views
  - `/{app_name}/management/` or `/{app_name}/employee/` for employee/manager views
- **Why:** Clean separation of customer vs internal interfaces

### 0.4 Register `SonyAccountOrderCategory` in Admin
- **What:** Add `SonyAccountOrderCategoryAdmin` to `orders/admin.py`

---

## Phase 1 — Foundation (Models, Services, Cache)

### 1.1 Create `WalletTransaction` Model
- **File:** `accounting/models.py`
- **What:** Add `WalletTransaction` model with:
  - FK to `Wallet`, `type` (charge_admin, charge_gateway, debit_order, refund), `amount`, `status` (pending, success, failed, cancelled), `description`
  - Gateway fields: `gateway_ref`, `gateway_name`
  - Generic FK for order relation: `order_content_type`, `order_object_id`
  - `performed_by` FK to `hr.Employee` (nullable)
  - Audit trail: `balance_before`, `balance_after`
  - `created_at`, `is_deleted`
  - Meta: `ordering = ['-created_at']`

### 1.2 Create `WalletService`
- **File:** `accounting/services.py` (new)
- **What:** Atomic wallet operations using `select_for_update()`:
  - `WalletService.charge(wallet, amount, type_, **kwargs)` — increase balance + create transaction
  - `WalletService.debit(wallet, amount, description, order_ct, order_id)` — check balance, decrease + create transaction
  - Both wrapped in `@db_transaction.atomic`

### 1.3 Add `post_save` Signal for Wallet Auto-Creation
- **File:** `accounting/signals.py` (new) + `accounting/apps.py`
- **What:** Auto-create `Wallet` for every new `CustomUser` via `post_save` signal

### 1.4 Add Redis Caching
- **What:** Implement caching per architecture doc §۱۰:
  - Product list cache (TTL 300s)
  - Wallet balance cache (TTL 60s, invalidate on transaction)
  - Customer profile cache (TTL 600s, invalidate on update)
  - Category list cache (TTL 3600s)
- **Where:** Use existing `django_redis` setup

### 1.5 Create `CustomerWishlist` Model
- **File:** `crm/models.py`
- **What:** `CustomerWishlist` with:
  - FK to `Customer`, Generic FK to `Product` or `Game`
  - `created_at`, `is_deleted`
  - `unique_together = ('customer', 'content_type', 'object_id')`
  - Index on `(customer, content_type)`

### 1.6 Create `support` App
- **Files:** `support/models.py`, `support/admin.py`, `support/views.py`, `support/serializers.py`, `support/urls.py`
- **Add** `support` to `INSTALLED_APPS` in `DrGame/settings.py`
- **Models:**
  - `Ticket` — FK to `crm.Customer`, assigned_to (`hr.Employee`), title, category (order/payment/account/general), status (open/in_progress/waiting/closed), priority (low/medium/high), optional order Generic FK, `closed_at`
  - `TicketMessage` — FK to `Ticket`, sender_type (customer/employee/system), sender_customer/sender_employee, body, attachment, `is_internal` (hidden from customer)

### 1.7 Activate & Populate `blog` App
- **Files:** `blog/models.py`, `blog/admin.py`, `blog/views.py`, `blog/serializers.py`, `blog/urls.py`
- **Add** `blog` to `INSTALLED_APPS`
- **Models:**
  - `BlogPostCategory` — title, description
  - Migrate `BlogPost` from `website/models.py` → `blog/models.py` (update FK to `hr.Employee`)
  - `BlogPostImages` — FK to `BlogPost`, `ImageField`
- **Note:** Remove or deprecate `BlogPost` from `website/models.py`

---

## Phase 2 — Store & Customer Profile

### 2.1 Merge `website` + `e_commerce` → `website`
- **What:** Consolidate both apps into `website` (the active app). Move any e_commerce logic into website
- **Remove** `e_commerce` from project if empty

### 2.2 Create Public Store Endpoints
- **URL prefix:** `/website/store/`
- **Endpoints:**
  - `GET /website/store/products/` — list products (filter: category, search, price range, in_stock, ordering)
  - `GET /website/store/products/{id}/` — product detail
  - `GET /website/store/products/{id}/images/` — product images
  - `GET /website/store/categories/` — category list
  - `GET /website/store/games/` — game categories (for Sony accounts)
  - `GET /website/store/games-category/` — game category list
- **Response fields:** id, title, main_img, price, stock, category_id, category_title, `is_in_wishlist` (null if unauthenticated)
- **Caching:** Cache product list in Redis (TTL 300s)
- **Permissions:** `AllowAny` for reads

### 2.3 Create Customer Profile Endpoints
- **URL prefix:** `/customer/`
- **Endpoints:**
  - `GET /customer/profile/` — profile detail (phone, name, address, postal_code, profile_pic, wallet_balance, is_b2b)
  - `PATCH /customer/profile/` — update profile
  - `POST /customer/profile/pic/` — upload profile picture
- **Permissions:** `IsAuthenticated` + `IsCustomer` (fixed)

### 2.4 Create Wishlist Endpoints
- **URL prefix:** `/customer/wishlist/`
- **Endpoints:**
  - `GET /customer/wishlist/` — list wishlist items
  - `POST /customer/wishlist/` — add item
  - `DELETE /customer/wishlist/{id}/` — remove item
  - `POST /customer/wishlist/toggle/` — toggle (add/remove)
- **Permissions:** `IsAuthenticated` + `IsCustomer`

---

## Phase 3 — Orders & Wallet

### 3.1 Create Customer Order Endpoints
- **URL prefix:** `/customer/orders/`
- **Endpoints:**
  - `GET /customer/orders/` — list all my orders (filter: type=product|sony|repair, status, date range)
  - `GET /customer/orders/products/` — my product orders
  - `GET /customer/orders/products/{id}/` — product order detail
  - `POST /customer/orders/products/` — create product order
  - `GET /customer/orders/sony/` — my Sony account orders
  - `GET /customer/orders/sony/{id}/` — Sony order detail (items hidden until final stage)
  - `POST /customer/orders/sony/` — create Sony order
  - `GET /customer/orders/repair/` — my repair orders
  - `GET /customer/orders/repair/{id}/` — repair order detail
  - `POST /customer/orders/repair/` — create repair order
- **Permissions:** `IsAuthenticated` + `IsCustomer`
- **Serializers:** Use `select_related`/`prefetch_related` for performance
- **Stage logs:** Expose only `stage_logs`, hide internal `action_logs` and employee info

### 3.2 Create Wallet Endpoints
- **URL prefix:** `/customer/wallet/`
- **Endpoints:**
  - `GET /customer/wallet/` — balance + last 5 transactions
  - `GET /customer/wallet/transactions/` — full transaction history
  - `POST /customer/wallet/charge/` — request online charge (no real payment gateway, simulate)
- **Callback:** `/accounting/payment/verify/` — payment gateway callback endpoint
- **Permissions:** `IsAuthenticated` + `IsCustomer`

### 3.3 Payment Gateway (Simple / Mock)
- **What:** Implement a simplified charge flow without connecting to a real payment portal
- Simulate successful payment on callback
- Create `WalletTransaction` with `type='charge_gateway'` and `status='success'`

---

## Phase 4 — Support & Admin Enhancement

### 4.1 Create Support Ticket Endpoints
- **URL prefix:** `/customer/tickets/`
- **Endpoints:**
  - `GET /customer/tickets/` — list my tickets
  - `GET /customer/tickets/{id}/` — ticket detail + messages
  - `POST /customer/tickets/create/` — create ticket with initial message
  - `POST /customer/tickets/{id}/reply/` — add message to ticket
  - `GET /customer/tickets/{id}/messages/` — ticket messages
- **Permissions:** `IsAuthenticated` + `IsCustomer` + `IsTicketOwner` (object-level)
- **Filter:** Never expose messages with `is_internal=True`

### 4.2 Create Employee/Manager Ticket Views
- **URL prefix:** `/support/` or `/hr/support/`
- **Endpoints:**
  - List all tickets (filter by status, priority, category)
  - Assign ticket to employee
  - Change ticket status
  - View/add internal notes (`is_internal=True`)
- **Permissions:** Employee with support module access

### 4.3 Enhance Customer Admin
- **File:** `crm/admin.py`
- **What:**
  - Add `list_display`: id, phone, full_name, wallet_balance, is_deleted
  - Add `search_fields`: phone, first_name, last_name
  - Add `WalletInline` to show wallet info

### 4.4 Add Wallet Admin
- **File:** `accounting/admin.py`
- **What:**
  - `WalletAdmin` — list display (customer, balance, is_active), readonly balance, custom action for manual charge (admin top-up)
  - `WalletTransactionAdmin` — list display (id, wallet, type, amount, status, created_at), list filter (type, status), all fields readonly, no delete/change permission

### 4.5 Add Ticket Admin
- **File:** `support/admin.py`
- **What:**
  - `TicketAdmin` — list display (id, title, customer, category, status, priority, assigned_to), list filter (status, priority, category), inline TicketMessage
  - Auto-set `closed_at` when status changes to 'closed'

### 4.6 Register `SonyAccountOrderCategoryAdmin`
- **File:** `orders/admin.py`
- **What:** Simple admin with list and editable `is_deleted`

---

## Phase 5 — Blog

### 5.1 Complete Blog App
- **URL prefix:** `/blog/`
- **Endpoints:**
  - `GET /blog/posts/` — published posts list
  - `GET /blog/posts/{slug}/` — post detail
- **Admin:** BlogPost admin with publish management
- **Permissions:** `AllowAny` for reads (public)

### 5.2 Blog Post Migrations
- Migrate existing data from `website.BlogPost` to `blog.BlogPost`
- Update FK from `settings.AUTH_USER_MODEL` to `hr.Employee`
- Deprecate/remove `website.BlogPost`

---

## Cross-Cutting Concerns

### Permission Classes (New)
- **File:** `users/permissions.py` or `core/permissions.py`
- **Add:**
  - `IsCustomerOrReadOnly` — full access for customers, read-only for anonymous
  - `IsTicketOwner` — object-level: only ticket owner can access

### `@extend_schema` Decorators
- All new views must include `@extend_schema` with proper request/response documentation

### Soft Delete Compliance
- All new querysets must filter `is_deleted=False`
- All new models must include `is_deleted` field

### Coding Standards
- Use DRF `generics.*` (no ViewSets)
- Use `LimitOffsetPagination` with `PAGE_SIZE=10`
- Use `django-filter` with custom `FilterSet` classes
- `select_related`/`prefetch_related` on all list/detail views
