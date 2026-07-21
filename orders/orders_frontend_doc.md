# Orders — داکیومنت پیاده‌سازی فرانت

---

## ساختار کلی بخش‌ها

چهار بخش اصلی داریم:

```
1. کانفیگ سفارشات     ← فقط مدیر
2. سفارشات سونی اکانت ← کارمند
3. سفارشات کالا        ← کارمند
4. سفارشات تعمیرات    ← کارمند
```

بخش‌های ۲، ۳ و ۴ ساختار یکسانی دارند — فقط نوع سفارش و endpoint فرق می‌کند.

---

## بخش ۱ — کانفیگ سفارشات

### ساختار تب‌ها

```
کانفیگ سفارشات
├── تب: اکانت سونی
├── تب: کالا
└── تب: تعمیرات
```

هر تب ساختار یکسانی دارد — فقط endpoint فرق می‌کند.

### داخل هر تب کانفیگ

سه سطح سلسله‌مراتبی:

```
Category (لیست + CRUD)
    └── Stage های آن Category (لیست + CRUD)
            └── Action های آن Stage (لیست + CRUD)
```

### جریان UI

**سطح اول — Category:**
- لیست category ها نمایش داده می‌شود
- دکمه افزودن category جدید
- روی هر category دکمه ویرایش و حذف
- با کلیک روی category، stage های آن باز می‌شود (expand یا navigate)

**سطح دوم — Stage:**
- لیست stage های آن category با ترتیب `order`
- فیلدهای stage: `title`، `description`، `order`، `employee_role`، `is_start`، `is_end`
- دکمه افزودن stage جدید
- روی هر stage دکمه ویرایش و حذف
- با کلیک روی stage، action های آن باز می‌شود

**سطح سوم — Action:**
- لیست action های آن stage با ترتیب `order`
- فیلدهای action: `title`، `action_type`، `target_field`، `is_required`، `order`
- دکمه افزودن action جدید
- روی هر action دکمه ویرایش و حذف

### نکته مهم برای فرم action

فیلد `target_field` فقط وقتی `action_type` برابر `update_order_field` یا `update_order_item_field` باشد نمایش داده شود.

مقادیر مجاز `target_field` بر اساس `action_type` و نوع سفارش:

```
سونی اکانت:
  update_order_field      → ['description']
  update_order_item_field → ['sony_account']

تعمیرات:
  update_order_field      → ['description', 'repair_fee', 'final_amount']
  update_order_item_field → [] (خالی — فعلاً پشتیبانی نمی‌شود)

کالا:
  update_order_field      → ['description']
  update_order_item_field → [] (خالی — فعلاً پشتیبانی نمی‌شود)
```

---

## بخش‌های ۲، ۳، ۴ — پنل کارمند (سفارشات)

ساختار هر سه بخش یکسان است. در ادامه با مثال سونی اکانت توضیح داده می‌شود.

### ساختار تب‌ها — داینامیک

```
سفارشات سونی اکانت
├── تب: [Category 1 title]   ← از API می‌آید
├── تب: [Category 2 title]   ← از API می‌آید
└── تب: [Category N title]   ← از API می‌آید
```

تب‌ها داینامیک هستند — تعداد و عنوان آن‌ها از API می‌آید.

### جریان بارگذاری صفحه

```
① GET /orders/sony-account/categories/
   → لیست category هایی که این کارمند دسترسی دارد
   → برای هر category یک تب بساز

② به ازای هر category:
   GET /orders/sony-account/categories/<id>/stages/
   → لیست stage های آن category
   → به عنوان تب‌های داخلی یا فیلتر نمایش بده

③ به ازای هر stage:
   GET /orders/sony-account/orders/by-stage/<stage_id>/
   → لیست کارتی سفارشات آن stage
```

> **نکته بارگذاری:** Call های step ② و ③ می‌توانند lazy باشند — یعنی فقط وقتی کاربر روی آن تب کلیک کرد بارگذاری شوند، نه همه با هم.

### ساختار داخل هر تب Category

داخل هر category تب، stage ها به صورت تب‌های داخلی یا dropdown نمایش داده می‌شوند:

```
[Category: فروش اکانت آنلاین]
    ├── [Stage: ثبت سفارش]     → N سفارش
    ├── [Stage: انجام پروسه]   → M سفارش
    └── [Stage: تحویل]         → K سفارش
```

داخل هر stage تب، لیست کارتی سفارشات نمایش داده می‌شود.

### کارت سفارش

هر کارت این اطلاعات را نمایش می‌دهد:

```
┌─────────────────────────────────┐
│  سفارش #12                      │
│  مشتری: علی رضایی               │
│  دسته‌بندی: فروش آنلاین          │
│  مرحله: انجام پروسه             │
│  مبلغ: ۵۰۰,۰۰۰ تومان           │
│  تاریخ: ۱۴۰۳/۰۵/۱۲             │
│  اکشن‌های باقیمانده: ۲          │
└─────────────────────────────────┘
```

فیلد `pending_actions_count` تعداد اکشن‌های اجباری انجام‌نشده را نشان می‌دهد.

### Modal/Drawer سفارش

با کلیک روی هر کارت، یک modal یا drawer باز می‌شود که سه بخش دارد:

**بخش اول — اطلاعات سفارش:**
از endpoint `GET /orders/sony-account/orders/<id>/` می‌آید.
شامل: مشتری، category، stage فعلی، آیتم‌ها، کنسول‌ها، تاریخچه stage ها.

**بخش دوم — اکشن‌های قابل انجام:**
از endpoint `GET /orders/sony-account/orders/<id>/actions/` می‌آید.

برای هر action بر اساس `action_type` کامپوننت مناسب نمایش داده می‌شود:

```
action_type == 'manual_confirm'
    → دکمه «تایید» — بدون input اضافه
    → POST execute-action با: {action_id, note (اختیاری)}

action_type == 'add_note'
    → textarea برای متن یادداشت
    → POST execute-action با: {action_id, value: "متن یادداشت"}

action_type == 'update_order_field' و target_field == 'description'
    → textarea ویرایش توضیحات
    → POST execute-action با: {action_id, value: "متن"}

action_type == 'update_order_field' و target_field == 'repair_fee'
    → number input
    → POST execute-action با: {action_id, value: عدد}

action_type == 'update_order_field' و target_field == 'final_amount'
    → number input
    → POST execute-action با: {action_id, value: عدد}

action_type == 'update_order_item_field' و target_field == 'sony_account'
    → به ازای هر item یک dropdown انتخاب اکانت سونی
    → POST execute-action با: {action_id, value: sony_account_id, item_id: id}
```

اکشن‌هایی که `is_done == true` هستند با علامت تیک نمایش داده می‌شوند و غیرفعالند.

**بخش سوم — دکمه انتقال به stage بعدی:**

```
شرط نمایش فعال: همه action های is_required == true باید is_done == true باشند
دکمه غیرفعال: وقتی هنوز action های اجباری باقیمانده دارد
دکمه فعال: وقتی همه action های اجباری انجام شده
```

با کلیک روی دکمه:
```
POST /orders/sony-account/orders/<id>/advance-stage/
body: {"note": "اختیاری"}

response موفق:
{
    "status": "ok",
    "new_stage": {"id": 4, "title": "تحویل نهایی"}
}
```

بعد از موفقیت:
- modal بسته شود
- لیست سفارشات stage فعلی refresh شود (این سفارش از لیست حذف می‌شود)
- اگر stage جدید در دسترس این کارمند هست، در تب مربوطه ظاهر می‌شود

---

## نکات مهم پیاده‌سازی

### مدیریت وضعیت is_done

فرانت نباید وضعیت `is_done` را خودش نگه دارد. بعد از هر `execute-action` موفق، باید `GET /actions/` را دوباره call کند تا وضعیت به‌روز بگیرد.

### فعال/غیرفعال بودن دکمه advance

```javascript
const canAdvance = actions
  .filter(a => a.is_required)
  .every(a => a.is_done)
```

### error handling

هر دو endpoint `execute-action` و `advance-stage` در صورت خطا `400` با این فرمت برمی‌گردانند:

```json
{"detail": "پیام خطا به فارسی"}
```

این پیام را مستقیم به کاربر نمایش بده.

### فیلترهای لیست سفارشات

endpoint `by-stage` این query param ها را پشتیبانی می‌کند:

```
سونی اکانت:
  source        → telegram | website | in_person
  type          → by_customer | by_employee
  customer      → id مشتری
  date_from     → YYYY-MM-DD
  date_to       → YYYY-MM-DD
  ordering      → created_at | -created_at | amount | -amount

تعمیرات:
  customer      → id مشتری
  date_from     → YYYY-MM-DD
  date_to       → YYYY-MM-DD
  ordering      → created_at | -created_at

کالا:
  customer      → id مشتری
  date_from     → YYYY-MM-DD
  date_to       → YYYY-MM-DD
  ordering      → created_at | -created_at | amount | -amount
```

---

## endpoint یکسان برای هر سه نوع سفارش

| عملکرد | سونی اکانت | تعمیرات | کالا |
|--------|-----------|---------|------|
| لیست category | `sony-account/categories/` | `repair/categories/` | `product/categories/` |
| stage های category | `sony-account/categories/<id>/stages/` | `repair/categories/<id>/stages/` | `product/categories/<id>/stages/` |
| سفارشات stage | `sony-account/orders/by-stage/<id>/` | `repair/orders/by-stage/<id>/` | `product/orders/by-stage/<id>/` |
| جزئیات سفارش | `sony-account/orders/<id>/` | `repair/orders/<id>/` | `product/orders/<id>/` |
| action های سفارش | `sony-account/orders/<id>/actions/` | `repair/orders/<id>/actions/` | `product/orders/<id>/actions/` |
| اجرای action | `sony-account/orders/<id>/execute-action/` | `repair/orders/<id>/execute-action/` | `product/orders/<id>/execute-action/` |
| انتقال stage | `sony-account/orders/<id>/advance-stage/` | `repair/orders/<id>/advance-stage/` | `product/orders/<id>/advance-stage/` |
