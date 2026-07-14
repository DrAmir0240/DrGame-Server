# ماژول انبارداری — مستندات فرانت‌اند

> **Base URL:** `/inventory/`

---

## ساختار کلی

ماژول انبارداری از دو بخش اصلی تشکیل شده است:

1. **کالاها** — مدیریت کالاها، دسته‌بندی‌ها، موجودیت‌ها و تصاویر
2. **تامین‌کنندگان و گردش انبار** — مدیریت تامین‌کنندگان و ثبت ورود/خروج کالا

---

## بخش اول — کالاها

این بخش دارای دو تب است.

---

### تب ۱ — لیست کالاها

#### نمای کلی
- نمایش لیست کالاها به همراه **فیلتربندی کامل** و **جستجو**
- نمایش **آمار انبار** در بالای صفحه (کارت‌های وضعیت)
- دکمه افزودن کالای جدید
- کلیک روی هر ردیف، کاربر را به **صفحه جزئیات کالا** هدایت می‌کند (نه مودال)

#### اندپوینت‌ها

| عملیات | متد | آدرس |
|--------|-----|-------|
| لیست کالاها با فیلتر | `GET` | `/inventory/products/` |
| افزودن کالا | `POST` | `/inventory/products/` |
| جستجوی کالا | `GET` | `/inventory/products/search/?search=` |
| آمار انبار | `GET` | `/inventory/stats/` |
| دراپ‌داون ساخت کالا (تامین‌کننده + دسته‌بندی) | `GET` | `/inventory/products/dropdown/` |

#### فیلترهای موجود روی لیست کالاها

| پارامتر | نوع | توضیح |
|--------|-----|-------|
| `search` | `string` | جستجو در عنوان و توضیحات |
| `title` | `string` | فیلتر عنوان (icontains) |
| `description` | `string` | فیلتر توضیحات (icontains) |
| `price_min` | `number` | حداقل قیمت |
| `price_max` | `number` | حداکثر قیمت |
| `stock_min` | `number` | حداقل موجودی |
| `stock_max` | `number` | حداکثر موجودی |
| `units_sold_min` | `number` | حداقل تعداد فروخته‌شده |
| `units_sold_max` | `number` | حداکثر تعداد فروخته‌شده |
| `category` | `integer` | شناسه دسته‌بندی |
| `category_title` | `string` | عنوان دسته‌بندی (icontains) |
| `supplier` | `integer` | شناسه تامین‌کننده |
| `created_at_after` | `datetime` | ایجادشده از تاریخ |
| `created_at_before` | `datetime` | ایجادشده تا تاریخ |
| `ordering` | `string` | مرتب‌سازی: `title`, `price`, `stock`, `units_sold`, `created_at` |

#### کارت‌های آمار انبار

پاسخ اندپوینت `/inventory/stats/` سه وضعیت موجودی را برمی‌گرداند:

| فیلد | رنگ | شرط |
|-----|-----|-----|
| `green_count` | 🟢 سبز | `stock > min_stock` |
| `yellow_count` | 🟡 زرد | `0 < stock ≤ min_stock` |
| `red_count` | 🔴 قرمز | `stock == 0` |
| `total_inventory_value` | — | ارزش کل موجودی انبار |

---

#### صفحه جزئیات کالا

این صفحه به جای مودال، در یک **صفحه مستقل** باز می‌شود زیرا شامل اطلاعات تودرتو است.

##### اندپوینت‌ها

| عملیات | متد | آدرس |
|--------|-----|-------|
| دریافت جزئیات کالا | `GET` | `/inventory/products/{id}/` |
| ویرایش کالا | `PATCH` | `/inventory/products/{id}/` |
| حذف کالا | `DELETE` | `/inventory/products/{id}/` |

##### زیربخش — موجودیت‌های کالا (ProductEntity)

لیست موجودیت‌های هر کالا در پایین صفحه جزئیات نمایش داده می‌شود و CRUD کامل از همین صفحه انجام می‌شود.

| عملیات | متد | آدرس |
|--------|-----|-------|
| لیست موجودیت‌ها | `GET` | `/inventory/products/{id}/entities/` |
| افزودن موجودیت | `POST` | `/inventory/products/{id}/entities/` |
| جزئیات موجودیت | `GET` | `/inventory/products/{id}/entities/{entity_id}/` |
| ویرایش موجودیت | `PATCH` | `/inventory/products/{id}/entities/{entity_id}/` |
| حذف موجودیت | `DELETE` | `/inventory/products/{id}/entities/{entity_id}/` |

##### زیربخش — تصاویر کالا (ProductImage)

مدیریت تصاویر به صورت مستقل از فرم اصلی کالا انجام می‌شود تا منطق آپلود ساده‌تر بماند.

| عملیات | متد | آدرس |
|--------|-----|-------|
| لیست تصاویر | `GET` | `/inventory/products/{id}/images/` |
| افزودن تصویر | `POST` | `/inventory/products/{id}/images/` |
| حذف تصویر | `DELETE` | `/inventory/products/{id}/images/{image_id}/` |

> **نکته:** آپلود تصویر با `multipart/form-data` انجام می‌شود.

---

### تب ۲ — دسته‌بندی کالاها

CRUD کامل دسته‌بندی‌ها در همین تب انجام می‌شود.

| عملیات | متد | آدرس |
|--------|-----|-------|
| لیست دسته‌بندی‌ها | `GET` | `/inventory/categories/` |
| افزودن دسته‌بندی | `POST` | `/inventory/categories/` |
| جزئیات / ویرایش / حذف | `GET / PATCH / DELETE` | `/inventory/categories/{id}/` |

---

## بخش دوم — تامین‌کنندگان و گردش انبار

این بخش دارای دو تب است.

---

### تب ۱ — گردش انبار

CRUD کامل ورود و خروج کالا از انبار.

| عملیات | متد | آدرس |
|--------|-----|-------|
| لیست گردش انبار با فیلتر | `GET` | `/inventory/movements/` |
| ثبت حرکت جدید | `POST` | `/inventory/movements/` |
| جزئیات / ویرایش / حذف | `GET / PATCH / DELETE` | `/inventory/movements/{id}/` |
| دراپ‌داون گردش انبار | `GET` | `/inventory/movements/dropdown/` |

#### فیلترهای گردش انبار

| پارامتر | نوع | توضیح |
|--------|-----|-------|
| `direction` | `in` / `out` | جهت حرکت: ورودی یا خروجی |
| `product` | `integer` | شناسه کالا |
| `product_title` | `string` | عنوان کالا (icontains) |
| `product_entity` | `integer` | شناسه موجودیت |
| `product_entity_uni_id` | `string` | شناسه یکتای موجودیت (icontains) |
| `created_at_after` | `datetime` | از تاریخ |
| `created_at_before` | `datetime` | تا تاریخ |
| `ordering` | `string` | مرتب‌سازی: `created_at`, `direction` |

---

### تب ۲ — تامین‌کنندگان

CRUD کامل تامین‌کنندگان.

| عملیات | متد | آدرس |
|--------|-----|-------|
| لیست تامین‌کنندگان | `GET` | `/inventory/suppliers/` |
| افزودن تامین‌کننده | `POST` | `/inventory/suppliers/` |
| جزئیات / ویرایش / حذف | `GET / PATCH / DELETE` | `/inventory/suppliers/{id}/` |

#### فیلترهای تامین‌کنندگان

| پارامتر | نوع | توضیح |
|--------|-----|-------|
| `type` | `real` / `legal` | نوع: حقیقی یا حقوقی |
| `search` | `string` | جستجو در نام، تلفن، کد ملی، شناسه مالیاتی |
| `ordering` | `string` | مرتب‌سازی: `name`, `created_at` |

---

## نکات پیاده‌سازی

- تمام حذف‌ها **Soft Delete** هستند — رکورد از دیتابیس پاک نمی‌شود.
- پاسخ حذف همیشه `204 No Content` است.
- فیلدهای `is_deleted`، `created_at`، `updated_at`، `stock` و `units_sold` در همه فرم‌ها **read-only** هستند.
- تصاویر با `multipart/form-data` ارسال می‌شوند، بقیه endpointها `application/json`.
- مرتب‌سازی نزولی با پیشوند `-` انجام می‌شود، مثلاً `ordering=-created_at`.