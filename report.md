# Architecture Conflict & Missing Parts Report

> Comparing `architecture-new-part.md` against the actual DrGame project state.
> Date: 2026-07-26

---

## CONFLICTS (Exists but Differs)

### 1. Wallet Model — Location & Structure Mismatch

| Aspect | Doc Says | Actual Project | what should be            | 
|---|---|---|---------------------------|
| App | `crm/models.py` | `accounting/models.py` | keep the accounting model |
| FK | `OneToOneField(Customer)` | `OneToOneField(CustomUser)` | keep the CustomUser relation |
| Balance type | `PositiveBigIntegerField` | `IntegerField` | change to big intiger |
| `is_active` | Yes | No | add the field |
| `WalletTransaction` | Proposed (full model) | **Does NOT exist** | add the model in accounting app |

**Impact:** Any code referencing `customer.wallet` will fail. Doc's atomic `WalletService` and `WalletTransaction` model are entirely missing.

---

### 2. OTP Storage — DB vs Redis

| Aspect | Doc Says | Actual Project | what should be |
|---|---|---|---|
| Storage | Redis (SHA256 hashed, TTL 120s) | DB (`users.models.OTP` model) | keep the current logic for now |
| Rate limiting | Redis key (`otp_attempts:{phone}`) | DRF `PhoneRateThrottle` | keep the current logic for now |
| OTP code length | 6 digits | 5 digits | keep the 5 digits |
| SMS sending | Always sent | **Commented out** (printed to console only) | keep the print for now |

**Impact:** Doc's Redis-based OTP service is not implemented. Current approach is DB-based.

---

### 3. `IsCustomer` Permission — Logic Bug

```python
# users/permissions.py — ACTUAL (BUGGY)
class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:   # <-- returns True unconditionally!
            return True
        return hasattr(request.user, 'customer') or ...  # dead code
```

Doc expects: `is_authenticated AND hasattr(request.user, 'customer') AND not customer.is_deleted`. Current code returns `True` for *any* authenticated user, even employees.
what should be : add the customer permission 

---

### 4. Blog Post Model — Duplicate Definitions

| Doc Proposes (`blog/models.py`) | Actually Exists (`website/models.py`) | what should be |
|---|---|---|
| `BlogPostCategory` | — | add the logic |
| `BlogPost` (FK to `hr.Employee`) | `BlogPost` (FK to `settings.AUTH_USER_MODEL`) | blog post to employee |
| `BlogPostImages` | — | add the model |
| Uses `ImageField` with specific paths | Uses `ImageField` with different paths | use a standard path |
| `is_published` boolean | `status` field (draft/published) | keep the status fields |

**Impact:** Two competing `BlogPost` definitions. The `blog` app scaffold exists but is empty.

---

### 5. URL Structure — No `/api/v1/` Prefix

Doc uses `/api/v1/auth/`, `/api/v1/customer/`, etc. Actual project uses direct prefixes: `/users/`, `/crm/`, `/orders/`. Inconsistency between doc's route paths and actual project conventions.
what should be : change the all urls for app_name/customer_panel or app_name/ first for customer or public views and second for the employee and manager panel
---

### 6. Admin Panel — All Bare-Bones

| Doc Proposes | Actual | what should be                                                                                     |
|---|---|----------------------------------------------------------------------------------------------------|
| Rich `CustomerAdmin` (wallet balance, inline, search) | Minimal (just `fields = "__all__"`) | we should add and wallet for employee and customer                                                 |
| `WalletAdmin` + `WalletTransactionAdmin` | **Don't exist** | we must add a management section for customer wallets and employee panels in management\employee panel |
| `TicketAdmin` + `TicketMessageInline` | **Don't exist** | add ticket for both side customer and employee\management                                          |                                                            
| `SonyAccountOrderCategoryAdmin` | **Not registered** | register it                                                                                        |                                                                                        |
| `ProductAdmin` with inline + editable fields | Exists but minimal | keep it minimal                                                                                    |                                                                                  |

---

### 7. CRM Views Architecture

Doc proposes `crm/views/profile.py`, `crm/views/wallet.py`, `crm/views/wishlist.py` (subdirectory). Actual project uses flat `crm/views.py`. Doc also splits serializers into subdirectory.
we must keep each part in its uniqe app and seperate by customer panel or nothing for employee panel
---

## MISSING (Not Implemented at All)

### Models

| Model | App (per doc) | Status | what should be |
|---|---|---|---|
| `WalletTransaction` | `crm` | **Missing** | add in accounting app |
| `CustomerWishlist` | `crm` | **Missing** | add in customer app |
| `Ticket` | `support` (new app) | **Missing** | add new app |
| `TicketMessage` | `support` (new app) | **Missing** | add new app |
| `BlogPostCategory` | `blog` | **Missing** | add in blog app |

### Customer-Facing API Endpoints

| Endpoint Group | Status | what should be|
|---|---|---|
| Store/Product public listing (`/store/`) | **Missing** — `e_commerce` is empty scaffold; `website` URLs disabled | we must merge the website and e_commerce apps to one app website sounds good|
| Customer Profile (`/customer/profile/`) | **Missing** — existing `crm` views are employee/admin-oriented | we must add customer orented views for customer not only on this section but everywhere we need |
| Customer Orders (`/customer/orders/`) | **Missing** — existing `orders` views are worker-panel only | add customer oriented |
| Wallet API (`/customer/wallet/`) | **Missing** — `Wallet` model exists but no endpoints | we most add bussines logic and endpoints |
| Wishlist API (`/customer/wishlist/`) | **Missing** | we must add apis |
| Support Tickets API (`/customer/tickets/`) | **Missing** | we must add api |
| Blog API (`/blog/`) | **Missing** — `blog` app is empty; `website` has BlogPost model but no endpoints | we must handle the blog in blog app |

### Services & Business Logic

| Service | Status | what should be |
|---|---|---|
| `WalletService.charge()` with `select_for_update()` | **Missing** | adding the logic |
| `WalletService.debit()` with balance check | **Missing** | adding the logic |
| Redis-based OTP send/verify service | **Missing** (uses DB instead) | use db for now |
| Payment gateway integration (charge flow) | **Missing** | keep it simple wihout real payment portal |
| Post-save signal to auto-create Wallet for Customer | **Missing** | add it |
| Product list Redis caching (TTL 300s) | **Missing** | add it |
| Wallet balance Redis caching (TTL 60s) | **Missing** | add it |
| Customer profile Redis caching (TTL 600s) | **Missing** | add it |

### Permission Classes

| Class | Status | what should be |
|---|---|---|
| `IsCustomerOrReadOnly` | **Missing** | add it |
| `IsTicketOwner` | **Missing** | add it |

### Admin Configuration

| Admin | Status | what should be |
|---|---|---|
| `WalletAdmin` (with charge action) | **Missing** | add it |
| `WalletTransactionAdmin` (read-only) | **Missing** | add it |
| `TicketAdmin` (with inline messages) | **Missing** | add it |
| `SonyAccountOrderCategoryAdmin` | **Missing** | add it |
| `CustomerAdmin` enhancements (wallet balance, search) | **Needs work** | add it |

### New Apps

| App | Status | what should be |
|---|---|---|
| `support` | **Does not exist** | add it |
| `store` (view-only, uses inventory models) | **Does not exist** | add it on website app |
| `blog` | Exists as empty scaffold, **not in INSTALLED_APPS** | add it |

### Other Missing Items

- `@extend_schema` decorators on views (doc requires them, not consistently used)
- Conditional `items` display in Sony orders (hide until final stage)
- `is_in_wishlist` field in product serializers (requires wishlist model)
- `messenger` and `website` URLs are commented out in `DrGame/urls.py`
- we must add or fix every unstandard parts and make it standard 
---

## ALREADY MATCHING (No Action Needed)

| Item | Status |
|---|---|
| `CustomUser` (phone as USERNAME_FIELD) | ✓ Matches |
| `Customer` model (address, postal_code, profile_pic) | ✓ Matches |
| `B2BProfile` model | ✓ Matches |
| OTP Auth endpoints (`request-otp`, `verify-otp`, `refresh-token`, `logout`) | ✓ Implemented |
| JWT tokens in HTTP-only cookies | ✓ Implemented via `CustomJWTAuthentication` |
| `ProductOrder`, `SonyAccountOrder`, `RepairOrder` models | ✓ Exist in `orders` app |
| `Product`, `ProductCategory` | ✓ Exist in `inventory` |
| `SonyAccountOrderCategory` | ✓ Exist in `orders` |
| `Invoice` model | ✓ Exist in `accounting` |
| Soft delete (`is_deleted` on all models) | ✓ Consistent |
| `IsCustomer`, `IsEmployee`, `IsMainManager` permission classes | ✓ Exist |
| Redis cache backend via `django_redis` | ✓ Configured |
| ContentType/GenericForeignKey usage | ✓ Used in `accounting.AccountSide` + `InvoiceItem` |

---

## Summary

- **Conflicts**: 7 areas (Wallet location/structure, OTP storage, IsCustomer bug, Blog duplicate, URL prefix, admin minimalism, CRM file structure)
- **Missing models**: 5 (WalletTransaction, CustomerWishlist, Ticket, TicketMessage, BlogPostCategory)
- **Missing endpoints**: 7 endpoint groups (Store, Profile, Orders, Wallet, Wishlist, Tickets, Blog)
- **Missing services**: 9 (WalletService, Redis OTP, Payment gateway, caching layer, signals)
- **Missing admin configs**: 5 (Wallet, WalletTransaction, Ticket, SonyOrderCategory, Customer enhancements)
- **New apps needed**: 2 (support, store)
- **Already matching**: 15 items
