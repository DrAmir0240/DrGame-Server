# DrGame — Full Gap Report: `architecture.md` vs. Actual Implementation

> تاریخ گزارش: ۲۰۲۶-۰۸-۰۱
> وضعیت پروژه: Backend-only (Django 5.2 + DRF) — Frontend جدا و monorepo پیاده‌سازی نشده

---

## فهرست مطالب

1. [خلاصه اجرایی](#1-خلاصه-اجرایی)
2. [استک فنی واقعی](#2-استک-فنی-واقعی)
3. [ساختار اپ‌های پیاده‌سازی‌شده](#3-ساختار-اپهای-پیادهسازیشده)
4. [ماژول‌های پیاده‌سازی‌شده (موجود)](#4-ماژولهای-پیادهسازیشده-موجود)
5. [ماژول‌های غایب (در معماری ولی نبوده)](#5-ماژولهای-غایب-در-معماری-ولی-نبوده)
6. [اجزای زیرساختی غایب](#6-اجزای-زیرساختی-غایب)
7. [تفاوت‌های طراحی و انحراف‌ها](#7-تفاوتهای-طراحی-وانحرافها)
8. [ماتریس وضعیت ماژول‌ها](#8-ماتریس-وضعیت-ماژولها)
9. [اولویت‌بندی پیشنهادی برای تکمیل](#9-اولویتبندی-پیشنهادی-برای-تکمیل)

---

## ۱. خلاصه اجرایی

فایل `architecture.md` یک ERP کامل چندشعبه‌ای را توصیف می‌کند شامل ۹ فاز توسعه (Core، Inventory، Accounts، Orders، Repair، Procurement، Accounting، HR، Task، CRM، Notification، E-commerce، Documents) به همراه **Frontend Next.js** و **nginx** در قالب **Monorepo**.

پروژه فعلی یک **Backend-only** است که بخش عمده‌ای از ماژول‌های کسب‌وکار را پیاده کرده، اما با انحراف‌های قابل توجه از مستند معماری:

- **حسابداری ساده‌شده**: به‌جای سیستم دوطرفه (Double-Entry) با Chart of Accounts و JournalEntry، از مدل ساده `Invoice` / `Transaction` استفاده شده.
- **بدون مدل شعبه (Branch)**: معماری چندشعبه‌ای، انبار شعبه‌ای و صندوق مجزا پیاده نشده.
- **RBAC ساده‌تر**: به‌جای ماتریس پویای Role × Module × read/write، از `EmployeeRole` با فیلدهای بولی ثابت استفاده شده.
- **Procurement، Refund، Notifications، AuditLog غایب** هستند.
- **Celery / Channels / WebSocket** در `requirements.txt` هست ولی **پیکربندی نشده**.
- **درگاه پرداخت Zarinpal** فقط متغیرهای محیطی دارد؛ پیاده‌سازی‌ای وجود ندارد.
- **بدون Frontend و nginx** — بخش بزرگ معماری عملاً غایب است.

---

## ۲. استک فنی واقعی

| بخش | معماری (طراحی) | واقعیت پروژه |
|-----|----------------|--------------|
| زبان | Python 3.12+ | Python 3.12 (venv) |
| فریم‌ورک | Django 5.x + DRF | Django 5.2.3 + DRF 3.16 |
| احراز هویت | SimpleJWT (Bearer) | SimpleJWT + **HTTP-only Cookie** (access/refresh) + OTP با Faraz SMS |
| WebSocket | Django Channels + Redis | فقط نصب (channels 4.3.1) — **بدون CHANNEL_LAYERS، routing، consumer** |
| صف | Celery + Redis | فقط نصب (celery 5.5.3) — **بدون celery.py و broker** |
| دیتابیس | PostgreSQL 16 خارجی | PostgreSQL 16 (docker-compose، پورت 5433) |
| Cache | Redis | django-redis پیکربندی شده (REDIS_URL) |
| ساختار | Monorepo (backend/frontend/nginx) | فقط Django backend — **بدون frontend و nginx** |
| Reverse Proxy | Nginx | غایب |
| Payment | Zarinpal Placeholder → پیاده‌سازی | فقط متغیرهای ZARINPAL_* — **بدون پیاده‌سازی** |
| SMS | Placeholder → Faraz | Faraz پیاده شده (FARAZ_*) |
| Telegram | — | utils/telegram.py پیاده شده |
| TOTP | — | psn.SonyAccount با Fernet-encrypted secrets |

---

## ۳. ساختار اپ‌های پیاده‌سازی‌شده

در `settings.py` این اپ‌ها فعال هستند:

```
users, platform_settings, hr, inventory, task_manager, accounting,
website, crm, messenger, utils, psn, docs, orders, dashboard, support
```

مسیرهای فعال در `DrGame/urls.py`:

```
admin/   accounting/   crm/   docs/   hr/   inventory/   orders/
psn/     support/   task-manager/   users/   website/   customer/   schema/   swagger/
```

**نکته:** برخلاف CLAUDE.md که می‌گوید فقط `users/`, `task-manager/`, `schema/`, `swagger/` فعال هستند، عملاً همه اپ‌ها در urls.py فعال‌اند.

---

## ۴. ماژول‌های پیاده‌سازی‌شده (موجود)

### ۴.۱ Auth (users)
- ✅ `CustomUser` با شماره تلفن به عنوان USERNAME_FIELD
- ✅ OTP (request/verify) — درخواست OTP، تأیید، JWT از طریق Cookie
- ✅ `MainManager` (singleton-like، PK=1)
- ✅ `APIKey` برای دسترسی خارجی
- ✅ JWT refresh/blacklist تنظیم‌شده
- ⚠️ `Rate limiting` روی auth با django_ratelimit موجود است
- ⚠️ OTP در DB ذخیره می‌شود (مدل `OTP`)، نه Redis (معماری جدید Redis را پیشنهاد می‌دهد)

### ۴.۲ HR (hr)
- ✅ `Employee` — اطلاعات کامل، نوع قرارداد، شعبه (فیلد موجود ولی مدل Branch ندارد!)
- ✅ `EmployeeRole` — ماتریس دسترسی بولی per-module
- ✅ `EmployeeRequest` — درخواست‌های کارمندان
- ✅ `EmploymentResume` — رزومه‌ها
- ✅ `EmployeeArrival` — حضور و غیاب
- ✅ `EmployeeOvertime` — اضافه‌کاری
- ✅ `EmployeeFile` — فایل‌ها
- ❌ مرخصی (LeaveRequest) مدل مجزا ندارد — احتمالاً در EmployeeRequest است
- ❌ `SalaryRecord` — محاسبه حقوق خودکار ندارد

### ۴.۳ Inventory (inventory)
- ✅ `Product` + `ProductCategory` + `ProductImage`
- ✅ `ProductEntity` — هر واحد فیزیکی/بارکد
- ✅ `InventoryMovement` — گردش انبار
- ✅ `Supplier` — تأمین‌کننده (فقط مدل؛ بدون workflow خرید)
- ❌ `BranchTransfer` — انتقال بین شعبه
- ❌ انبار مستقل per-branch (چون Branch غایب است)

### ۴.۴ Task Manager (task_manager)
- ✅ `PlannedTask` — تسک برنامه‌ریزی‌شده با approval workflow و پاداش
- ✅ `DailyTask` — تسک روزانه
- ✅ APIها و Permission کامل

### ۴.۵ Accounting (accounting) — ساده‌شده
- ✅ `BankAccount`, `AccountSide`, `InvoiceCategory`
- ✅ `Invoice` + `InvoiceItem` — فاکتور (درآمد/هزینه/حقوق/خرید/فروش/تعمیر)
- ✅ `Transaction` — جهت in/out
- ✅ `PayrollDetail` — فیش حقوق
- ✅ `Wallet` + `WalletTransaction` — کیف پول با WalletService اتمیک (select_for_update)
- ✅ گزارش‌ها: درآمد/هزینه، هفتگی، net، گزارش سفارش‌ها (repair/product/sony)
- ❌ Chart of Accounts، JournalEntry، TaxConfig، CashReconciliation

### ۴.۶ Website / E-commerce (website)
- ✅ Store محصولات (search, list, detail, images)
- ✅ Store بازی‌ها (games)
- ✅ Cart محصول + Cart بازی + matched-accounts + volume
- ✅ Blog (categories, posts, images)
- ✅ Videoها
- ✅ HomeBanner / HomeSection / AboutUs
- ✅ نسخه Employee (CRUD کامل از پنل)
- ⚠️ Blog در `website` است؛ معماری فاز ۵ اپ جداگانه `blog` می‌خواهد

### ۴.۷ CRM (crm)
- ✅ `Customer`, `B2BProfile` (debt_amount_max, discount)
- ✅ `CustomerWishlist`
- ✅ پروفایل مشتری، کیف پول، wishlist، سفارش‌ها، تیکت‌ها (مسیرهای `/customer/`)
- ❌ منطق بلاک‌کردن خودکار خرید هنگام تجاوز از سقف بدهی

### ۴.۸ Orders (orders)
- ✅ معماری Stage-based پیشرفته: `BaseOrderStage`, `BaseOrderStageAction`, `BaseOrderStageLog`, `BaseOrderActionLog`
- ✅ `ProductOrder` + items — سفارش کالا
- ✅ `SonyAccountOrder` + consoles + items — سفارش اکانت سونی
- ✅ `RepairOrder` + devices — سفارش تعمیر
- ✅ فیلترها و گزارش‌ها
- ❌ Invoice پیوسته (INV-YYYY-NNNNN) — Invoice در accounting ساده است
- ❌ Refund / Return / Cancellation
- ❌ Payment از نوع online gateway

### ۴.۹ PSN (psn)
- ✅ `SonyAccount` — با TOTP (set_totp_secret / get_otp)
- ✅ `SonyAccountStatus`, `SonyAccountBank`, `SonyAccountSellMethod`, `SonyAccountAction`
- ✅ `SonyAccountGame`

### ۴.۱۰ Support (support)
- ✅ `Ticket` + `TicketMessage` (is_internal مخفی از مشتری)
- ✅ پنل Employee (list, detail, assign, status, internal-note)
- ✅ مسیرهای مشتری `/customer/tickets/`

### ۴.۱۱ Docs & Assets (docs)
- ✅ `DocCategory`, `DocSubCategory`, `Document`
- ✅ `RealAssetsCategory`, `RealAssetsSubCategory`, `RealAssets`

### ۴.۱۲ Messenger (messenger)
- ✅ `ChatRoom`, `Membership`, `Message`
- ⚠️ چت داخلی — نه سیستم اعلان عمومی

### ۴.۱۳ Dashboard (dashboard)
- ✅ اپ داشبورد با گزارش‌ها

### ۴.۱۴ Utils (utils)
- ✅ `get_game_price`, `humanize_price`, `build_account_message`, `send_telegram_message`, crypto (Fernet)

---

## ۵. ماژول‌های غایب (در معماری ولی نبوده)

جستجوی سراسری در کد (بدون migrations/venv):

| ماژول معماری | مدل/سیستم | وضعیت |
|--------------|-----------|-------|
| **Branch** | مدل Branch، انبار شعبه‌ای، صندوق مجزا، انتقال بین شعبه | ❌ کاملاً غایب |
| **RBAC پویا** | Role, Module, Permission, UserRole | ❌ فقط EmployeeRole ثابت |
| **AuditLog** | core_auditlog + middleware | ❌ کاملاً غایب |
| **Procurement** | PurchaseRequest, PurchaseOrder (فقط Supplier موجود) | ❌ workflow غایب |
| **Double-Entry** | Account (Chart of Accounts), JournalEntry, JournalLine | ❌ غایب |
| **TaxConfig / VAT** | نرخ مالیات متغیر | ❌ غایب |
| **CashReconciliation** | صفرسازی روزانه صندوق | ❌ غایب |
| **Refund / Return** | Refund, ReturnPolicy, لغو سفارش با برگشت موجودی | ❌ غایب |
| **Notifications** | Notification, NotificationPreference, WebSocket | ❌ غایب |
| **SalaryRecord** | محاسبه حقوق (base+commission+reward−advance−penalty) | ❌ غایب |
| **B2B credit blocking** | بلاک خودکار روی تجاوز از سقف بدهی | ❌ منطق غایب |
| **Leave (مرخصی)** | LeaveRequest مجزا | ❌ (در EmployeeRequest ادغام شده) |

---

## ۶. اجزای زیرساختی غایب

| جزء | جزئیات |
|-----|--------|
| **Frontend (Next.js 14+)** | کل بخش frontend غایب — معماری §3.1 خالی |
| **nginx** | Reverse Proxy غایب — سرویس nginx در docker-compose نیست |
| **Celery / Celery Beat** | هیچ `celery.py`، `__init__` بدون celery، بدون broker URL، بدون تسک‌های زمان‌بندی (نوتیفیکیشن deadline، پاک‌سازی ماهانه) |
| **Django Channels** | نصب است ولی `CHANNEL_LAYERS`، `routing.py`، consumer، ASGI config وجود ندارد — `asgi.py` صرفاً `get_asgi_application()` است |
| **Zarinpal Payment** | فقط متغیرهای `ZARINPAL_*` در settings؛ تابع `request_payment` / `verify_payment` وجود ندارد (CLAUDE.md ادعای اشتباه دارد). شارژ کیف پول شبیه‌سازی‌شده است |
| **docker-compose services** | فقط `db`, `redis`, `app` — بدون celery, celery-beat, nginx, frontend |
| **Backup/Restore** | Makefile دارد ولی docker-compose prod ندارد |

---

## ۷. تفاوت‌های طراحی و انحراف‌ها

1. **حسابداری**: معماری دوطرفه کامل → پروژه از مدل ساده Invoice/Transaction استفاده می‌کند (شاید تصمیم عمدی برای MVP باشد).
2. **RBAC**: معماری Role×Module×action پویا → پروژه فیلدهای بولی ثابت در `EmployeeRole` (ساده‌تر ولی غیرقابل سفارشی‌سازی).
3. **سفارش‌ها**: پروژه به سراغ Stage-based workflow (BaseOrderStage) رفته که از معماری پیشرفته‌تر است.
4. **Auth**: معماری Bearer token → پروژه از HTTP-only Cookie استفاده می‌کند (امن‌تر).
5. **TOTP**: معماری اکانت‌ها را ساده دارد؛ پروژه TOTP کامل با Fernet برای SonyAccount دارد.
6. **واقعیت‌تر**: پروژه اپ‌های `psn`, `messenger`, `support`, `dashboard`, `platform_settings` را اضافه کرده که در معماری نبودند.
7. **Blog**: در `website` ادغام شده به‌جای اپ مجزا.
8. **الگوی Codebase**: معماری می‌گوید `config/settings/base.py` و `development.py`؛ پروژه تک‌فایل `settings.py` دارد.

---

## ۸. ماتریس وضعیت ماژول‌ها

| ماژول | وضعیت | پوشش | یادداشت |
|-------|-------|------|---------|
| Auth/OTP | ✅ کامل | ~100% | Cookie-based، OTP در DB |
| RBAC | ⚠️ جزئی | ~50% | EmployeeRole بولی؛ بدون نقش پویا |
| Branch | ❌ غایب | 0% | نیاز بنیادی برای چندشعبه‌ای |
| AuditLog | ❌ غایب | 0% | |
| Inventory | ⚠️ جزئی | ~70% | بدون انتقال بین شعبه، بدون انبار شعبه‌ای |
| Accounts/PSN | ✅ خوب | ~85% | TOTP + لاگ فروش |
| Orders | ✅ خوب | ~80% | Stage-based؛ بدون refund/return |
| Invoice/Payment | ⚠️ جزئی | ~40% | بدون شماره پیوسته، بدون درگاه واقعی |
| Repair | ✅ خوب | ~80% | Stage-based |
| Procurement | ❌ غایب | ~10% | فقط Supplier |
| Accounting | ⚠️ جزئی | ~50% | ساده‌شده؛ بدون double-entry |
| HR | ⚠️ جزئی | ~60% | بدون محاسبه حقوق/مرخصی مجزا |
| Task Manager | ✅ کامل | ~95% | |
| CRM/B2B | ⚠️ جزئی | ~65% | بدون credit-blocking |
| Notifications | ❌ غایب | 0% | فقط messenger چت |
| E-commerce | ✅ خوب | ~85% | website کامل؛ بدون checkout/درگاه |
| Documents/Assets | ✅ کامل | ~95% | |
| Dashboard/Reports | ✅ خوب | ~80% | |
| Support | ✅ کامل | ~95% | اپ جدید فراتر از معماری |
| Celery/Channels | ❌ غایب | 0% | نصب ولی بدون پیکربندی |
| Frontend/nginx | ❌ غایب | 0% | |

---

## ۹. اولویت‌بندی پیشنهادی برای تکمیل

### سطح ۱ — بحرانی برای ERP (پیشنهاد فوری)
1. **درگاه پرداخت Zarinpal** — پیاده‌سازی `request_payment` / `verify_payment` واقعی (الزام کسب‌وکار)
2. **مدل Branch** + وابسته‌ها — بنیاد چندشعبه‌ای (انبار شعبه‌ای، صندوق مجزا)
3. **Refund / Return / Cancellation** — برگشت موجودی + استرداد وجه
4. **AuditLog** — لاگ تغییرات قبل/بعد

### سطح ۲ — مهم برای تکمیل معماری
5. **Procurement workflow** — PurchaseRequest / PurchaseOrder با Signal موجودی
6. **Celery + Celery Beat** — بروکر Redis، نوتیفیکیشن deadline، پاک‌سازی ماهانه
7. **Django Channels** — WebSocket نوتیفیکیشن real-time
8. **سیستم Notification** — مدل + Preference + سرویس

### سطح ۳ — بهبود/انطباق با معماری
9. **RBAC پویا** — Role/Module/Permission ماتریس
10. **حسابداری دوطرفه** — Chart of Accounts + JournalEntry (یا مستندسازی عمدی ساده‌بودن)
11. **محاسبه حقوق** — SalaryRecord خودکار با کسر مساعده/جریمه
12. **B2B credit-blocking** — منطق بلاک خودکار
13. **Frontend / nginx** — ساختار Monorepo کامل

---

*گزارش بر اساس کد واقعی پروژه و `architecture.md` تهیه شده است.*
