# منابع انسانی — مستندات فرانت‌اند

---

## ساختار کلی

سکشن **منابع انسانی** از دو بخش اصلی تشکیل شده:

1. **پرونده کارمندان** — لیست کارمندان در سمت چپ و پروفایل کامل کارمند انتخاب‌شده در سمت راست (دقیقاً مشابه پرونده مشتریان)
2. **مدیریت منابع انسانی** — یک صفحه با تب‌بندی برای CRUD روی: استخدام، حضور و غیاب، درخواست‌ها، فیش حقوقی، اضافه‌کاری

> تمام endpoint های این سکشن با prefix `/hr/` شروع می‌شوند.

---

## بخش اول — پرونده کارمندان

### چیدمان کلی

چیدمان این بخش دقیقاً مشابه بخش پرونده مشتریان است:

- **سمت چپ:** لیست کارمندان با سرچ‌بار و فیلتر
- **سمت راست:** پروفایل کامل کارمند انتخاب‌شده (با کلیک روی هر کارمند)

---

### پنل چپ — لیست کارمندان

**ویژگی‌ها:**
- سرچ‌بار و فیلتر بالای لیست
- هر آیتم لیست شامل: نام کامل، کد پرسنلی، تصویر پروفایل، نقش‌ها

**Endpoint:**

```
GET /hr/employees/
```

**فیلترها (query param):**

| پارامتر | توضیح |
|---|---|
| `role` | آیدی نقش (EmployeeRole) |
| `first_name` | جستجوی نام (icontains) |
| `last_name` | جستجوی نام خانوادگی (icontains) |
| `national_code` | کد ملی (تطابق دقیق) |
| `employee_id` | کد پرسنلی (تطابق دقیق) |

> برای سرچ‌بار می‌توانید از `first_name` / `last_name` استفاده کنید.

---

### پنل راست — پروفایل کارمند

با کلیک روی هر کارمند، پنل راست پروفایل کامل را نمایش می‌دهد:

```
GET /hr/employees/{id}/
```

خروجی این endpoint شامل تمام اطلاعات مورد نیاز پروفایل است:

#### ۱. اطلاعات پایه
نام کامل، نام، نام خانوادگی، کد ملی، تاریخ تولد، کد پرسنلی، تصویر پروفایل، وضعیت پورسانت (`has_commission` / `commission_amount`)، نقش‌ها (`roles_detail`)

#### ۲. موجودی کیف پول
`wallet_balance` — موجودی کیف پول کارمند (از طریق یوزر کارمند خوانده می‌شود، در صورت نبود کیف پول مقدار `0`)

#### ۳. آخرین تردد
`last_arrival` — آبجکت شامل `check_in` و `check_out` آخرین رکورد حضور (یا `null`)

#### ۴. آمار خلاصه
فیلد `stats` شامل:

| کلید | توضیح |
|---|---|
| `total_requests` | تعداد کل درخواست‌ها |
| `pending_requests` | درخواست‌های در انتظار بررسی |
| `total_files` | تعداد فایل‌های پرونده |
| `total_overtimes` | تعداد کل اضافه‌کاری‌ها |
| `pending_overtimes` | اضافه‌کاری‌های تاییدنشده |

---

### فایل‌های کارمند (داخل پروفایل)

بخشی از پروفایل کارمند، لیست فایل‌های اسکن‌شده (قرارداد، مدارک و...) است:

```
GET    /hr/employees/{employee_id}/files/   # لیست فایل‌های کارمند
POST   /hr/employees/files/create/          # آپلود فایل جدید
DELETE /hr/employees/files/{id}/delete/     # حذف فایل
```

> هنگام آپلود (`POST`)، فیلد `employee` (آیدی کارمند) در بدنه ارسال می‌شود. آپلود به‌صورت `multipart/form-data` انجام می‌گیرد.

---

### عملیات CRUD روی کارمند

| عملیات | Method | Endpoint |
|---|---|---|
| افزودن | POST | `/hr/employees/create/` |
| ویرایش | PATCH | `/hr/employees/{id}/update/` |
| حذف | DELETE | `/hr/employees/{id}/delete/` |

**فیلدهای ایجاد/ویرایش کارمند:**
`user` (آیدی یوزر)، `first_name`، `last_name`، `national_code`، `birth_date`، `employee_id`، `profile_picture`، `has_commission`، `commission_amount`، `roles` (لیست آیدی نقش‌ها)

---

## بخش دوم — مدیریت منابع انسانی (تب‌بندی)

این بخش یک صفحه با چند تب است. هر تب یک موجودیت مستقل با CRUD خودش دارد.

| تب | توضیح |
|---|---|
| استخدام | مدیریت رزومه‌های دریافتی |
| حضور و غیاب | ثبت و ویرایش ترددها |
| درخواست‌ها | درخواست‌های کارمندان + مدیریت انواع درخواست |
| فیش حقوقی | صدور و مشاهده فیش‌های حقوقی |
| اضافه‌کاری | ثبت و تایید اضافه‌کاری |

---

### تب استخدام (Recruitment)

لیست رزومه‌های دریافتی. با کلیک روی هر رزومه، جزئیات کامل + فایل رزومه نمایش داده می‌شود.

| عملیات | Method | Endpoint |
|---|---|---|
| لیست | GET | `/hr/resumes/` |
| جزئیات | GET | `/hr/resumes/{id}/` |
| ثبت رزومه | POST | `/hr/resumes/create/` |
| حذف | DELETE | `/hr/resumes/{id}/delete/` |

**فیلدها:** `first_name`، `last_name`، `national_code`، `birth_date`، `phone_number`، `description`، `resume_file`، `user`
خروجی شامل `user_detail` (آبجکت `id` / `phone` / `full_name`) است.

---

### تب حضور و غیاب (Attendance)

| عملیات | Method | Endpoint |
|---|---|---|
| لیست | GET | `/hr/arrivals/` |
| ثبت تردد | POST | `/hr/arrivals/create/` |
| ویرایش | PATCH | `/hr/arrivals/{id}/update/` |
| حذف | DELETE | `/hr/arrivals/{id}/delete/` |

**فیلترها (query param):** `employee` (آیدی کارمند)، `date_from`، `date_to` (بازه تاریخ روی `check_in`)

**فیلدها:** `employee`، `check_in`، `check_out`
خروجی لیست شامل `employee_detail` و `duration_minutes` (مدت حضور به دقیقه، در صورت وجود `check_out`) است.

---

### تب درخواست‌ها (Requests)

این تب دو زیربخش دارد: **درخواست‌ها** و **انواع درخواست**.

#### درخواست‌ها

| عملیات | Method | Endpoint |
|---|---|---|
| لیست | GET | `/hr/requests/` |
| جزئیات | GET | `/hr/requests/{id}/` |
| ثبت درخواست | POST | `/hr/requests/create/` |
| تغییر وضعیت | PATCH | `/hr/requests/{id}/status/` |
| حذف | DELETE | `/hr/requests/{id}/delete/` |

**فیلترها (query param):** `employee`، `status`، `request_type` (آیدی)

**فیلدهای ثبت:** `employee`، `title`، `request_type`، `description`
**تغییر وضعیت:** فقط فیلد `status` با یکی از مقادیر `waiting` / `accepted` / `rejected`
خروجی لیست/جزئیات شامل `employee_detail` و `request_type_detail` است.

#### انواع درخواست (Request Types)

| عملیات | Method | Endpoint |
|---|---|---|
| لیست | GET | `/hr/request-types/` |
| ایجاد | POST | `/hr/request-types/create/` |
| حذف | DELETE | `/hr/request-types/{id}/delete/` |

**فیلدها:** `title`، `needs_approval`، `description`

---

### تب فیش حقوقی (Payroll)

هر فیش حقوقی در واقع یک `Invoice` با `is_payroll=True` به‌همراه جزئیات حقوقی (`PayrollDetail`) است. مبلغ نهایی فیش (`amount`) هنگام صدور از روی `net_salary` محاسبه می‌شود.

| عملیات | Method | Endpoint |
|---|---|---|
| لیست | GET | `/hr/payrolls/` |
| جزئیات | GET | `/hr/payrolls/{id}/` |
| صدور فیش | POST | `/hr/payrolls/create/` |
| پرداخت‌های یک فیش | GET | `/hr/payrolls/{invoice_id}/transactions/` |

**خروجی جزئیات فیش (`payroll_detail`)** شامل درآمدها و کسورات و همچنین سه فیلد محاسبه‌شده read-only است:
`gross_salary` (جمع درآمد)، `total_deductions` (جمع کسورات)، `net_salary` (خالص)

**فیلدهای صدور فیش (POST):**

- فیلدهای فاکتور: `account_side` (طرف حساب — کارمند)، `category`، `discount`، `description`
- فیلدهای حقوقی: `base_salary`، `overtime_amount`، `bonus`، `housing_allowance`، `food_allowance`، `transportation_allowance`، `insurance_deduction`، `tax_deduction`، `loan_deduction`، `other_deductions`، `work_days`، `overtime_hours`، `payroll_description`

**لیست پرداخت‌های فیش:** رکوردهای `Transaction` مربوط به آن فاکتور را برمی‌گرداند (`amount`, `direction`, `bank_account_detail`, `description`, `created_at`).

---

### تب اضافه‌کاری (Overtime)

| عملیات | Method | Endpoint |
|---|---|---|
| لیست | GET | `/hr/overtimes/` |
| ثبت | POST | `/hr/overtimes/create/` |
| تایید | PATCH | `/hr/overtimes/{id}/approve/` |
| حذف | DELETE | `/hr/overtimes/{id}/delete/` |

**فیلترها (query param):** `employee`، `date_from`، `date_to`، `is_approved`

**فیلدهای ثبت:** `employee`، `date`، `hours`، `description`
> فیلدهای `is_approved` و `approved_by` read-only هستند و فقط از طریق endpoint تایید ست می‌شوند.

**تایید:** با `PATCH` روی endpoint تایید، فیلد `is_approved` روی `true` و `approved_by` روی کارمند لاگین‌کرده ست می‌شود (بدنه لازم نیست).

---

## نقش‌ها و دسترسی‌ها (Roles & Permissions)

این بخش زیرساخت سیستم دسترسی است و معمولاً در تنظیمات مدیریت استفاده می‌شود:

```
GET    /hr/permissions/              # لیست تمام پرمیژن‌های سیستم
GET    /hr/my-permissions/           # پرمیژن‌های یوزر لاگین‌کرده (فرانت موقع لاگین صدا می‌زند)
GET    /hr/roles/                    # لیست نقش‌ها
POST   /hr/roles/create/             # ایجاد نقش
GET    /hr/roles/{id}/               # جزئیات نقش
PATCH  /hr/roles/{id}/update/        # ویرایش نقش
DELETE /hr/roles/{id}/delete/        # حذف نقش
```

> `GET /hr/my-permissions/` را فرانت هنگام لاگین صدا می‌زند تا دسترسی‌های کاربر را بگیرد.

---

## نکات کلی

- تمام حذف‌ها **soft delete** هستند (پاسخ `204 No Content`)
- تمام لیست‌ها با `LimitOffsetPagination` صفحه‌بندی می‌شوند (`PAGE_SIZE=10`) — از query param های `limit` و `offset` استفاده کنید
- در serializer ها هر فیلد رابطه‌ای هم به‌صورت آیدی برای نوشتن و هم به‌صورت `{field}_detail` برای خواندن ارائه می‌شود
- تمام endpoint ها فعلاً فقط `IsAuthenticated` می‌خواهند؛ پرمیژن دقیق‌تر بعداً اعمال می‌شود
- آپلودها (فایل کارمند، رزومه، تصویر پروفایل) با `multipart/form-data` ارسال می‌شوند
