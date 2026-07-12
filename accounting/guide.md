<div dir="rtl">

# مستندات API بخش حسابداری — DrGame ERP

> **نکات کلی:**
> - تمام endpoint ها نیاز به احراز هویت دارند (`IsAuthenticated`)
> - تمام حذف‌ها **Soft Delete** هستند (فیلد `is_deleted=True`)
> - فیلدهای auto-generate در `perform_create` inject می‌شوند و از فرانت دریافت نمی‌شوند
> - فرمت تاریخ در تمام فیلترها: `YYYY-MM-DD`
> - پاسخ‌های لیست دارای pagination هستند

---

## ۱. بخش گزارش‌های مالی

> این بخش شامل چهار تب گزارشی است. هر تب دارای نمودار هفتگی (شنبه تا جمعه) و نمودار کلی با فیلتر بازه تاریخی است.

---

### ۱.۱ گزارش درآمد و سود

| متد   | endpoint                            | توضیح                             |
|-------|-------------------------------------|-----------------------------------|
| `GET` | /accounting/report/income/`      | گزارش کلی درآمدها با فیلتر تاریخ  |
| `GET` | /accounting/report/income/weekly/` | گزارش هفتگی درآمدها به تفکیک روز  |
| `GET` | /accounting/report/expense/`     | گزارش کلی هزینه‌ها با فیلتر تاریخ |
| `GET` | /accounting/report/expense/weekly/` | گزارش هفتگی هزینه‌ها به تفکیک روز |
| `GET` | /accounting/report/net/`         | گزارش خالص مالی (درآمد − هزینه)   |

**Query Parameters (فیلتر تاریخ):**

| پارامتر      | نوع    | پیش‌فرض      | توضیح            |
|--------------|--------|--------------|------------------|
| `start_date` | `date` | اول ماه جاری | تاریخ شروع بازه  |
| `end_date`   | `date` | بدون محدودیت | تاریخ پایان بازه |

**نمونه Response — گزارش کلی درآمد:**

```json
{
  "direction": "in",
  "direction_display": "دریافت",
  "count": 42,
  "total_amount": 15000000
}
```

**نمونه Response — گزارش هفتگی:**

```json
[
  {
    "date": "2024-01-06",
    "weekday": "شنبه",
    "count": 5,
    "total_amount": 2000000
  },
  {
    "date": "2024-01-07",
    "weekday": "یکشنبه",
    "count": 3,
    "total_amount": 1500000
  },
  {
    "date": "2024-01-08",
    "weekday": "دوشنبه",
    "count": 0,
    "total_amount": 0
  },
  {
    "date": "2024-01-09",
    "weekday": "سه‌شنبه",
    "count": 7,
    "total_amount": 3200000
  },
  {
    "date": "2024-01-10",
    "weekday": "چهارشنبه",
    "count": 4,
    "total_amount": 1800000
  },
  {
    "date": "2024-01-11",
    "weekday": "پنجشنبه",
    "count": 6,
    "total_amount": 2800000
  },
  {
    "date": "2024-01-12",
    "weekday": "جمعه",
    "count": 2,
    "total_amount": 900000
  }
]
```

**نمونه Response — خالص مالی:**

```json
{
  "income": {
    "direction": "in",
    "direction_display": "دریافت",
    "count": 42,
    "total_amount": 15000000
  },
  "expense": {
    "direction": "out",
    "direction_display": "پرداخت",
    "count": 18,
    "total_amount": 6000000
  },
  "net": 9000000
}
```

> **نکته فرانت:** endpoint های هفتگی همیشه هفته جاری (شنبه تا جمعه) را برمی‌گردانند و نیازی به ارسال پارامتر تاریخ
> ندارند.

---

### ۱.۲ گزارش سفارشات تعمیرات

| متد   | endpoint                          | توضیح                                  |
|-------|-----------------------------------|----------------------------------------|
| `GET` | /orders/repair/report/`        | گزارش کلی سفارشات تعمیر با فیلتر تاریخ |
| `GET` | /orders/repair/report/weekly/` | گزارش هفتگی سفارشات تعمیر به تفکیک روز |

**Query Parameters:**

| پارامتر      | نوع    | پیش‌فرض      | توضیح       |
|--------------|--------|--------------|-------------|
| `start_date` | `date` | اول ماه جاری | تاریخ شروع  |
| `end_date`   | `date` | بدون محدودیت | تاریخ پایان |

**نمونه Response — گزارش کلی:**

```json
{
  "count": 28,
  "total_amount": 8400000
}
```

---

### ۱.۳ گزارش سفارشات اکانت سونی

| متد   | endpoint                        | توضیح                           |
|-------|---------------------------------|---------------------------------|
| `GET` | /orders/sony/report/`        | گزارش کامل با تفکیک تمام فیلدها |
| `GET` | /orders/sony/report/weekly/` | گزارش هفتگی به تفکیک روز        |

**Query Parameters:**

| پارامتر      | نوع    | پیش‌فرض      | توضیح       |
|--------------|--------|--------------|-------------|
| `start_date` | `date` | اول ماه جاری | تاریخ شروع  |
| `end_date`   | `date` | بدون محدودیت | تاریخ پایان |

**نمونه Response — گزارش کامل:**

```json
{
  "summary": {
    "count": 120,
    "total_amount": 36000000
  },
  "by_source": [
    {
      "source": "telegram",
      "source_display": "تلگرام",
      "count": 70,
      "total_amount": 21000000
    },
    {
      "source": "in_person",
      "source_display": "حضوری",
      "count": 30,
      "total_amount": 9000000
    },
    {
      "source": "website",
      "source_display": "سایت",
      "count": 20,
      "total_amount": 6000000
    }
  ],
  "by_type": [
    {
      "type": "by_employee",
      "type_display": "توسط کارمند",
      "count": 80,
      "total_amount": 24000000
    },
    {
      "type": "by_customer",
      "type_display": "توسط مشتری",
      "count": 40,
      "total_amount": 12000000
    }
  ],
  "by_category": [
    {
      "category_id": 1,
      "category_title": "اجاره آفلاین",
      "category_type": "اجاره",
      "count": 50,
      "total_amount": 10000000
    },
    {
      "category_id": 2,
      "category_title": "خرید آنلاین",
      "category_type": "خرید",
      "count": 70,
      "total_amount": 26000000
    }
  ],
  "by_stage": [
    {
      "stage_id": 1,
      "stage_title": "تحویل داده شده",
      "count": 100,
      "total_amount": 30000000
    },
    {
      "stage_id": 2,
      "stage_title": "در انتظار",
      "count": 20,
      "total_amount": 6000000
    }
  ]
}
```

> **نکته:** این endpoint به تنهایی کل داده‌های مورد نیاز چهار زیربخش تب سونی را برمی‌گرداند.

---

### ۱.۴ گزارش سفارشات کالا

| متد   | endpoint                               | توضیح                    |
|-------|----------------------------------------|--------------------------|
| `GET` | /orders/product/report/`            | گزارش کلی سفارشات کالا   |
| `GET` | /orders/product/report/weekly/`     | گزارش هفتگی سفارشات کالا |
| `GET` | /orders/product/report/by-category/` | گزارش به تفکیک دسته‌بندی |

**Query Parameters:**

| پارامتر      | نوع    | پیش‌فرض      | توضیح       |
|--------------|--------|--------------|-------------|
| `start_date` | `date` | اول ماه جاری | تاریخ شروع  |
| `end_date`   | `date` | بدون محدودیت | تاریخ پایان |

**نمونه Response — تفکیک دسته‌بندی:**

```json
[
  {
    "category": "مرحله ارسال",
    "count": 15,
    "total_amount": 4500000
  },
  {
    "category": "مرحله آماده‌سازی",
    "count": 22,
    "total_amount": 6600000
  }
]
```

> **نکته:** فیلد `category` در این گزارش فعلاً بر اساس `stage` گروه‌بندی می‌شود. پس از آماده شدن مدل `Product`، به
`product__category` تغییر می‌کند.

---

## ۲. بخش دفتر روزانه

> تمام endpoint های این بخش فقط داده‌های **امروز** را برمی‌گردانند و نیازی به ارسال پارامتر تاریخ ندارد.

---

### ۲.۱ فاکتورهای روز

| متد         | endpoint                                  | توضیح                    |
|-------------|-------------------------------------------|--------------------------|
| `GET`       | /accounting/daily/invoices/`           | لیست فاکتورهای امروز     |
| `GET`       | /accounting/daily/invoices/<id>/`      | جزئیات فاکتور            |
| `PUT/PATCH` | /accounting/daily/invoices/<id>/edit/` | ویرایش فاکتور            |
| `DELETE`    | /accounting/daily/invoices/<id>/delete/` | حذف فاکتور (soft delete) |

**فیلترهای موجود:**

| پارامتر          | نوع       | توضیح                                          |
|------------------|-----------|------------------------------------------------|
| `status`         | `string`  | وضعیت فاکتور: `draft` / `primary` / `finalize` |
| `payment_status` | `string`  | وضعیت پرداخت: `unpaid` / `partial` / `paid`    |
| `account_side`   | `integer` | شناسه طرف حساب                                 |
| `category`       | `integer` | شناسه دسته‌بندی فاکتور                         |

**نمونه Response — لیست:**

```json
[
  {
    "id": 1,
    "account_side": {
      "id": 3,
      "name": "علی رضایی",
      "type": "customer"
    },
    "category": {
      "id": 2,
      "title": "فروش",
      "direction": "in"
    },
    "amount": 500000,
    "discount": 0,
    "paid_amount": 0,
    "remaining_amount": 500000,
    "status": "primary",
    "status_display": "صادر شده",
    "payment_status": "unpaid",
    "payment_status_display": "پرداخت نشده",
    "is_payroll": false,
    "created_at": "2024-01-10T09:30:00Z"
  }
]
```

---

### ۲.۲ تراکنش‌های روز

| متد         | endpoint                                      | توضیح                    |
|-------------|-----------------------------------------------|--------------------------|
| `GET`       | /accounting/daily/transactions/`           | لیست تراکنش‌های امروز    |
| `GET`       | /accounting/daily/transactions/<id>/`      | جزئیات تراکنش            |
| `PUT/PATCH` | /accounting/daily/transactions/<id>/edit/` | ویرایش تراکنش            |
| `DELETE`    | /accounting/daily/transactions/<id>/delete/` | حذف تراکنش (soft delete) |

**فیلترهای موجود:**

| پارامتر        | نوع       | توضیح                               |
|----------------|-----------|-------------------------------------|
| `direction`    | `string`  | جهت: `in` (دریافت) / `out` (پرداخت) |
| `bank_account` | `integer` | شناسه حساب بانکی                    |
| `account_side` | `integer` | شناسه طرف حساب                      |

**نمونه Response — لیست:**

```json
[
  {
    "id": 5,
    "direction": "in",
    "direction_display": "دریافت",
    "amount": 200000,
    "account_side": {
      "id": 3,
      "name": "علی رضایی",
      "type": "customer"
    },
    "bank_account": {
      "id": 1,
      "title": "حساب اصلی",
      "account_number": "1234567890"
    },
    "description": "پرداخت نقدی",
    "created_at": "2024-01-10T10:00:00Z"
  }
]
```

---

### ۲.۳ لیست طرف‌های حساب

> طرف‌های حساب (`AccountSide`) شامل مشتریان، کارمندان، تامین‌کنندگان و سایر است.

| متد         | endpoint                                | توضیح                      |
|-------------|-----------------------------------------|----------------------------|
| `GET`       | /accounting/account-sides/`          | لیست همه طرف‌های حساب      |
| `GET`       | /accounting/account-sides/?search=علی` | جستجو در طرف‌های حساب      |
| `GET`       | /accounting/account-sides/<id>/`     | جزئیات طرف حساب            |
| `POST`      | /accounting/account-sides/create/`   | ثبت طرف حساب جدید          |
| `PUT/PATCH` | /accounting/account-sides/<id>/edit/` | ویرایش طرف حساب            |
| `DELETE`    | /accounting/account-sides/<id>/delete/` | حذف طرف حساب (soft delete) |

**فیلترهای موجود:**

| پارامتر  | نوع      | توضیح                                               |
|----------|----------|-----------------------------------------------------|
| `type`   | `string` | نوع: `customer` / `employee` / `supplier` / `other` |
| `search` | `string` | جستجو در فیلد `name`                                |

---

### ۲.۴ حساب‌های پرداختنی روز

> فاکتورهای **خروجی** (`category__direction=out`) امروز که پرداخت نشده یا جزئی پرداخت شده‌اند.

| متد   | endpoint                        | توضیح                        |
|-------|---------------------------------|------------------------------|
| `GET` | /accounting/daily/payable/` | لیست حساب‌های پرداختنی امروز |

**فیلترهای موجود:**

| پارامتر          | نوع       | توضیح                |
|------------------|-----------|----------------------|
| `payment_status` | `string`  | `unpaid` / `partial` |
| `account_side`   | `integer` | شناسه طرف حساب       |

**نمونه Response:**

```json
[
  {
    "id": 8,
    "account_side": {
      "id": 5,
      "name": "شرکت آلفا",
      "type": "supplier"
    },
    "category": {
      "id": 3,
      "title": "خرید",
      "direction": "out"
    },
    "amount": 1200000,
    "paid_amount": 0,
    "remaining_amount": 1200000,
    "payment_status": "unpaid",
    "payment_status_display": "پرداخت نشده",
    "created_at": "2024-01-10T08:00:00Z"
  }
]
```

---

### ۲.۵ حساب‌های دریافتنی روز

> فاکتورهای **ورودی** (`category__direction=in`) امروز که دریافت نشده یا جزئی دریافت شده‌اند.

| متد   | endpoint                           | توضیح                        |
|-------|------------------------------------|------------------------------|
| `GET` | /accounting/daily/receivable/` | لیست حساب‌های دریافتنی امروز |

**فیلترهای موجود:**

| پارامتر          | نوع       | توضیح                |
|------------------|-----------|----------------------|
| `payment_status` | `string`  | `unpaid` / `partial` |
| `account_side`   | `integer` | شناسه طرف حساب       |

---

## ۳. بخش حسابداری

---

### ۳.۱ هزینه‌ها

> فاکتورهای با `category__direction=out` و `is_payroll=False`

| متد         | endpoint                          | توضیح                   |
|-------------|-----------------------------------|-------------------------|
| `GET`       | /accounting/expense/`           | لیست فاکتورهای هزینه‌ای |
| `GET`       | /accounting/expense/?search=اجاره` | جستجو در هزینه‌ها       |
| `GET`       | /accounting/expense/<id>/`      | جزئیات فاکتور هزینه     |
| `POST`      | /accounting/expense/create/`    | ثبت هزینه جدید          |
| `PUT/PATCH` | /accounting/expense/<id>/edit/` | ویرایش هزینه            |
| `DELETE`    | /accounting/expense/<id>/delete/` | حذف هزینه (soft delete) |

**فیلترهای موجود:**

| پارامتر          | نوع       | پیش‌فرض      | توضیح                            |
|------------------|-----------|--------------|----------------------------------|
| `start_date`     | `date`    | اول ماه جاری | تاریخ شروع                       |
| `end_date`       | `date`    | بدون محدودیت | تاریخ پایان                      |
| `status`         | `string`  | —            | `draft` / `primary` / `finalize` |
| `payment_status` | `string`  | —            | `unpaid` / `partial` / `paid`    |
| `account_side`   | `integer` | —            | شناسه طرف حساب                   |
| `search`         | `string`  | —            | جستجو در توضیحات                 |

**Body ثبت هزینه (فیلدهای مورد نیاز از فرانت):**

```json
{
  "account_side": 3,
  "amount": 500000,
  "discount": 0,
  "status": "primary",
  "description": "اجاره ماهانه"
}
```

> **نکته:** فیلد `category` به صورت خودکار به دسته‌بندی "هزینه" با `direction=out` ست می‌شود.

---

### ۳.۲ درآمدها

> فاکتورهای با `category__direction=in` و `is_payroll=False`

| متد         | endpoint                         | توضیح                   |
|-------------|----------------------------------|-------------------------|
| `GET`       | /accounting/income/`           | لیست فاکتورهای درآمدی   |
| `GET`       | /accounting/income/?search=فروش` | جستجو در درآمدها        |
| `GET`       | /accounting/income/<id>/`      | جزئیات فاکتور درآمد     |
| `POST`      | /accounting/income/create/`    | ثبت درآمد جدید          |
| `PUT/PATCH` | /accounting/income/<id>/edit/` | ویرایش درآمد            |
| `DELETE`    | /accounting/income/<id>/delete/` | حذف درآمد (soft delete) |

**فیلترهای موجود:**

| پارامتر          | نوع       | پیش‌فرض      | توضیح                            |
|------------------|-----------|--------------|----------------------------------|
| `start_date`     | `date`    | اول ماه جاری | تاریخ شروع                       |
| `end_date`       | `date`    | بدون محدودیت | تاریخ پایان                      |
| `status`         | `string`  | —            | `draft` / `primary` / `finalize` |
| `payment_status` | `string`  | —            | `unpaid` / `partial` / `paid`    |
| `account_side`   | `integer` | —            | شناسه طرف حساب                   |
| `search`         | `string`  | —            | جستجو در توضیحات                 |

**Body ثبت درآمد:**

```json
{
  "account_side": 3,
  "amount": 800000,
  "discount": 0,
  "status": "primary",
  "description": "فروش محصول"
}
```

> **نکته:** فیلد `category` به صورت خودکار به دسته‌بندی "درآمد" با `direction=in` ست می‌شود.

---

### ۳.۳ فیش‌های حقوقی

> فاکتورهای با `is_payroll=True` — طرف حساب همیشه از نوع **کارمند** است

| متد         | endpoint                          | توضیح                               |
|-------------|-----------------------------------|-------------------------------------|
| `GET`       | /accounting/payroll/`           | لیست فیش‌های حقوقی                  |
| `GET`       | /accounting/payroll/?search=احمدی` | جستجو در فیش‌های حقوقی              |
| `GET`       | /accounting/payroll/<id>/`      | جزئیات فیش حقوقی (شامل جزئیات حقوق) |
| `POST`      | /accounting/payroll/create/`    | ثبت فیش حقوقی جدید                  |
| `PUT/PATCH` | /accounting/payroll/<id>/edit/` | ویرایش فیش حقوقی                    |
| `DELETE`    | /accounting/payroll/<id>/delete/` | حذف فیش حقوقی (soft delete)         |

**فیلترهای موجود:**

| پارامتر          | نوع       | پیش‌فرض      | توضیح                         |
|------------------|-----------|--------------|-------------------------------|
| `start_date`     | `date`    | اول ماه جاری | تاریخ شروع                    |
| `end_date`       | `date`    | بدون محدودیت | تاریخ پایان                   |
| `payment_status` | `string`  | —            | `unpaid` / `partial` / `paid` |
| `account_side`   | `integer` | —            | شناسه طرف حساب (کارمند)       |
| `search`         | `string`  | —            | جستجو در نام طرف حساب         |

**Body ثبت فیش حقوقی:**

```json
{
  "account_side": 7,
  "amount": 12000000,
  "discount": 0,
  "status": "primary",
  "description": "حقوق فروردین ۱۴۰۳",
  "payroll_detail": {
    "base_salary": 8000000,
    "overtime_amount": 1500000,
    "bonus": 500000,
    "housing_allowance": 800000,
    "food_allowance": 400000,
    "transportation_allowance": 300000,
    "insurance_deduction": 720000,
    "tax_deduction": 0,
    "loan_deduction": 0,
    "other_deductions": 0,
    "work_days": 26,
    "overtime_hours": 10,
    "description": "عملکرد عالی"
  }
}
```

**نمونه Response — جزئیات:**

```json
{
  "id": 12,
  "account_side": {
    "id": 7,
    "name": "محمد احمدی",
    "type": "employee"
  },
  "amount": 12000000,
  "paid_amount": 0,
  "remaining_amount": 12000000,
  "payment_status": "unpaid",
  "payment_status_display": "پرداخت نشده",
  "description": "حقوق فروردین ۱۴۰۳",
  "payroll_detail": {
    "base_salary": 8000000,
    "overtime_amount": 1500000,
    "bonus": 500000,
    "housing_allowance": 800000,
    "food_allowance": 400000,
    "transportation_allowance": 300000,
    "insurance_deduction": 720000,
    "tax_deduction": 0,
    "loan_deduction": 0,
    "other_deductions": 0,
    "work_days": 26,
    "overtime_hours": 10,
    "description": "عملکرد عالی",
    "gross_salary": 11500000,
    "total_deductions": 720000,
    "net_salary": 10780000
  },
  "created_at": "2024-01-10T09:00:00Z",
  "updated_at": "2024-01-10T09:00:00Z"
}
```

> **نکته‌های auto-generate:**
> - `category` → به صورت خودکار `InvoiceCategory(title='حقوق و دستمزد', direction='out')` ست می‌شود
> - `is_payroll` → همیشه `True`
> - `gross_salary`، `total_deductions`، `net_salary` → فیلدهای محاسباتی (read-only property)

---

## ۴. Dropdown / Choices Endpoints

> برای پر کردن select box های فرانت

| متد   | endpoint                                            | توضیح                     |
|-------|-----------------------------------------------------|---------------------------|
| `GET` | /accounting/invoice/dropdown/?type=account_side` | لیست طرف‌های حساب         |
| `GET` | /accounting/invoice/dropdown/?type=category`     | لیست دسته‌بندی‌های فاکتور |
| `GET` | /accounting/invoice/dropdown/?type=status`       | وضعیت‌های فاکتور          |
| `GET` | /accounting/invoice/dropdown/?type=payment_status` | وضعیت‌های پرداخت          |

**نمونه Response:**

```json
[
  {
    "key": "draft",
    "value": "پیش‌نویس"
  },
  {
    "key": "primary",
    "value": "صادر شده"
  },
  {
    "key": "finalize",
    "value": "نهایی"
  }
]
```

---

## ۵. جدول کامل Endpoint ها

| بخش                        | متد       | endpoint                  |
|----------------------------|-----------|---------------------------|
| **گزارش مالی**             | GET       | /accounting/report/income/` |
|                            | GET       | /accounting/report/income/weekly/` |
|                            | GET       | /accounting/report/expense/` |
|                            | GET       | /accounting/report/expense/weekly/` |
|                            | GET       | /accounting/report/net/`  |
| **گزارش تعمیرات**          | GET       | /orders/repair/report/`   |
|                            | GET       | /orders/repair/report/weekly/` |
| **گزارش سونی**             | GET       | /orders/sony/report/`     |
|                            | GET       | /orders/sony/report/weekly/` |
| **گزارش کالا**             | GET       | /orders/product/report/`  |
|                            | GET       | /orders/product/report/weekly/` |
|                            | GET       | /orders/product/report/by-category/` |
| **دفتر روزانه — فاکتور**   | GET       | /accounting/daily/invoices/` |
|                            | GET       | /accounting/daily/invoices/<id>/` |
|                            | PUT/PATCH | /accounting/daily/invoices/<id>/edit/` |
|                            | DELETE    | /accounting/daily/invoices/<id>/delete/` |
| **دفتر روزانه — تراکنش**   | GET       | /accounting/daily/transactions/` |
|                            | GET       | /accounting/daily/transactions/<id>/` |
|                            | PUT/PATCH | /accounting/daily/transactions/<id>/edit/` |
|                            | DELETE    | /accounting/daily/transactions/<id>/delete/` |
| **دفتر روزانه — طرف حساب** | GET       | /accounting/account-sides/` |
|                            | GET       | /accounting/account-sides/<id>/` |
|                            | POST      | /accounting/account-sides/create/` |
|                            | PUT/PATCH | /accounting/account-sides/<id>/edit/` |
|                            | DELETE    | /accounting/account-sides/<id>/delete/` |
| **دفتر روزانه — پرداختنی** | GET       | /accounting/daily/payable/` |
| **دفتر روزانه — دریافتنی** | GET       | /accounting/daily/receivable/` |
| **حسابداری — هزینه**       | GET       | /accounting/expense/`     |
|                            | GET       | /accounting/expense/<id>/` |
|                            | POST      | /accounting/expense/create/` |
|                            | PUT/PATCH | /accounting/expense/<id>/edit/` |
|                            | DELETE    | /accounting/expense/<id>/delete/` |
| **حسابداری — درآمد**       | GET       | /accounting/income/`      |
|                            | GET       | /accounting/income/<id>/` |
|                            | POST      | /accounting/income/create/` |
|                            | PUT/PATCH | /accounting/income/<id>/edit/` |
|                            | DELETE    | /accounting/income/<id>/delete/` |
| **حسابداری — فیش حقوقی**   | GET       | /accounting/payroll/`     |
|                            | GET       | /accounting/payroll/<id>/` |
|                            | POST      | /accounting/payroll/create/` |
|                            | PUT/PATCH | /accounting/payroll/<id>/edit/` |
|                            | DELETE    | /accounting/payroll/<id>/delete/` |
| **Dropdown**               | GET       | /accounting/invoice/dropdown/` |

---

## ۶. نکات پیاده‌سازی باقی‌مانده

> موارد زیر در بک‌اند هنوز پیاده‌سازی نشده و باید اضافه شوند:

| مورد                | توضیح                                                                                                                     |
|---------------------|---------------------------------------------------------------------------------------------------------------------------|
| `AccountSide` CRUD  | ویوهای لیست، جزئیات، ایجاد، ویرایش، حذف برای طرف‌های حساب                                                                 |
| `daily/payable/`    | ویو فاکتورهای پرداختنی امروز — فیلتر `direction=out` + `payment_status__in=[unpaid, partial]`                             |
| `daily/receivable/` | ویو فاکتورهای دریافتنی امروز — فیلتر `direction=in` + `payment_status__in=[unpaid, partial]`                              |
| Search endpoint     | اضافه کردن `SearchFilter` به تمام ویوهای لیست                                                                             |
| فاکتور خرید و فروش  | ویوهای `/purchase/` و `/sales/` که در کد پیاده‌سازی شده ولی در این داکیومنت جداگانه نیامده — در صورت نیاز فرانت اضافه شود |

</div>