# Orders App — Implementation Notes & Known Problems

این سند توضیح می‌دهد در پیاده‌سازی endpoint های اپ `orders` چه کاری انجام شد،
منطق کلی workflow چیست، و چه مشکلات/ریسک‌هایی باقی مانده که باید قبل از production حل شوند.

---

## بخش ۱ — چه کاری انجام شد (What was built)

سه نوع سفارش با ساختار کاملاً یکسان اما جدا از هم پیاده‌سازی شد:

| نوع سفارش | مدل سفارش | مدل آیتم | مدل دستگاه/کنسول |
|-----------|-----------|----------|------------------|
| Sony Account | `SonyAccountOrder` | `SonyAccountOrderItem` | `SonyAccountOrderConsole` |
| Repair | `RepairOrder` | — | `RepairOrderDevice` |
| Product | `ProductOrder` | `ProductOrderItem` | — |

### فایل‌ها

- **`orders/services.py`** (جدید) — منطق workflow. برای هر نوع سفارش دو تابع:
  - `execute_*_order_action(...)` — اجرای یک اکشن روی سفارش + ثبت لاگ.
  - `advance_*_order_stage(...)` — انتقال سفارش به مرحله بعدی بعد از چک کردن اکشن‌های اجباری.
  - یک helper مشترک `_advance_stage_generic(...)` که منطق تکراری advance را متمرکز می‌کند.
- **`orders/serializers.py`** — یک بخش جدید (WORKFLOW) در انتهای فایل، تقسیم‌شده با کامنت به سه section.
  کد legacy قدیمی (که به مدل‌های حذف‌شده‌ی `accounting` وابسته بود) داخل `''' LEGACY ... '''` کامنت شد.
- **`orders/views.py`** — بخش WORKFLOW در انتهای فایل. کد legacy قدیمی هم اینجا داخل `''' LEGACY '''` کامنت شد.
- **`orders/urls.py`** — بازنویسی کامل، ۴۲ مسیر با `name=` (الگو: `<type>-<resource>-<action>`).
- **`DrGame/urls.py`** — خط `path('orders/', include('orders.urls'))` از حالت کامنت خارج شد.

### الگوی endpoint ها (برای هر نوع سفارش تکرار می‌شود)

**Config (مدیر) — مدیریت ساختار workflow:**
```
GET    /orders/{type}/categories/                     لیست دسته‌بندی‌ها
POST   /orders/{type}/categories/create/              ایجاد دسته‌بندی
PATCH  /orders/{type}/categories/<pk>/update/         ویرایش
DELETE /orders/{type}/categories/<pk>/delete/         حذف
GET    /orders/{type}/categories/<id>/stages/         لیست مراحل دسته‌بندی
POST   /orders/{type}/stages/create/                  ایجاد مرحله
GET    /orders/{type}/stages/<pk>/                    جزئیات مرحله + اکشن‌ها
PATCH  /orders/{type}/stages/<pk>/update/
DELETE /orders/{type}/stages/<pk>/delete/
POST   /orders/{type}/stage-actions/create/           ایجاد اکشن برای مرحله
PATCH  /orders/{type}/stage-actions/<pk>/update/
DELETE /orders/{type}/stage-actions/<pk>/delete/
```

**Worker (کارمند) — کار روزانه با سفارش‌ها:**
```
GET  /orders/{type}/my-stages/                        مراحلی که رول این کارمند بهشون دسترسی داره
GET  /orders/{type}/orders/by-stage/<stage_id>/       لیست کارتی سفارش‌های یک مرحله
GET  /orders/{type}/orders/<pk>/                      جزئیات کامل سفارش
GET  /orders/{type}/orders/<order_id>/actions/        اکشن‌های مرحله فعلی + وضعیت انجام
POST /orders/{type}/orders/<order_id>/execute-action/ اجرای یک اکشن
POST /orders/{type}/orders/<order_id>/advance-stage/  انتقال به مرحله بعد
```

---

## بخش ۲ — منطق کلی (Logic of the orders app)

### مدل ذهنی: هر نوع سفارش یک state machine قابل‌تنظیم است

```
Category (دسته‌بندی)
   └── Stage ها (مراحل، مرتب با فیلد order، هرکدام به یک EmployeeRole وصل)
          └── StageAction ها (کارهایی که در آن مرحله باید انجام شوند)
```

- **Category** یک نوع مشخص از سفارش را تعریف می‌کند (مثلاً «اجاره اکانت آنلاین ۳۰ روزه»).
- **Stage** یک مرحله در مسیر انجام سفارش است. با `order` مرتب می‌شود و با `is_start` / `is_end` ابتدا و انتهای مسیر مشخص می‌شود. هر Stage به یک `EmployeeRole` وصل است — یعنی فقط کارمندهای دارای آن رول آن مرحله را می‌بینند.
- **StageAction** یک کار مشخص در آن مرحله است. `action_type` تعیین می‌کند چه اتفاقی می‌افتد:
  - `update_order_field` — یک فیلد روی خود سفارش را آپدیت می‌کند (مثل `description`).
  - `update_order_item_field` — یک فیلد روی آیتم سفارش را آپدیت می‌کند (فقط Sony: `sony_account`).
  - `manual_confirm` — فقط یک تایید دستی، هیچ فیلدی آپدیت نمی‌شود.
  - `add_note` — یک یادداشت ثبت می‌کند.
  - `target_field` مشخص می‌کند کدام فیلد آپدیت شود (فقط برای دو نوع اول معنی دارد).
  - `is_required` تعیین می‌کند آیا این اکشن برای رفتن به مرحله بعد اجباری است.

### جریان کار کارمند (front-end flow)

```
۱. GET /orders/sony-account/my-stages/
     → کارمند لیست مراحلی که رولش بهشون دسترسی داره رو می‌بینه

۲. برای هر stage: GET .../orders/by-stage/<stage_id>/
     → لیست کارتی سفارش‌هایی که الان در آن مرحله‌اند
     → هر کارت pending_actions_count داره (چند اکشن اجباری مونده)

۳. کلیک روی سفارش: GET .../orders/<order_id>/
     → جزئیات کامل + آیتم‌ها + لاگ‌ها

۴. GET .../orders/<order_id>/actions/
     → اکشن‌های مرحله فعلی + is_done هر کدام
     → فرانت از action_type و target_field می‌فهمه چه فرمی نشون بده

۵. POST .../orders/<order_id>/execute-action/
     {"action_id": 7, "value": 42, "item_id": 15}
     → سرویس فیلد رو آپدیت می‌کنه و یک ActionLog ثبت می‌کنه

۶. POST .../orders/<order_id>/advance-stage/
     {"note": "..."}
     → چک می‌کنه همه اکشن‌های اجباری انجام شدن، بعد سفارش رو به مرحله بعد می‌بره
     → یک StageLog ثبت می‌کنه
```

### دو نکته مرکزی منطق

1. **«انجام‌شدن» یک اکشن = وجود یک `ActionLog` برای آن اکشن روی آن سفارش.** هیچ فیلد `is_done` روی خود اکشن ذخیره نمی‌شود؛ وضعیت به‌صورت مشتق از لاگ‌ها محاسبه می‌شود.
2. **advance_stage قبل از انتقال چک می‌کند:** همه‌ی `is_required=True` اکشن‌های مرحله‌ی فعلی حداقل یک لاگ داشته باشند، و مرحله فعلی `is_end` نباشد، و مرحله بعدی (`order + 1` در همان category) وجود داشته باشد.

---

## بخش ۳ — مشکلات و ریسک‌ها (Known problems)

### 🔴 بحرانی (باید قبل از استفاده حل شود)

#### ۱. هیچ endpoint ای برای *ساختن* سفارش وجود ندارد
کل این workflow فقط سفارش‌های **موجود** را مدیریت می‌کند. هیچ‌جا `SonyAccountOrder` / `RepairOrder` / `ProductOrder` ساخته نمی‌شود و هیچ‌جا `stage` اولیه (مرحله‌ی `is_start`) روی سفارش ست نمی‌شود. تا وقتی این تکمیل نشود، `by-stage` و بقیه endpoint ها همیشه خالی برمی‌گردند. باید مشخص شود سفارش کجا ساخته می‌شود (سایت؟ تلگرام؟ پنل کارمند؟) و در لحظه‌ی ساخت `stage = category.stages.filter(is_start=True)` ست شود.

#### ۲. `request.user.employee` بدون گارد → کرش برای کاربر غیرکارمند
همه‌ی view های worker مستقیم `self.request.user.employee` را صدا می‌زنند. اما permission فقط `IsAuthenticated` است. اگر یک **مشتری** (که `employee` ندارد) لاگین کند و این endpoint ها را صدا بزند، `RelatedObjectDoesNotExist` می‌خورد → خطای ۵۰۰. باید یا permission به `IsEmployee` تغییر کند یا `hasattr(user, 'employee')` چک شود.

#### ۳. هیچ کنترل نقش/دسترسی واقعی نیست
طبق spec فعلاً همه‌چیز `IsAuthenticated` است. یعنی **هر کاربر لاگین‌شده** می‌تواند endpoint های config مدیر را صدا بزند (ساخت/حذف category و stage). همچنین کارمند می‌تواند روی سفارشی که در مرحله‌ای *خارج از رول خودش* است اکشن اجرا کند — `execute_action` فقط چک می‌کند اکشن متعلق به stage فعلی سفارش باشد، اما چک نمی‌کند که `order.stage.employee_role` با رول این کارمند بخورد.

### 🟠 مهم (باگ‌های منطقی)

#### ۴. عدم اتمی بودن (no transaction)
در `execute_action`، ابتدا فیلد سفارش/آیتم ذخیره می‌شود و **بعد** لاگ ساخته می‌شود، بدون `transaction.atomic()`. اگر ساخت لاگ خطا بخورد، آپدیت فیلد باقی می‌ماند ولی لاگی ثبت نشده → وضعیت ناسازگار. باید کل عملیات در یک `with transaction.atomic():` قرار گیرد.

#### ۵. اکشن‌ها را می‌شود چند بار اجرا کرد
هیچ چیزی جلوی اجرای دوباره‌ی یک اکشن را نمی‌گیرد. هر بار یک `ActionLog` جدید ساخته می‌شود. برای اکشن‌هایی مثل `update_order_field` شاید مشکلی نباشد، اما لاگ‌ها تکراری/شلوغ می‌شوند و `is_done` همیشه true می‌ماند حتی اگر منطقاً باید یک‌بار انجام شود.

#### ۶. `value` هنگام assign کردن `sony_account` اعتبارسنجی نمی‌شود
در Sony، `_sony_update_order_item_field` مقدار `value` را مستقیم به `item.sony_account_id` می‌دهد. اگر `value` یک id نامعتبر باشد (اکانتی که وجود ندارد یا `is_deleted=True`)، یا خطای integrity می‌خورد یا به اکانت حذف‌شده وصل می‌شود. باید وجود `SonyAccount` با `is_deleted=False` چک شود.

#### ۷. `add_note` با ورودی خالی لاگ خالی می‌سازد
اگر `action_type == 'add_note'` و نه `value` و نه `note` داده شود، یک `ActionLog` با `note=''` ساخته می‌شود که به‌عنوان «انجام‌شده» حساب می‌شود ولی محتوایی ندارد.

### 🟡 جزئی / کیفیت کد

#### ۸. حذف Category در Sony و Product حذف واقعی (hard delete) است
مدل‌های `SonyAccountOrderCategory` و `ProductOrderCategory` فیلد `is_deleted` ندارند (برخلاف بقیه مدل‌ها که soft delete هستند). پس delete آن‌ها ردیف را واقعاً پاک می‌کند و به‌خاطر `CASCADE` روی stage ها، کل مراحل و اکشن‌های آن category هم پاک می‌شوند. `RepairOrderCategory` این فیلد را دارد و soft delete است — این ناسازگاری بهتر است یکدست شود.

#### ۹. تفاوت `is_done` بین spec و مدل‌ها
فایل `orders.md` فرض کرده بود آیتم‌ها فیلد `is_done` دارند، ولی هیچ‌کدام از مدل‌های آیتم آن را ندارند (طبق تصمیم: مدل منبع حقیقت است). نتیجه: برای **Repair و Product** هیچ فیلد آیتمی قابل آپدیت نیست، پس serializer آن‌ها `update_order_item_field` را کلاً رد می‌کند. اگر واقعاً به «تیک‌زدن آیتم به‌عنوان انجام‌شده» نیاز است، باید فیلد `is_done` به مدل‌ها اضافه و migration ساخته شود.

#### ۱۰. warning های cosmetic در schema
سه دسته warning در `drf-spectacular` هست که در کل پروژه (از جمله `accounting`) وجود دارد و runtime را خراب نمی‌کند:
- `could not resolve authenticator CustomJWTAuthentication` — نبود `OpenApiAuthenticationExtension` برای auth سفارشی.
- `DeleteView should include serializer_class` — روی `DestroyAPIView` ها.
- `unable to resolve type hint for get_is_done/get_actions` — می‌شود با `@extend_schema_field` رفع کرد.

#### ۱۱. نبود pagination/filter روی لیست‌ها
spec به `django-filter` اشاره کرده بود ولی روی endpoint های فعلی هیچ `filterset_class` یا `SearchFilter` ست نشده. لیست‌ها فقط pagination پیش‌فرض پروژه را دارند.

---

## خلاصه‌ی اولویت‌بندی رفع

| # | مشکل | اولویت |
|---|------|--------|
| ۱ | نبود endpoint ساخت سفارش + ست‌نشدن stage اولیه | 🔴 |
| ۲ | کرش `user.employee` برای غیرکارمند | 🔴 |
| ۳ | نبود کنترل نقش (config مدیر + رول stage) | 🔴 |
| ۴ | نبود transaction در execute_action | 🟠 |
| ۵ | اجرای تکراری اکشن | 🟠 |
| ۶ | اعتبارسنجی نشدن sony_account id | 🟠 |
| ۷ | لاگ خالی add_note | 🟠 |
| ۸ | ناسازگاری soft/hard delete در category ها | 🟡 |
| ۹ | نبود is_done روی آیتم‌ها | 🟡 |
| ۱۰ | warning های cosmetic schema | 🟡 |
| ۱۱ | نبود filter/pagination سفارشی | 🟡 |