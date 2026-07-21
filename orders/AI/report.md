# Orders App — Session Report

گزارش کامل کاری که در این session روی اپ `orders` انجام شد — از پیاده‌سازی اولیه‌ی
موتور workflow تا رفع مشکلات و امن‌سازی.

---

## ۱. چه چیزی ساخته شد (فاز اول)

موتور stage/action برای هر سه نوع سفارش (اکانت سونی، تعمیر، محصول) پیاده‌سازی شد.

### فایل‌ها
- **`orders/services.py`** (جدید) — منطق workflow: `execute_*_order_action` و
  `advance_*_order_stage` برای هر سه نوع، با helper مشترک `_advance_stage_generic`.
- **`orders/serializers.py`** — بخش workflow اضافه شد (Category / Stage / StageAction /
  nested / worker card + detail / action). کلاس‌های legacy که به مدل‌های حذف‌شده‌ی
  accounting وابسته بودند داخل `''' '''` کامنت شدند.
- **`orders/views.py`** — view های config (مدیر) + worker (کارمند) برای هر سه نوع.
- **`orders/urls.py`** — ۴۲ مسیر با `name=` (الگو `<type>-<resource>-<action>`).
- **`DrGame/urls.py`** — فعال‌سازی `path('orders/', include('orders.urls'))`.

### منطق اپ
لایه‌ی config (مدیر): `Category → Stage (+employee_role, +order) → StageAction
(+action_type, +target_field)`.
لایه‌ی worker (کارمند) — جریان ۶ مرحله‌ای فرانت:
```
my-stages → orders/by-stage/{id} → orders/{id} → orders/{id}/actions
→ execute-action → advance-stage
```
دو عملیات هسته:
- **execute_action** — یک اکشن را روی سفارش اجرا و لاگ می‌کند.
- **advance_stage** — چک می‌کند همه‌ی اکشن‌های required انجام شده، سپس به مرحله‌ی
  بعدی (`order + 1`) می‌رود.

---

## ۲. تصمیم‌های کلیدی (قانون: مدل‌های پروژه منبع حقیقت‌اند، نه md)

- **`is_done` حذف شد** — روی هیچ item model وجود ندارد. نتیجه: Repair و Product هیچ
  فیلد آیتم قابل‌آپدیتی ندارند، پس serializer شان `update_order_item_field` را رد می‌کند.
  Sony فقط `sony_account` را نگه می‌دارد.
- **serializer ها بر اساس فیلدهای واقعی مدل شکل گرفتند** (`customer.user.full_name()`
  نه `customer.full_name`؛ `CustomerListSerializer` نه `CustomerSerializer`).

---

## ۳. مشکلات مستندشده (`orders/problems.md`)

فایل `problems.md` نوشته شد: توضیح کامل منطق اپ + فهرست مشکلات به ترتیب شدت
(نبود endpoint ساخت سفارش، نبود transaction، نبود چک رول، `IsAuthenticated` تنها، …).

---

## ۴. رفع مشکلات (فاز دوم — بر اساس `orders/fix-problems.md`)

### پرمیژن — استفاده از سیستم موجود
- **`users/permissions.py`** — کلاس `IsEmployee` ارتقا یافت: حالا `is_deleted` کارمند
  را هم چک می‌کند (طبق درخواست، به‌جای ساختن کلاس جدید در hr).
- زیرساخت پرمیژن HR از قبل کامل بود (`employee_permission()` factory +
  `permission_service` + seed شامل `('orders','read'/'write')`) — **نیاز به تغییر seed
  نبود**.
- روی **۵۴ view فعال** پرمیژن اعمال شد:

| نوع view | تعداد | پرمیژن |
|---|---|---|
| Config read (List, StageDetail) | ۹ | `IsAuthenticated, IsEmployee, employee_permission('orders','read')` |
| Config write (Create, Update, Delete) | ۲۷ | `IsAuthenticated, IsEmployee, employee_permission('orders','write')` |
| Worker | ۱۸ | `IsAuthenticated, IsEmployee` |

### سرویس‌ها (`orders/services.py`)
- **`transaction.atomic()`** دور کل بدنه‌ی `execute_*` و `advance_*` — جلوگیری از
  نوشتن ناقص + لاگ.
- **چک رول کارمند** (`_check_employee_role_for_stage`) — اگر مرحله `employee_role`
  دارد، کارمند باید همان رول را داشته باشد؛ در execute و advance هر دو.
- **جلوگیری از اجرای تکراری** (`_check_not_duplicate`) — اکشن `is_required` دوباره
  اجرا نمی‌شود.
- **اعتبارسنجی `sony_account`** — چک وجود اکانت (`is_deleted=False`) + assign نشدن به
  سفارش دیگر.
- **`add_note` خالی** رد می‌شود.
- **`item_id`** موقع ثبت لاگ پاس داده می‌شود.

### مدل‌ها (`orders/models.py`) + migration `0003`
- `item_id` به `BaseOrderActionLog` اضافه شد (روی هر سه لاگ اعمال می‌شود).
- `is_deleted` به `SonyAccountOrderCategory` و `ProductOrderCategory` اضافه شد.
  > نکته: فیلدهای timestamp اضافه **نشدند** چون `auto_now_add` روی رکوردهای موجود
  > بدون default مقدور نبود؛ برای soft delete فقط `is_deleted` لازم بود.
- view های Category این دو نوع حالا `is_deleted=False` فیلتر و soft delete می‌کنند.

### schema warnings (`orders/views.py` + `serializers.py`)
- `serializer_class = Serializer` روی ۹ تا `DestroyAPIView`.
- type hint (`-> str/int/bool`) روی method field های primitive.
- `@extend_schema_field(...)` روی method field های nested (۱۳ مورد).
- guard `swagger_fake_view` روی سه view `by-stage` (چون `filterset_class`
  باعث introspect شدن queryset می‌شد و به `stage_id` نیاز داشت).

### فیلترها (`orders/filters.py` جدید)
- `SonyAccountOrderFilter` (source, type, customer, category, date range)
- `RepairOrderFilter` (customer, category, date range)
- `ProductOrderFilter` (customer, date range — مدل source/type/category ندارد)
- روی هر سه `*OrderByStageView` وصل شدند.

---

## ۵. تأیید (Verification)

- `manage.py check` → **۰ مشکل**.
- `makemigrations orders` → migration `0003` ساخته شد (تمیز، بدون prompt).
- schema generation → **exit 0**، هر ۵۴ مسیر orders موجود، **۰ warning** مربوط به
  orders (به‌جز warning عمومی و cosmetic «could not resolve authenticator
  CustomJWTAuthentication» که در کل پروژه هست).

> **migration هنوز apply نشده** — دیتابیس (`db`) از این محیط در دسترس نبود. موقع
> deploy باید `python manage.py migrate` اجرا شود.

---

## ۶. کارهای باقی‌مانده (خارج از scope این session)

- **endpoint های ساخت سفارش** — هنوز هیچ راهی برای ساخت
  `SonyAccountOrder`/`RepairOrder`/`ProductOrder` و آیتم‌هایشان وجود ندارد (بزرگ‌ترین
  gap باقی‌مانده).
- **حذف کد legacy** — فعلاً فقط کامنت شده؛ می‌تواند کامل پاک شود.
- **OpenApiAuthenticationExtension** برای `CustomJWTAuthentication` تا warning عمومی
  schema رفع شود (کل پروژه، نه فقط orders).

---

## فایل‌های تغییر یافته

```
M DrGame/urls.py
M orders/models.py
M orders/serializers.py
M orders/urls.py
M orders/views.py
M users/permissions.py
+ orders/filters.py           (جدید)
+ orders/services.py          (جدید)
+ orders/migrations/0003_*.py (جدید)
+ orders/problems.md          (جدید)
+ orders/report.md            (این فایل)
```
