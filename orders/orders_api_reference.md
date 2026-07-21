# Orders API — راهنمای Endpoints برای فرانت

Base URL: `/orders/`

---

## بخش ۱ — کانفیگ سفارشات (مدیر)

این بخش فقط برای مدیر است. مدیر از اینجا category، stage و action تعریف می‌کند.

### سونی اکانت

| Method | URL | کاربرد |
|--------|-----|---------|
| GET | `sony-account/categories/` | لیست همه category های سونی اکانت |
| POST | `sony-account/categories/create/` | ساخت category جدید |
| PATCH | `sony-account/categories/<id>/update/` | ویرایش category |
| DELETE | `sony-account/categories/<id>/delete/` | حذف category |
| GET | `sony-account/categories/<id>/stages/` | لیست stage های یک category |
| POST | `sony-account/stages/create/` | ساخت stage جدید (category را در body بفرست) |
| GET | `sony-account/stages/<id>/` | جزئیات یک stage + لیست action های آن |
| PATCH | `sony-account/stages/<id>/update/` | ویرایش stage |
| DELETE | `sony-account/stages/<id>/delete/` | حذف stage |
| POST | `sony-account/stage-actions/create/` | ساخت action جدید برای یک stage (stage را در body بفرست) |
| PATCH | `sony-account/stage-actions/<id>/update/` | ویرایش action |
| DELETE | `sony-account/stage-actions/<id>/delete/` | حذف action |

### تعمیرات

| Method | URL | کاربرد |
|--------|-----|---------|
| GET | `repair/categories/` | لیست category های تعمیر |
| POST | `repair/categories/create/` | ساخت category |
| PATCH | `repair/categories/<id>/update/` | ویرایش category |
| DELETE | `repair/categories/<id>/delete/` | حذف category |
| GET | `repair/categories/<id>/stages/` | لیست stage های یک category |
| POST | `repair/stages/create/` | ساخت stage |
| GET | `repair/stages/<id>/` | جزئیات stage + action ها |
| PATCH | `repair/stages/<id>/update/` | ویرایش stage |
| DELETE | `repair/stages/<id>/delete/` | حذف stage |
| POST | `repair/stage-actions/create/` | ساخت action |
| PATCH | `repair/stage-actions/<id>/update/` | ویرایش action |
| DELETE | `repair/stage-actions/<id>/delete/` | حذف action |

### کالا

| Method | URL | کاربرد |
|--------|-----|---------|
| GET | `product/categories/` | لیست category های کالا |
| POST | `product/categories/create/` | ساخت category |
| PATCH | `product/categories/<id>/update/` | ویرایش category |
| DELETE | `product/categories/<id>/delete/` | حذف category |
| GET | `product/categories/<id>/stages/` | لیست stage های یک category |
| POST | `product/stages/create/` | ساخت stage |
| GET | `product/stages/<id>/` | جزئیات stage + action ها |
| PATCH | `product/stages/<id>/update/` | ویرایش stage |
| DELETE | `product/stages/<id>/delete/` | حذف stage |
| POST | `product/stage-actions/create/` | ساخت action |
| PATCH | `product/stage-actions/<id>/update/` | ویرایش action |
| DELETE | `product/stage-actions/<id>/delete/` | حذف action |

---

## بخش ۲ — پنل کارمند (سفارشات)

این بخش برای کارمند است. جریان call ها به ترتیب زیر است.

### جریان call ها

```
Step 1: لیست category ها
Step 2: لیست stage های هر category (به ازای هر category یک call)
Step 3: لیست سفارشات هر stage (به ازای هر stage یک call)
Step 4: جزئیات یک سفارش (با کلیک روی سفارش)
Step 5: لیست action های stage فعلی آن سفارش
Step 6: اجرای هر action
Step 7: انتقال به stage بعدی
```

### سونی اکانت

| Method | URL | کاربرد | Step |
|--------|-----|---------|------|
| GET | `sony-account/categories/` | لیست category هایی که کارمند دسترسی دارد | 1 |
| GET | `sony-account/categories/<id>/stages/` | لیست stage های یک category | 2 |
| GET | `sony-account/orders/by-stage/<stage_id>/` | لیست کارتی سفارشات یک stage | 3 |
| GET | `sony-account/orders/<id>/` | جزئیات کامل یک سفارش | 4 |
| GET | `sony-account/orders/<id>/actions/` | لیست action های stage فعلی + وضعیت انجام هر کدام | 5 |
| POST | `sony-account/orders/<id>/execute-action/` | اجرای یک action | 6 |
| POST | `sony-account/orders/<id>/advance-stage/` | انتقال سفارش به stage بعدی | 7 |

### تعمیرات

| Method | URL | کاربرد | Step |
|--------|-----|---------|------|
| GET | `repair/categories/` | لیست category ها | 1 |
| GET | `repair/categories/<id>/stages/` | لیست stage های category | 2 |
| GET | `repair/orders/by-stage/<stage_id>/` | لیست سفارشات stage | 3 |
| GET | `repair/orders/<id>/` | جزئیات سفارش | 4 |
| GET | `repair/orders/<id>/actions/` | action های stage فعلی | 5 |
| POST | `repair/orders/<id>/execute-action/` | اجرای action | 6 |
| POST | `repair/orders/<id>/advance-stage/` | انتقال به stage بعدی | 7 |

### کالا

| Method | URL | کاربرد | Step |
|--------|-----|---------|------|
| GET | `product/categories/` | لیست category ها | 1 |
| GET | `product/categories/<id>/stages/` | لیست stage های category | 2 |
| GET | `product/orders/by-stage/<stage_id>/` | لیست سفارشات stage | 3 |
| GET | `product/orders/<id>/` | جزئیات سفارش | 4 |
| GET | `product/orders/<id>/actions/` | action های stage فعلی | 5 |
| POST | `product/orders/<id>/execute-action/` | اجرای action | 6 |
| POST | `product/orders/<id>/advance-stage/` | انتقال به stage بعدی | 7 |

---

## فرمت request/response های مهم

### execute-action — POST body

```json
{
    "action_id": 7,
    "value": 42,
    "item_id": 15,
    "note": "توضیحات اختیاری"
}
```

- `action_id` — همیشه الزامی
- `value` — برای `update_order_field` و `update_order_item_field` و `add_note` الزامی
- `item_id` — فقط برای `update_order_item_field` الزامی
- `note` — اختیاری در همه حالت‌ها

### advance-stage — POST body

```json
{
    "note": "توضیحات اختیاری"
}
```

### actions/ — نمونه response

```json
[
    {
        "id": 7,
        "title": "اختصاص اکانت سونی",
        "action_type": "update_order_item_field",
        "target_field": "sony_account",
        "is_required": true,
        "order": 1,
        "is_done": false
    },
    {
        "id": 8,
        "title": "تایید دستی",
        "action_type": "manual_confirm",
        "target_field": "",
        "is_required": true,
        "order": 2,
        "is_done": true
    }
]
```

### مقادیر `action_type` و کامپوننت متناظر

| action_type | target_field | کامپوننت فرانت |
|-------------|--------------|----------------|
| `update_order_field` | `description` | textarea |
| `update_order_item_field` | `sony_account` | dropdown انتخاب اکانت سونی |
| `update_order_field` | `repair_fee` | number input |
| `update_order_field` | `final_amount` | number input |
| `manual_confirm` | — | دکمه تایید |
| `add_note` | — | textarea |
