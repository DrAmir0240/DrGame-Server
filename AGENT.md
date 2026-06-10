# Project Overview

- Confirmed behavior: this repository is a Django REST backend for a game/e-commerce/service business called DrGame. It manages OTP-based login, customers, employees, repairmen, product sales, game-account orders, repair orders, course purchases, internal chat, Sony-account inventory, documents, and real assets (`DrGame/urls.py`, `accounts/views.py`, `customers/views.py`, `employees/views.py`, `home/views.py`, `payments/views.py`, `messenger/views.py`, `storage/models.py`).
- Confirmed behavior: the public-facing surface is mostly JSON APIs, plus OpenAPI/Swagger docs; there are no custom templates, no frontend source tree, and no active server-rendered pages beyond Django admin/docs plumbing (`DrGame/urls.py`, `DrGame/settings.py`).
- Confirmed behavior: the business domain combines three lines of work: physical product sales, digital/game-order fulfillment using Sony accounts, and console repair operations; a fourth line is paid course access (`payments/models.py`, `home/models.py`, `storage/models.py`).
- Confirmed behavior: the high-level architecture is a single Django project with app-level separation by domain: identity/accounts, customers, employees/operations, home/storefront content, payments/orders, messenger, storage/inventory, and utils/integrations (`DrGame/settings.py`).
- Inferred from implementation naming and status enums: internal staff appear to process customer-submitted game and repair orders through staged workflows, while customer balances and payment-method balances act as internal ledgers in addition to online Zarinpal payments (`payments/models.py`, `payments/views.py`, `employees/serializers.py`, `employees/views.py`).

# Tech Stack

- Python version: the checked-in virtualenv is Python 3.12, and the project imports are compatible with that runtime (`venv/pyvenv.cfg`).
- Django version: `Django==5.2.3` (`requirements.txt`).
- Major libraries: Django REST Framework, SimpleJWT, django-filter, drf-spectacular, django-cors-headers, django-redis, django-storages, boto3, cryptography/Fernet, pyotp, requests, celery, channels, channels_redis (`requirements.txt`).
- Infrastructure dependencies configured in code: PostgreSQL via `dj_database_url`, Redis cache, S3-compatible object storage (Liara), Faraz/IPPanel SMS, Zarinpal payment gateway, Telegram Bot API (`DrGame/settings.py`, `accounts/models.py`, `payments/models.py`, `utils/telegram.py`).
- Deployment style confirmed in repo: no Docker, Compose, Procfile, CI pipeline, Gunicorn, Nginx, or Kubernetes manifests are present in-repo. Runtime assumptions are therefore only partially observable from code and `.env` (`find` inventory, `DrGame/settings.py`, `.env`).
- Async/task systems: Celery and Channels are installed but there are no Celery app modules, tasks, consumers, routing modules, or signal-driven background flows in the repository (`requirements.txt`; grep across repo for `shared_task`, `Celery`, `ProtocolTypeRouter`, `Consumer`).
- API technologies: DRF generic views/APIViews, cookie/bearer JWT auth, drf-spectacular schema at `/schema/` and Swagger UI at `/swagger/` (`DrGame/settings.py`, `DrGame/urls.py`, `accounts/auth.py`).

# Repository Structure

- `DrGame/`: project settings, ASGI/WSGI entrypoints, root URL routing (`DrGame/settings.py`, `DrGame/urls.py`, `DrGame/asgi.py`, `DrGame/wsgi.py`).
- `accounts/`: custom user model, OTP login, API-key issuance, custom JWT auth, coarse role permissions (`accounts/models.py`, `accounts/views.py`, `accounts/auth.py`, `accounts/permissions.py`).
- `customers/`: customer profile completion and customer-self-service order/transaction/balance APIs (`customers/models.py`, `customers/views.py`).
- `employees/`: the largest operational app; includes employee/repairman records, requests, tasks, deposits, order management, reporting, stats, documents, real assets, global search, and many staff panel endpoints (`employees/models.py`, `employees/views.py`, `employees/serializers.py`, `employees/filters.py`).
- `home/`: storefront/catalog browsing, carts, blog/content pages, course/video content, banners, and resume submission (`home/models.py`, `home/views.py`, `home/serializers.py`).
- `payments/`: payment methods, transactions, product orders, game orders, repair orders, course orders, delivery-man records, Telegram orders, and Zarinpal callback/payment request logic (`payments/models.py`, `payments/views.py`).
- `messenger/`: internal chat rooms, membership, and messages for employees/main manager (`messenger/models.py`, `messenger/views.py`).
- `storage/`: core inventory/reference entities such as products, games, Sony accounts, documents, and real assets (`storage/models.py`, `storage/serializers.py`).
- `utils/`: TOTP encryption/OTP utilities for Sony accounts and Telegram broadcast of Sony-account details (`utils/views.py`, `utils/crypto.py`, `utils/services.py`, `utils/telegram.py`).
- `management/`: effectively dormant; URL patterns are commented out and models/views are empty or commented (`management/urls.py`, `management/models.py`, `management/serializers.py`, `management/views.py`).
- `staticfiles/`: collected static assets, including DRF/Redoc assets; appears to be build output rather than source (`staticfiles/...`).
- `backup.json`: a large Django fixture/backup snapshot containing live-like app data, API keys, and users; it is not referenced by runtime code (`backup.json`).

# Configuration & Environment

- Confirmed settings layout: there is a single `DrGame/settings.py`; there are no environment-specific settings modules (`DrGame/settings.py`).
- Environment variables in active use: `DATABASE_URL`, `REDIS_URL`, Liara S3 credentials, Faraz/IPPanel SMS config, Zarinpal URLs and merchant ID, `FERNET_KEY`, Telegram bot/channel config (`DrGame/settings.py`).
- Secrets handling is unsafe in-repo: `.env` contains real-looking database, Redis, S3, SMS, payment, Fernet, and Telegram secrets committed directly in the workspace (`.env`).
- Runtime modes currently encoded in code: `DEBUG=True`, permissive CORS (`CORS_ORIGIN_ALLOW_ALL=True`), non-secure session/CSRF flags, disabled HSTS, and a hard-coded Django `SECRET_KEY` in source (`DrGame/settings.py`).
- Database/cache/storage wiring: DB is loaded only from `DATABASE_URL`; Redis is used only as the default cache backend and throttling backend; file storage is configured through `django-storages` to an S3-compatible backend for default media while staticfiles remain local (`DrGame/settings.py`).
- External services configured: SMS sending is synchronous via HTTP calls from model/view code, payment initiation/verification is synchronous via Zarinpal HTTP calls from model/view code, Telegram posting is synchronous via Bot API (`accounts/models.py`, `employees/views.py`, `payments/models.py`, `utils/telegram.py`).
- Unknown until clarified: no in-repo deployment manifests describe how Redis, PostgreSQL, object storage, or process topology are actually provisioned in non-local environments.

# Application Architecture

- `accounts`
- Purpose: custom phone-based user identity, OTP login, JWT cookie issuance, API-key gating for auth endpoints, and role helpers (`accounts/models.py`, `accounts/views.py`).
- Models: `CustomUser`, singleton-style `MainManager`, `OTP`, and `APIKey` (`accounts/models.py`).
- Services/workflows: OTP codes are generated in `RequestOTPView`, stored in `OTP`, and sent synchronously through `OTP.send_otp`; `VerifyOTPView` validates the latest OTP and sets `access_token`/`refresh_token` cookies (`accounts/views.py`, `accounts/models.py`).
- Auth: `CustomJWTAuthentication` first checks the `access_token` cookie, then falls back to bearer auth (`accounts/auth.py`).
- Permissions: role checks are presence-based on one-to-one relations (`customer`, `employee`, `repairman`, `main_manager`) plus a decorator-style `restrict_access` helper that is currently imported but not used (`accounts/permissions.py`, `employees/views.py`).
- Important risk: `IsCustomer.has_permission` returns `True` for any authenticated user before checking the `customer` relation, so authenticated non-customers pass customer-only gates (`accounts/permissions.py`).

- `customers`
- Purpose: customer profile completion and self-service retrieval of orders, game orders, repair orders, course orders, balance, and transactions (`customers/views.py`).
- Models: `Customer` stores profile data, balance, discount, course-access flag, and soft-delete flag (`customers/models.py`).
- APIs: profile create/retrieve/update endpoints plus list/detail endpoints for each order family and transactions (`customers/urls.py`, `customers/views.py`).
- Dependencies: reads `Order`, `GameOrder`, `RepairOrder`, `CourseOrder`, and `Transaction` from `payments`; uses custom JWT auth from `accounts` (`customers/views.py`, `customers/serializers.py`).
- Important workflows: profile completion creates a `Customer` tied to the logged-in `CustomUser`; order endpoints scope data to `request.user.customer`; balance endpoint returns the stored integer ledger (`customers/serializers.py`, `customers/views.py`).
- Important risk: `CustomerProfileRetrieveAPIView.get_object()` auto-creates blank customers for any authenticated user, even before explicit profile completion (`customers/views.py`).

- `employees`
- Purpose: the internal back-office and operator panel for almost every business workflow (`employees/views.py`).
- Models: `Employee`, `Repairman`, `EmployeeFile`, `EmployeeTask`, `EmployeeRequest`, `EmployeeHire` (`employees/models.py`).
- Scope covered by this app: employee CRUD, customer CRUD, game/product/blog CRUD, Sony-account assignment and maintenance, product/game/repair/course order management, internal transactions, SMS blasts, tasks, employee requests, documents, real assets, reporting, and repairman panel APIs (`employees/urls.py`, `employees/views.py`).
- Serializer conventions: large multi-purpose serializers often implement write-side business logic directly, especially for transactions, game orders, repair orders, and nested item creation (`employees/serializers.py`).
- Workflows: employee personal requests/tasks, role-based owned game-order queues, assignment of the oldest unowned Sony account, deposit/withdrawal ledger adjustments, and stats/report endpoints (`employees/views.py`, `employees/serializers.py`).
- Dependencies: heavily coupled to `payments`, `storage`, `customers`, `home`, and `accounts`; this is the orchestration hub of the system (`employees/views.py`, `employees/serializers.py`).
- Important risks: many endpoints declare `permission_classes = [IsEmployee, IsMainManager]`, which DRF treats as logical AND, likely making those endpoints inaccessible to both standalone employees and the main manager unless a user somehow has both relations (`home/views.py`, `employees/views.py`).

- `home`
- Purpose: public/storefront APIs for products, games, blog/content pages, carts, game carts, courses/videos, banners, and resume submission (`home/views.py`).
- Models: `Cart`, `CartItem`, `GameCart`, `GameCartItem`, `BlogPost`, `AboutUs`, `ContactUs`, `ContactSubmission`, `Course`, `Video`, `HomeBanner` (`home/models.py`).
- APIs: catalog browsing, most-sold lists, add/remove cart items, game-cart manipulation, blog CRUD, singleton about/contact pages, contact submissions, course/video APIs, and banner CRUD (`home/urls.py`, `home/views.py`).
- Important workflows: physical cart quantities enforce stock, game carts collect games before conversion to `GameOrder`, and course/video exposure is limited by `Customer.has_access_to_course` and/or paid `CourseOrder` checks (`home/serializers.py`, `home/views.py`).
- Important risks: blog/about/contact/banner create/update/delete endpoints have no explicit permissions, and course/video management endpoints use `IsEmployee` and `IsMainManager` as an AND combination (`home/views.py`).

- `payments`
- Purpose: order/payment domain models and checkout flows for product, game, repair, and course purchases (`payments/models.py`, `payments/views.py`).
- Models: `PaymentMethod`, `Transaction`, `Order`, `OrderItem`, `DeliveryMan`, `GameOrder`, `GameOrderItem`, `RepairOrderType`, `RepairOrder`, `CourseOrder`, `TelegramOrder` (`payments/models.py`).
- Workflows: customer carts become `Order`/`OrderItem`; game carts become `GameOrder`/`GameOrderItem`; repair orders are created directly; all can generate online payment `Transaction` records through Zarinpal request URLs (`payments/views.py`, `payments/models.py`).
- Ledger coupling: order creation often immediately mutates `Customer.balance`, while transaction creation/payment callbacks also mutate customer and payment-method balances (`payments/views.py`, `payments/models.py`, `employees/serializers.py`).
- Important risks: the Zarinpal callback mutates order/payment state before calling `verify_payment()`, course-order payment request appears to fetch a `RepairOrder`, and repair payment callback sets `transaction.repair.status = 'paid'` even though repair status choices do not include `paid` (`payments/views.py`, `payments/models.py`).

- `messenger`
- Purpose: internal chat for employees and the main manager (`messenger/models.py`, `messenger/views.py`).
- Models: `ChatRoom`, `Membership`, `Message` with soft-delete/edit flags (`messenger/models.py`).
- APIs: list/create/delete/update chat rooms, add/remove members, list messages, send/edit/delete messages (`messenger/urls.py`, `messenger/views.py`).
- Workflows: only `MainManager` can create rooms; memberships are maintained via a through model; message sending validates room membership and optional same-room reply chains (`messenger/serializers.py`, `messenger/views.py`).
- Important risk: URL kwargs and view expectations appear mismatched for add/remove member endpoints (`messenger/urls.py`, `messenger/views.py`).

- `storage`
- Purpose: core master data and inventory records (`storage/models.py`).
- Models: product taxonomy and media, games and game images, Sony accounts and linked games, document categories/files, and real-asset categories/assets (`storage/models.py`).
- Business rules: max 4 trending games; `SonyAccount` supports encrypted TOTP secret storage and OTP generation; many models use `is_deleted` soft-delete markers (`storage/models.py`).
- Dependencies: consumed broadly by `home`, `employees`, `payments`, and `utils` (`home/views.py`, `employees/views.py`, `payments/models.py`, `utils/views.py`).

- `utils`
- Purpose: Sony-account TOTP management and Telegram integration (`utils/views.py`, `utils/crypto.py`, `utils/telegram.py`).
- APIs: set 2FA secret from otpauth URI, fetch current OTP, list matched Sony accounts for a game order, list matched game orders for a Sony account, send a Sony account summary to Telegram, and add Sony accounts (`utils/urls.py`, `utils/views.py`).
- Integrations: Fernet-encrypted secret storage, pyotp TOTP generation, Telegram Bot API posting (`utils/crypto.py`, `utils/views.py`, `utils/telegram.py`).
- Important risk: `SonyAccountAddFromFile` declares a serializer only; there is no implementation for parsing/importing the uploaded file (`utils/views.py`, `utils/serializers.py`).

# Data Model

- Core identity entity: `accounts.CustomUser` keyed by unique phone number and related one-to-one to one of `Customer`, `Employee`, `Repairman`, or `MainManager` (`accounts/models.py`, `customers/models.py`, `employees/models.py`).
- Customer ledger entity: `customers.Customer` stores profile, discount, balance, and course-access state (`customers/models.py`).
- Inventory entities: `storage.Product`, `storage.Game`, and `storage.SonyAccount`; Sony accounts link to many games through `SonyAccountGame` (`storage/models.py`).
- Product-sales flow: `home.Cart` + `CartItem` -> `payments.Order` + `OrderItem` -> optional `payments.Transaction` (`home/models.py`, `payments/models.py`, `payments/views.py`).
- Game-order flow: `home.GameCart` + `GameCartItem` -> `payments.GameOrder` + `GameOrderItem`, optionally linked to `SonyAccount` rows and `DeliveryMan` rows (`home/models.py`, `payments/models.py`, `payments/views.py`).
- Repair flow: `payments.RepairOrder` references `Customer`, `Repairman`, `RepairOrderType`, `Transaction`, and delivery records (`payments/models.py`).
- Course-access flow: `payments.CourseOrder` references `Customer` and `Transaction`; actual course entitlement is currently stored as a boolean on `Customer`, not a per-course relation (`payments/models.py`, `customers/models.py`, `home/views.py`).
- Staff-operation entities: `EmployeeTask`, `EmployeeRequest`, `EmployeeFile`, `EmployeeHire`, `TelegramOrder`, `Document`, and `RealAssets` (`employees/models.py`, `payments/models.py`, `storage/models.py`).
- Ownership rules confirmed in code: customer-facing order detail endpoints scope by `request.user.customer`; repairman panel scopes repair orders by `request.user.repairman`; employee personal queues scope by `request.user.employee` (`customers/views.py`, `employees/views.py`).
- State transitions confirmed in code: game orders use explicit status enums like `waiting_for_delivery`, `delivered_to_drgame_and_in_waiting_queue`, `in_data_uploading_queue`, `done`, `delivered_to_customer`; repair orders use their own progression from `waiting_for_delivery_to_drgame` through `done`/`delivered_to_customer` (`payments/models.py`).

# Authentication & Authorization

- Confirmed auth flow: clients must include an `X-API-Key` header for OTP endpoints, request an OTP by phone, verify the OTP, then receive `access_token` and `refresh_token` as HTTP-only cookies (`accounts/views.py`, `accounts/models.py`).
- Confirmed auth implementation: API requests use `CustomJWTAuthentication`, which prefers the cookie token and falls back to bearer auth (`accounts/auth.py`, `DrGame/settings.py`).
- JWT settings: access lifetime 72,600 seconds, refresh lifetime 4,320,000 seconds, rotation enabled, secure cookie flag set `True`, SameSite `None` (`DrGame/settings.py`).
- Session auth is not actively used for API flows despite Django session middleware being enabled; no login views or DRF session auth classes are configured (`DrGame/settings.py`, `accounts/views.py`).
- Roles/actors confirmed in code: customer, employee, repairman, main manager, and superuser (`accounts/permissions.py`, `accounts/views.py`).
- Permission model is inconsistent: some endpoints use correct OR composition (`IsEmployee | IsMainManager`), others incorrectly pass multiple permission classes in a list expecting OR semantics (`messenger/views.py`, `utils/views.py`, `employees/views.py`, `home/views.py`).
- Granular employee capability booleans exist on `Employee` and are surfaced by `UserStatusView`, but the decorator that could enforce them (`restrict_access`) is unused (`employees/models.py`, `accounts/views.py`, `accounts/permissions.py`, `employees/views.py`).

# API Architecture

- Root API namespaces: `/accounts/`, `/customers/`, `/employees/`, `/messenger/`, `/payments/`, and root-level public/storefront routes from `home` (`DrGame/urls.py`).
- API style: mostly DRF generic class-based views with queryset scoping and serializer-driven write logic; only a few custom `APIView` classes are used for OTP, payment callbacks, and some delivery/TOTP actions (`accounts/views.py`, `home/views.py`, `payments/views.py`, `utils/views.py`).
- Validation approach: lightweight field checks in serializers and views; critical transactional business rules are often implemented in serializer `create()`/`update()` methods instead of service classes (`home/serializers.py`, `employees/serializers.py`, `payments/views.py`).
- Filtering/search/pagination: DRF limit-offset pagination is default project-wide; `employees` and `home` add search/order/filter backends on many list views (`DrGame/settings.py`, `home/views.py`, `employees/views.py`, `employees/filters.py`).
- Error handling: mostly direct `Response(...)` or raised `ValidationError`; no custom exception handler or shared error envelope exists (`accounts/views.py`, `payments/views.py`, `employees/views.py`).
- Schema/docs: drf-spectacular serves `/schema/` and `/swagger/`; a custom auth extension is referenced, but `accounts.auth.CustomJWTAuthenticationExtension` is not implemented in `accounts/auth.py` (`DrGame/settings.py`, `accounts/auth.py`).

# Background Processing

- Confirmed absence: no Celery app, no task modules, no scheduled jobs, no Django-Q/Huey/RQ setup, and no management commands were found in the repository (repo-wide grep, `requirements.txt`).
- Confirmed behavior: all third-party side effects happen synchronously in request/response paths or model methods, including OTP SMS, bulk SMS, Zarinpal payment requests/verifications, and Telegram posting (`accounts/models.py`, `employees/views.py`, `payments/models.py`, `utils/telegram.py`).
- Retries/failure handling: failures are handled ad hoc per request with immediate error responses; there is no queue, dead-letter, retry policy, or compensating workflow framework in code (`accounts/models.py`, `payments/models.py`, `utils/telegram.py`).
- Unknown until clarified: if external cron/worker infrastructure exists outside the repo, it is not represented here.

# Business Logic & Workflows

- OTP onboarding/login: request OTP by phone with API key, create inactive users on first contact, verify latest OTP, activate user if needed, and set JWT cookies (`accounts/views.py`).
- Customer profile completion: authenticated users can create or auto-create/update a `Customer` profile, after which customer-only order/cart flows become usable (`customers/views.py`, `customers/serializers.py`).
- Product purchase flow: customer adds items to `Cart`; `OrderCreate` snapshots cart items into `OrderItem`, deletes the cart, and immediately subtracts order amount from `Customer.balance`; payment is later requested via Zarinpal (`home/views.py`, `payments/views.py`).
- Game-order flow: customer builds `GameCart`, chooses console/type at checkout, `GameOrderCreate` prices each selected game from the corresponding platform-specific price field, creates `GameOrderItem` rows, deletes the game cart, and subtracts the amount from `Customer.balance` (`home/views.py`, `payments/views.py`).
- Internal game-order fulfillment flow: staff update `GameOrderItem.account`/`.data`, which stamps the acting employee as `account_setter` or `data_uploader`; when a game order reaches `done`, percentage commissions are credited to those employees if enabled (`employees/serializers.py`).
- Repair-order flow: customer creates a repair order and optionally assigns a delivery person; repairmen can accept jobs and progress them through fee/amount/in-progress/done states; customer balance is adjusted when the order enters `in_progress`, and repairman balance increases when the order reaches `done` (`payments/views.py`, `employees/serializers.py`, `employees/views.py`).
- Course-access flow: customers can create a `CourseOrder`; successful payment callback sets `Customer.has_access_to_course = True`, and course/video APIs then expose more content based on that flag and/or paid-order checks (`payments/views.py`, `home/views.py`, `home/serializers.py`).
- Sony-account workflow: employees can claim the oldest unowned Sony account if they do not already hold an unchecked account; main-manager/employee tools can set TOTP secrets, fetch OTP codes, match accounts against game orders, and push account summaries to Telegram (`employees/views.py`, `utils/views.py`, `utils/services.py`).
- Internal finance workflow: manual incoming/outgoing transaction endpoints mutate both `Transaction` rows and `PaymentMethod`/`Customer`/`Employee` balances, making the balance fields a core internal ledger rather than a derived metric (`employees/serializers.py`, `employees/views.py`).

# Integrations

- Faraz/IPPanel SMS: OTP sending uses `settings.FARAZ_URL`, `FARAZ_API_KEY`, and `FARAZ_SMS_PATTERN` in `OTP.send_otp`; bulk staff/customer SMS views also POST directly to `https://edge.ippanel.com/v1/api/send` (`accounts/models.py`, `employees/views.py`, `DrGame/settings.py`).
- Zarinpal: `Transaction.request_payment()` and `Transaction.verify_payment()` call configured request/verify URLs and persist `authority`, `status`, and `ref_id`; callback endpoint is `/payments/verify-payment` (`payments/models.py`, `payments/views.py`, `DrGame/settings.py`).
- S3-compatible object storage: Django default file storage is `storages.backends.s3.S3Storage` configured with Liara object-storage credentials (`DrGame/settings.py`).
- Telegram Bot API: `utils.telegram.send_telegram_message()` posts HTML messages to a configured channel/chat using `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHANNEL_ID` (`utils/telegram.py`, `DrGame/settings.py`).
- TOTP/Fernet: Sony-account 2FA secrets are stored encrypted with `FERNET_KEY` and surfaced as current TOTP codes through `pyotp` (`storage/models.py`, `utils/crypto.py`, `utils/views.py`).
- No OAuth/social auth providers, payment webhooks beyond Zarinpal callback, or email integrations are present in code.

# Frontend Interaction

- Confirmed architecture: this repo is backend/API-only from the source available; no SPA source, no SSR templates, and no frontend build config are present (`find` inventory, `DrGame/urls.py`).
- Public JSON APIs serve storefront data for products, games, blogs, contact/about pages, courses/videos, and banners (`home/urls.py`, `home/views.py`).
- Auth/frontend contract: OTP endpoints require `X-API-Key`; login state is conveyed primarily through HTTP-only JWT cookies, with bearer fallback also accepted by the custom auth class (`accounts/views.py`, `accounts/auth.py`).
- CORS/CSRF posture: CORS is effectively open to all origins with credentials allowed; CSRF middleware is enabled, but cookie settings are currently insecure/non-production friendly (`DrGame/settings.py`).
- Static/media strategy: static files collect to `staticfiles/`; media uses the default storage backend, which is configured to S3-compatible object storage (`DrGame/settings.py`).

# Testing Strategy

- Confirmed status: there is effectively no meaningful automated test coverage in-repo. Most app `tests.py` files are empty stubs, and `accounts/tests.py` is completely empty (`accounts/tests.py`, `customers/tests.py`, `employees/tests.py`, `home/tests.py`, `messenger/tests.py`, `payments/tests.py`, `storage/tests.py`, `utils/tests.py`).
- No fixtures/factories: there are no pytest configs, factory libraries, or dedicated test data builders; only a broad `backup.json` fixture-like dump exists (`backup.json`).
- High-risk uncovered areas: auth/OTP, payment callbacks, balance mutations, permission gates, repair/game-order state transitions, and Sony-account/TOTP flows all lack visible tests (`accounts/views.py`, `payments/views.py`, `employees/serializers.py`, `utils/views.py`).

# DevOps & Deployment

- Runtime infra assumptions in code: PostgreSQL, Redis, S3-compatible object storage, external SMS provider, external Zarinpal gateway, and Telegram are all required or strongly assumed (`DrGame/settings.py`, `.env`).
- `manage.py`, WSGI, and ASGI entrypoints are present, but no process manager configs are included (`manage.py`, `DrGame/wsgi.py`, `DrGame/asgi.py`).
- Monitoring/logging: no structured logging, Sentry, health endpoints, metrics, or tracing hooks are configured; many code paths use raw `print()` statements, including auth and OTP flows (`accounts/auth.py`, `accounts/models.py`, `payments/views.py`).
- Scaling concerns: synchronous third-party API calls, heavy serializer business logic, absent background jobs, and balance mutations in request paths all create operational risk under load (`accounts/models.py`, `payments/models.py`, `employees/serializers.py`, `utils/telegram.py`).
- Unknown until clarified: the intended production deployment topology, worker count, reverse proxy, TLS termination, and secrets-management approach are not represented in the repo.

# Security Notes

- Critical: real-looking secrets are committed in `.env`, and Django `SECRET_KEY` is hard-coded in source (`.env`, `DrGame/settings.py`).
- Critical: `DEBUG=True`, permissive CORS with credentials, insecure CSRF/session flags, and disabled HSTS/browser protections are committed as runtime defaults (`DrGame/settings.py`).
- Critical: auth code prints request headers and raw access tokens to stdout during authentication (`accounts/auth.py`).
- High risk: OTP send flow prints phone numbers and OTP codes to stdout (`accounts/models.py`, `accounts/views.py`).
- High risk: several create/update/delete content endpoints have no explicit permission classes, exposing mutation paths if global defaults permit authenticated or unauthenticated access (`home/views.py`).
- High risk: role enforcement is inconsistent; `IsCustomer` is overly permissive for authenticated users, and many staff endpoints likely use incorrect AND semantics for permissions (`accounts/permissions.py`, `home/views.py`, `employees/views.py`).
- High risk: customer/employee/payment balances are directly mutable integers spread across multiple code paths without centralized invariants or reconciliation (`payments/views.py`, `employees/serializers.py`, `employees/views.py`).

# Technical Debt / Risks

- Large files and tight coupling: `employees/views.py` and `employees/serializers.py` each concentrate many unrelated domains, making change impact high (`employees/views.py`, `employees/serializers.py`).
- Dormant/dead code: `management` app is commented out; `restrict_access` is unused; Channels/Celery are installed without active code paths (`management/*`, `accounts/permissions.py`, `employees/views.py`, `requirements.txt`).
- Data model drift: some code references fields/relations that do not exist or do not match current models, indicating partial refactors (for example `CourseOrderSerializer` in `customers` references `source='course.title'`, while `CourseOrder` has no `course` field; repair/payment code mixes status/payment fields inconsistently) (`customers/serializers.py`, `payments/models.py`, `payments/views.py`).
- Permission bugs: repeated `permission_classes = [IsEmployee, IsMainManager]` patterns appear across multiple apps (`home/views.py`, `employees/views.py`).
- Soft-delete inconsistency: many models have `is_deleted`, but delete views often call hard delete through generic destroy behavior unless overridden (`home/views.py`, `employees/views.py`, `messenger/views.py`, model definitions).
- Migration complexity: several apps have long migration histories and at least one merge migration in `payments`, suggesting non-trivial schema evolution (`payments/migrations/0015_merge_20250707_1501.py`, app migration folders).
- Missing tests: critical workflows have no automated safety net (`tests.py` files across apps).

# Developer Conventions

- Confirmed conventions: broad use of DRF generics, model-level `is_deleted` flags, and serializer-embedded business logic (`employees/serializers.py`, `home/serializers.py`, `payments/views.py`).
- Naming patterns: public/storefront endpoints live in `home`, customer-self-service in `customers`, and admin/back-office APIs are prefixed with `EmployeePanel...` or repairman-specific panel classes in `employees` (`home/views.py`, `customers/views.py`, `employees/views.py`).
- File/media naming: upload paths are domain-specific (`profile_pics/customers/`, `employee_files/`, `blog_images/`, `course/`, `videos/`, `docs/`, `real_assets/photos/`) (`customers/models.py`, `employees/models.py`, `home/models.py`, `storage/models.py`).
- Query conventions: many list views use `select_related`/`prefetch_related`, but service boundaries are minimal and write flows are not isolated into dedicated domain services (`customers/views.py`, `home/views.py`, `employees/views.py`).
- Error/response style: mixed Persian and English messages, often returned directly from views/serializers without shared formatting (`accounts/views.py`, `payments/views.py`, `employees/views.py`, `messenger/views.py`).

# Known Unknowns

- Is the `management` app intentionally deprecated, or should it be treated as an incomplete but planned surface? Current repo evidence shows it is inactive (`management/urls.py`, `management/views.py`, `management/serializers.py`).
- Are the many `permission_classes = [IsEmployee, IsMainManager]` declarations known bugs, or is there an unstated expectation that one user can hold both relations? Repo evidence points to logical-AND behavior in DRF, but intended production behavior is unclear (`home/views.py`, `employees/views.py`).
- Is course access intended to be global or per-course? Current models only store a single boolean on `Customer`, while `CourseOrder` has no foreign key to `Course` (`customers/models.py`, `payments/models.py`, `home/serializers.py`).
- Are customer/employee balance mutations intended as a prepayment wallet/reservation ledger, or are some of the immediate debits/credits accidental? The implementation is internally inconsistent across order creation, manual transactions, and payment callbacks (`payments/views.py`, `employees/serializers.py`, `employees/views.py`).
- Is `backup.json` an active operational fixture that should be preserved and documented, or a historical/export artifact? The code does not reference it (`backup.json`).
- Are Channels/Celery planned for future use, or are they stale dependencies? No active usage is present in the repo (`requirements.txt`, repo-wide grep results).
- What is the intended production hosting/deployment model? There is no in-repo Docker/CI/process-manager config to confirm it.

# Suggested Improvements

- Deferred until the remaining architecture and production-intent ambiguities are clarified.
