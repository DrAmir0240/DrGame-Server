# ARCHITECTURE.md — سیستم ERP دکترگیم

> مستند جامع معماری، نیازمندی‌ها، فازبندی و تسک‌بندی پروژه  
> نسخه ۱.۰ — بر اساس نیازمندی‌نامه و جلسات شفاف‌سازی

---

## فهرست مطالب

1. [نمای کلی سیستم](#1-نمای-کلی-سیستم)
2. [استک فنی](#2-استک-فنی)
3. [معماری زیرساخت](#3-معماری-زیرساخت)
4. [ماژول‌های سیستم](#4-ماژول‌های-سیستم)
5. [معماری دیتابیس — ERD کامل](#5-معماری-دیتابیس--erd-کامل)
6. [طراحی API](#6-طراحی-api)
7. [سیستم نقش‌ها و دسترسی‌ها — RBAC](#7-سیستم-نقشها-و-دسترسیها--rbac)
8. [سرویس‌های جانبی و Placeholder ها](#8-سرویسهای-جانبی-و-placeholder-ها)
9. [فازبندی و تسک‌بندی توسعه](#9-فازبندی-و-تسکبندی-توسعه)

---

## ۱. نمای کلی سیستم

### ۱.۱ معرفی کسب‌وکار

**دکترگیم** یک مجموعه فروشگاهی چندشعبه‌ای است که در زمینه گیمینگ فعالیت می‌کند. محصولات و سرویس‌های اصلی:

| نوع | شرح |
|-----|-----|
| کالای فیزیکی | فروش کنسول، دسته، لوازم جانبی گیمینگ |
| بازی فیزیکی | فروش بازی روی دیسک (مانند کالا، با انبار مستقل) |
| اکانت آنلاین PS | اکانت قانونی سونی با ظرفیت مشخص — فروش بازی‌های دیجیتال |
| اکانت آفلاین PS | اکانت کرک‌شده با ظرفیت مشخص |
| بازی Xbox / Nintendo | فروش بازی برای پلتفرم‌های دیگر |
| تعمیر | سرویس تعمیر کنسول و دسته توسط تعمیرکار خارجی |

### ۱.۲ مدل شعبه

- سیستم چندشعبه‌ای است
- **انبار کالا و بازی فیزیکی:** مستقل به ازای هر شعبه
- **انبار بازی دیجیتال (اکانت):** مرکزی و مشترک بین همه شعبه‌ها
- **صندوق مالی:** مستقل به ازای هر شعبه — صفرسازی روزانه توسط صندوق‌دار
- **قیمت‌گذاری:** یکسان برای همه شعبه‌ها
- **انتقال کالا بین شعبه:** ممکن ولی استثناء — نیاز به درخواست رسمی

### ۱.۳ مدل کاربری

یک کاربر می‌تواند چند نقش داشته باشد (به استثنای Admin که فقط یک نفر است). مثال: یک نفر می‌تواند هم مشتری عادی باشد، هم B2B، هم کارمند. سوئیچ بین نقش‌ها از طریق یک پنل یکپارچه با تب‌های جداگانه انجام می‌شود.

### ۱.۴ احراز هویت

- ورود با شماره تلفن + کد OTP
- بدون پسورد — OTP تنها مکانیزم ورود است
- سرویس ارسال OTP به صورت Placeholder تعریف می‌شود

---

## ۲. استک فنی

### Backend
```
زبان:        Python 3.12+
فریم‌ورک:    Django 5.x + Django REST Framework
احراز هویت: SimpleJWT (JWT-based)
WebSocket:   Django Channels + Redis Channel Layer
صف:          Celery + Redis
ORM:         Django ORM
مهاجرت DB:  Django Migrations
```

### Frontend
```
فریم‌ورک:    Next.js 14+ (App Router)
زبان:        TypeScript
State:        Zustand / React Query
UI:           Tailwind CSS + Shadcn/UI
WebSocket:    Native WebSocket API
HTTP Client:  Axios
```

### زیرساخت
```
دیتابیس:      PostgreSQL 16+ (خارجی — URL به Backend وصل می‌شود)
Cache/Queue:  Redis
Container:    Docker + Docker Compose (Monorepo)
ساختار:       Monorepo — Backend و Frontend در یک ریپو
Reverse Proxy: Nginx (داخل Docker Compose)
```


### زبان طراحی


```
طراحی این سایت بر اساس دو طرح لایت مود و دارک مود است و 
رنگ مین تیم استفاده شده در سایت بنفش با کد زیر است
#3c02cf
در دارک مود با تم 
#0a0024
 پیوند میخورد
  و در لایت مود با سفید 
#ffffff
```


---

## ۳. معماری زیرساخت

### ۳.۱ ساختار Monorepo

```
DrGame/
├── docker-compose.yml
├── docker-compose.dev.yml
├── architecture.md
├── .env.example
├── nginx/
│   └── nginx.conf
├── backend/                    # Django Project
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   ├── asgi.py             # WebSocket Support
│   │   └── celery.py
│   └── apps/
│       ├── core/               # User, Role, Permission, Branch, AuditLog
│       ├── inventory/          # Product, Stock, StockMovement
│       ├── accounts/           # PSAccount, XboxAccount, AccountSale
│       ├── orders/             # Order, Invoice, Payment, Refund
│       ├── repair/             # RepairOrder, TechnicianPricing
│       ├── procurement/        # PurchaseRequest, PurchaseOrder, Supplier
│       ├── accounting/         # GeneralLedger, JournalEntry, Tax
│       ├── hr/                 # Employee, Attendance, Leave, Salary
│       ├── tasks/              # Task, TaskAssignment, TaskReward
│       ├── crm/                # Customer, B2BCustomer, CreditLimit
│       ├── notifications/      # Notification, NotificationPreference
│       ├── ecommerce/          # Cart, Checkout, ShippingAddress
│       └── documents/          # Document, Asset
└── frontend/                   # Next.js Project
    ├── Dockerfile
    ├── package.json
    ├── src/
    │   ├── app/
    │   │   ├── (public)/       # صفحات عمومی سایت
    │   │   ├── (auth)/         # ورود و ثبت‌نام
    │   │   └── (panel)/        # پنل‌های Admin, Employee, Technician, Customer
    │   ├── components/
    │   ├── lib/
    │   │   ├── api/            # Axios instances
    │   │   └── websocket/      # WebSocket client
    │   └── store/              # Zustand stores
```

### ۳.۲ Docker Compose

```yaml
# docker-compose.yml (ساختار کلی)
services:
  nginx:          # Reverse Proxy (Port 80/443)
  backend:        # Django (Port 8000 internal)
  celery:         # Celery Worker
  celery-beat:    # Celery Beat (Scheduled tasks)
  frontend:       # Next.js (Port 3000 internal)
  redis:          # Cache + Channel Layer + Celery Broker

# دیتابیس PostgreSQL خارجی است — فقط DATABASE_URL در .env تعریف می‌شود
```

### ۳.۳ ارتباط سرویس‌ها

```
Browser / Mobile
    │
    ▼
  Nginx (80/443)
    ├──── /api/v1/*        ──►  Django Backend (8000)
    ├──── /ws/*            ──►  Django Channels (8000/ws)
    └──── /*               ──►  Next.js Frontend (3000)

Django Backend
    ├──── PostgreSQL        (External DB)
    ├──── Redis             (Cache + Celery + Channel Layer)
    └──── Celery Workers    (Async Tasks: SMS, Reports, Notifications)
```

---

## ۴. ماژول‌های سیستم

### ۴.۱ Core — هسته اصلی

**User & Auth**
- ثبت‌نام و ورود با شماره تلفن + OTP
- یک کاربر می‌تواند چند نقش داشته باشد
- JWT Access Token + Refresh Token
- مدیریت نشست‌های فعال

**Role & Permission (RBAC)**
- نقش‌های پیش‌فرض: Admin، Cashier، Account Setter، Accountant، Warehouse، Customer، B2B Customer، Repair Technician
- قابلیت تعریف نقش سفارشی توسط Admin
- دسترسی‌ها بر اساس ماژول (Read / Write به ازای هر ماژول)
- ماتریس Permission: `[Role] × [Module] × [read|write]`

**Branch Management**
- تعریف شعبه‌ها با اطلاعات کامل (نام، آدرس، تلفن)
- هر کارمند به یک یا چند شعبه وابسته است
- گزارش‌های مالی و عملکردی تفکیکی به ازای هر شعبه

**Audit Log**
- لاگ تمام تغییرات: چه کسی، چه زمانی، چه چیزی را تغییر داد (before / after)
- لاگ برای همه ماژول‌های اصلی
- قابل جستجو و فیلتر در پنل Admin

---

### ۴.۲ Inventory — انبارداری

**کالای فیزیکی**
- انبار مستقل به ازای هر شعبه
- هر کالا با بارکد یونیک، دسته‌بندی (سه‌لایه)، قیمت خرید و فروش
- موجودی‌های مجزا (هر واحد با سریال / بارکد خود)
- کسر خودکار موجودی پس از فروش

**بازی فیزیکی**
- مانند کالای فیزیکی — انبار شعبه‌ای
- جدا از بازی دیجیتال

**بازی دیجیتال (اکانت‌ها)**
- انبار مرکزی — مشترک بین همه شعبه‌ها
- وقتی شعبه‌ای می‌فروشد، از انبار مرکزی کسر می‌شود

**Stock Movement Log**
- ثبت تمام گردش‌های انبار: خرید، فروش، برگشت، انتقال، تنظیم دستی
- هر movement با کاربر، زمان، نوع عملیات و مقدار ثبت می‌شود
- قابل فیلتر بر اساس تاریخ، نوع، کالا و شعبه

**انتقال بین شعبه**
- درخواست انتقال → تأیید مدیر → ثبت خروج از مبدأ → ثبت ورود در مقصد
- وضعیت‌ها: در انتظار / تأیید شده / در راه / تحویل شده / لغو

---

### ۴.۳ Accounts Management — مدیریت اکانت‌ها

**ساختار اکانت PS (آنلاین و آفلاین)**
- مشخصات اکانت: نام اکانت، ایمیل، پسورد، نوع (آنلاین/آفلاین)، ظرفیت کل
- ظرفیت فروخته‌شده: با هر فروش یک واحد اضافه می‌شود
- لاگ فروش: هر فروش با مشخصات مشتری، تاریخ و کنسول ضمیمه اکانت می‌شود
- سیستم نمی‌داند ظرفیت واقعی چقدر است — فقط تعداد فروش‌ها ثبت می‌شود

**اکانت Xbox / Nintendo**
- مدل مشابه PS آفلاین — با مشخصات مربوط به پلتفرم

**فرآیند فروش آنلاین اکانت PS**
1. مشتری بازی‌های مورد نظر را انتخاب می‌کند
2. سیستم بر اساس دیتابیس بازی‌ها، اکانت(های) حاوی بازی را پیدا می‌کند
3. قیمت نهایی و تعداد اکانت مورد نیاز محاسبه می‌شود
4. پس از پرداخت، اطلاعات اکانت به مشتری نمایش داده می‌شود
5. یک رکورد فروش به اکانت ضمیمه می‌شود

---

### ۴.۴ Orders — سفارش‌ها

**انواع سفارش**

| نوع | کانال | جزئیات |
|-----|-------|---------|
| فروش کالا — آنلاین | سایت | مشتری سفارش می‌دهد، صندوق‌دار تأیید، پیک ارسال |
| فروش کالا — حضوری | پنل | صندوق‌دار ثبت می‌کند |
| فروش اکانت آنلاین — آنلاین | سایت | سیستم قیمت محاسبه، پرداخت، نمایش اکانت |
| فروش اکانت آنلاین — حضوری | پنل | کنسول تحویل، اکانت‌ستر ست می‌کند |
| فروش اکانت آفلاین — آنلاین | سایت / تلگرام | مشتری کنسول می‌آورد |
| فروش اکانت آفلاین — حضوری | پنل | مانند آنلاین |
| فروش Xbox/Nintendo | سایت / پنل | کنسول می‌آورد |
| تعمیر | سایت / پنل | کنسول می‌آورد |

**وضعیت‌های سفارش**
- pending → confirmed → processing → ready → dispatched → delivered → completed
- برای تعمیر: pending → received → under_review → price_set → approved → in_repair → repaired → dispatched → completed / cancelled

**پیک**
- پیک خارجی — فقط اطلاعات (نام، شماره، مبلغ پیک) به سفارش ضمیمه می‌شود
- مشتری و صندوق‌دار می‌توانند اطلاعات پیک را ثبت کنند
- یک پیک می‌تواند چند سفارش همزمان داشته باشد (فقط برای ردیابی اطلاعات)

**فاکتور**
- شماره فاکتور یونیک و پیوسته (مثال: INV-1404-00001)
- شامل VAT (درصد مالیات متغیر و قابل تنظیم)
- فاکتور رسمی برای همه مشتریان (B2C و B2B)
- قابل پرینت / PDF

**پرداخت**
- پرداخت آنلاین (از طریق درگاه — Placeholder)
- پرداخت از کیف پول
- ثبت پرداخت حضوری توسط صندوق‌دار
- پرداخت می‌تواند در هر زمانی پس از ثبت سفارش انجام شود (نه لزوماً در لحظه)

**تخفیف**
- B2B: درصد ثابت روی سفارش‌های بازی (قابل تنظیم کلی یا به ازای هر مشتری)
- سایر سفارش‌ها: تخفیف موقع ثبت سفارش توسط کارمند وارد می‌شود — نام کارمند ثبت می‌شود

---

### ۴.۵ Refund / Return / Cancellation — برگشت و لغو

**برگشت کالا**
- بازه زمانی مجاز: قابل تنظیم به ازای هر دسته‌بندی محصول
- فرآیند: درخواست مشتری → تأیید ادمین/صندوق‌دار → ثبت بازگشت موجودی → استرداد وجه
- استرداد وجه: واریز به کیف پول مشتری یا برگشت به کارت/حساب

**لغو سفارش**
- قابل لغو قبل از مرحله dispatched
- لغو پس از dispatched فقط با تأیید ادمین
- موجودی خودکار به انبار برمی‌گردد
- وجه به کیف پول مشتری برمی‌گردد

**قوانین برگشت اکانت‌ها و بازی دیجیتال**
- اکانت‌های دیجیتال پس از نمایش اطلاعات قابل برگشت نیستند (قابل تنظیم)

---

### ۴.۶ Repair — تعمیرات

**فرآیند کامل**
1. ثبت سفارش تعمیر (آنلاین یا حضوری)
2. ارسال دستگاه (توسط پیک یا حضوری)
3. تأیید دریافت دستگاه توسط صندوق‌دار
4. قبول سفارش توسط تعمیرکار از پنل خود
5. بررسی دستگاه و ثبت قیمت تعمیر
6. سیستم درصد سود مدیریت (قابل تنظیم توسط Admin) را به قیمت اضافه می‌کند
7. نمایش قیمت نهایی به مشتری در پنل
8. تأیید یا رد توسط مشتری
9. در صورت رد: دستگاه برگردانده می‌شود
10. در صورت تأیید: تعمیر انجام می‌شود
11. تحویل به صندوق‌دار و سپس به مشتری
12. پرداخت در هر زمانی پس از تعیین قیمت (آنلاین یا حضوری)

**تعمیرکار**
- تعمیرکار خارجی است (نه کارمند رسمی)
- پنل مستقل دارد
- درآمد از طریق سیستم ثبت می‌شود (با کسر درصد سود مدیریت)
- درصد سود مدیریت توسط Admin تنظیم می‌شود

---

### ۴.۷ Procurement — خرید و تأمین

**ساختار**
- ثبت درخواست خرید توسط کارمند مربوطه (انباردار، حسابدار، یا هر کارمند با دسترسی)
- گردش کار: درخواست خرید → تأیید مدیر → ثبت خرید انجام‌شده
- نیاز به مقایسه چند تأمین‌کننده نیست — فقط ثبت اطلاعات خرید

**اطلاعات درخواست خرید**
- نوع کالا / محصول مورد نیاز
- مقدار، توضیحات
- شعبه درخواست‌دهنده
- وضعیت: draft / submitted / approved / rejected / purchased

**اطلاعات خرید انجام‌شده**
- تأمین‌کننده، مبلغ، روش پرداخت (نقدی / نسیه / چک)
- تاریخ خرید، شماره فاکتور تأمین‌کننده
- تأثیر خودکار روی موجودی انبار (Stock Movement)
- ثبت در دفتر حسابداری (Journal Entry)

**مدیریت تأمین‌کنندگان**
- اطلاعات کامل: نام شرکت، شخص تماس، تلفن، ایمیل، آدرس
- سابقه خرید از هر تأمین‌کننده
- مانده حساب (بدهی به تأمین‌کننده)

---

### ۴.۸ Accounting — حسابداری دوطرفه

**ساختار کلی**
- سیستم حسابداری دوطرفه (Double-Entry)
- خودکفا — بدون اتصال به نرم‌افزار خارجی

**نمودار حساب‌ها (Chart of Accounts)**
```
دارایی‌ها (Assets)
    ├── صندوق نقدی (Cash - به ازای هر شعبه)
    ├── حساب‌های بانکی
    ├── حساب‌های دریافتنی (Accounts Receivable)
    ├── موجودی انبار (Inventory)
    └── دارایی‌های حقیقی (Fixed Assets)

بدهی‌ها (Liabilities)
    ├── حساب‌های پرداختنی (Accounts Payable - به تأمین‌کننده)
    ├── مالیات پرداختنی (VAT Payable)
    └── مساعده‌های پرداختنی

حقوق صاحبان سهام (Equity)
    └── سرمایه

درآمد (Revenue)
    ├── فروش کالا
    ├── فروش اکانت
    ├── سرویس تعمیر
    └── سایر درآمدها

هزینه (Expenses)
    ├── خرید کالا
    ├── حقوق و دستمزد
    ├── هزینه‌های عملیاتی
    └── سایر هزینه‌ها
```

**Journal Entry**
- هر تراکنش مالی = یک یا چند Journal Entry
- هر Entry: حساب بدهکار، حساب بستانکار، مبلغ، توضیح، تاریخ
- مثال — فروش کالا:
  ```
  Dr. حساب‌های دریافتنی / صندوق    XXX
      Cr. درآمد فروش                     XXX
      Cr. مالیات پرداختنی (VAT)          XXX
  ```

**مالیات (VAT)**
- درصد مالیات متغیر و قابل تنظیم از پنل Admin
- محاسبه خودکار در فاکتور
- گزارش مالیاتی دوره‌ای

**صفرسازی صندوق روزانه**
- صندوق‌دار مبالغ نقدی و کارتخوان را جداگانه گزارش می‌دهد
- ثبت در سیستم → انتقال به حساب اصلی → صفرشدن صندوق شعبه
- Journal Entry خودکار تولید می‌شود

**گزارش‌های مالی**
- سود و زیان (P&L) — فیلتر تاریخ، شعبه
- جریان نقدی (Cash Flow)
- ترازنامه (Balance Sheet)
- گزارش مالیاتی (VAT Report)
- حساب‌های دریافتنی و پرداختنی

**ورودی‌های دستی**
- ادمین یا حسابدار می‌تواند ورودی‌های دستی ثبت کند (مثل جریمه، پاداش، هزینه تنخواه)

---

### ۴.۹ HR — منابع انسانی

**مدیریت کارمندان**
- اطلاعات کامل: نام، شماره تلفن، کد ملی، آدرس، تاریخ استخدام، شعبه
- نوع قرارداد: حقوق ثابت / پورسانتی / ترکیبی
- درصد پورسانت قابل تنظیم به ازای هر کارمند
- وابستگی به شعبه

**حقوق و دستمزد**
- محاسبه ماهانه: حقوق پایه + پورسانت + پاداش تسک − مساعده − جریمه
- ثبت در دفتر حسابداری (Journal Entry)
- سابقه پرداخت حقوق

**مساعده (پیش‌پرداخت)**
- درخواست مساعده توسط کارمند
- تأیید توسط مدیر
- مبلغ از حقوق ماه بعد کسر می‌شود
- اگر حقوق کافی نباشد، از ماه‌های بعدی ادامه کسر داشته باشد

**مرخصی**
- حداقل یک روز قبل باید ثبت شود
- تعداد روز مرخصی سالانه قابل تنظیم به ازای هر کارمند
- وضعیت: pending / approved / rejected
- نوتیفیکیشن به مدیر پس از ثبت درخواست

**درخواست‌های کارمندان**
- انواع: مرخصی، مساعده، سایر درخواست‌ها
- گردش: ثبت → تأیید/رد توسط مدیر → نوتیف به کارمند

**حضور و غیاب**
- ثبت ورود و خروج کارمند
- لیست غیبت‌ها قابل مشاهده در پنل مدیر
- تأثیر بر محاسبه حقوق

**رزومه‌های استخدام**
- فرم عمومی در سایت برای ارسال رزومه
- دسته‌بندی بر اساس نقش درخواستی
- تغییر وضعیت به "استخدام‌شده"

---

### ۴.۱۰ Task Management — تسک‌منیجر

- **تعریف‌کننده تسک:** مدیر یا هر کارمند با دسترسی مربوطه
- **اساین‌شونده:** یک یا چند کارمند
- **فیلدها:** عنوان، توضیحات، اساین به، start_datetime، deadline_datetime، وضعیت، پاداش
- **پاداش:** می‌تواند مبلغ ریالی یا امتیاز باشد
- **نوتیفیکیشن:** یک روز قبل از deadline هم نوتیف داخلی + SMS می‌رود
- **نمایش در تقویم:** تسک‌ها در تقویم صفحه‌ای و هفتگی نمایش داده می‌شوند
- **وضعیت‌ها:** open / in_progress / done / cancelled
- **تسک دسته‌ای:** امکان اساین کردن یک تسک به چند کارمند هم‌زمان

---

### ۴.۱۱ CRM — مدیریت مشتریان

**مشتری عادی (B2C)**
- ثبت‌نام با شماره تلفن
- کیف پول شخصی
- سابقه سفارش‌ها و پرداخت‌ها
- ارسال SMS تکی یا دسته‌ای از پنل مدیر

**مشتری B2B**
- تمام ویژگی‌های B2C + موارد زیر:
- سقف بدهی (مبلغ ریالی) — قابل تنظیم کلی یا به ازای هر مشتری
- امکان خرید نسیه
- اگر بدهی از سقف بگذرد، خرید جدید مسدود می‌شود
- تخفیف درصدی روی سفارش‌های بازی
- گزارش جداگانه B2B در داشبورد
- فاکتور رسمی با مالیات

**کیف پول**
- شارژ توسط Admin / درگاه پرداخت
- کسر هنگام خرید
- تاریخچه تراکنش‌ها

---

### ۴.۱۲ Notification System — نوتیفیکیشن

**کانال‌ها**
- نوتیف داخلی (WebSocket — Real-time)
- SMS (برای رویدادهای مهم)

**نوتیف‌های مشتری**

| رویداد | داخلی | SMS |
|--------|-------|-----|
| ثبت سفارش | ✓ | ✓ |
| تأیید سفارش | ✓ | - |
| ارسال شد / در دست پیک | ✓ | ✓ |
| تحویل داده شد | ✓ | - |
| تأیید/رد برگشت کالا | ✓ | ✓ |
| تعیین قیمت تعمیر | ✓ | ✓ |
| تخفیف و کمپین | ✓ | ✓ (از پنل مدیر) |

**نوتیف‌های کارمند**

| رویداد | داخلی | SMS |
|--------|-------|-----|
| سفارش جدید برای تأیید | ✓ | - |
| اساین شدن تسک | ✓ | - |
| یک روز مانده به deadline تسک | ✓ | ✓ |
| تأیید/رد درخواست (مرخصی، مساعده) | ✓ | - |
| پیامک اختصاصی از پنل مدیر | - | ✓ |

**نوتیف‌های تعمیرکار**

| رویداد | داخلی | SMS |
|--------|-------|-----|
| سفارش تعمیر جدید | ✓ | - |
| تأیید قیمت توسط مشتری | ✓ | ✓ |
| رد قیمت توسط مشتری | ✓ | - |

**مدیریت نوتیف‌ها**
- Mark as Read (تکی و دسته‌ای)
- تاریخچه نوتیف‌ها قابل مشاهده
- پاک‌سازی خودکار تاریخچه ماهی یک‌بار (Celery Beat)
- کاربر می‌تواند ترجیح نوتیف‌ها را تنظیم کند

---

### ۴.۱۳ E-commerce — فروشگاه اینترنتی

**صفحات عمومی سایت (بدون لاگین)**
- همه صفحات قابل مشاهده برای بازدیدکننده ناشناس
- مشتری می‌تواند محصول انتخاب و به سبد خرید اضافه کند
- قبل از نهایی‌کردن سفارش و پرداخت: ثبت‌نام / ورود اجباری است

**سبد خرید (Cart)**
- Session-based برای ناشناس، User-based پس از ورود
- امکان ذخیره سبد خرید پس از ورود

**Checkout Flow**
1. بررسی سبد خرید
2. ورود / ثبت‌نام (اگر ناشناس)
3. انتخاب آدرس تحویل
4. بررسی قیمت نهایی + مالیات
5. هدایت به درگاه پرداخت (Placeholder)
6. تأیید پرداخت → ثبت سفارش → کسر موجودی

**پرداخت در محل:** وجود ندارد — فقط پرداخت آنلاین

**صفحات سایت**
- صفحه اصلی (بنر، اطلاعیه، معرفی بخش‌ها)
- فروشگاه کالا (سرچ + فیلتر دسته‌بندی + فیلتر قیمت)
- فروشگاه اکانت (انتخاب بازی → محاسبه قیمت → سفارش)
- مقالات (CRUD از پنل)
- ویدیوهای آموزشی رایگان (آموزش ساین‌این اکانت‌های سونی)
- ثبت رزومه
- درباره ما (قابل ویرایش از پنل)
- هدر و فوتر ثابت در همه صفحات (نه پنل‌ها)

---

### ۴.۱۴ Documents & Assets — اسناد و دارایی‌ها

**مدیریت اسناد**
- دسته‌بندی سه‌لایه
- CRUD کامل با فیلد‌های: عنوان، نوع، تاریخ، فایل پیوست، توضیحات
- قابل جستجو و فیلتر

**دارایی‌های حقیقی**
- دسته‌بندی دولایه
- اطلاعات: نام، ارزش خرید، تاریخ خرید، وضعیت، محل استقرار (شعبه)
- CRUD کامل

---

## ۵. معماری دیتابیس — ERD کامل

> نام‌گذاری جداول به سبک Django (app_modelname)

### ۵.۱ Core

```sql
-- core_user
id              UUID PK
phone           VARCHAR(15) UNIQUE NOT NULL
full_name       VARCHAR(100)
is_active       BOOLEAN DEFAULT true
is_admin        BOOLEAN DEFAULT false
created_at      TIMESTAMP
updated_at      TIMESTAMP

-- core_role
id              SERIAL PK
name            VARCHAR(50) UNIQUE NOT NULL   -- 'cashier', 'accountant', 'custom_xyz'
display_name    VARCHAR(100)
is_default      BOOLEAN                       -- آیا نقش پیش‌فرض سیستم است
created_at      TIMESTAMP

-- core_userrole  (Many-to-Many: User ↔ Role)
id              SERIAL PK
user_id         UUID FK → core_user
role_id         INT FK → core_role
branch_id       INT FK → core_branch (nullable — نقش در کدام شعبه)
assigned_at     TIMESTAMP

-- core_module
id              SERIAL PK
name            VARCHAR(50) UNIQUE  -- 'orders', 'inventory', 'accounting', ...
display_name    VARCHAR(100)

-- core_permission
id              SERIAL PK
role_id         INT FK → core_role
module_id       INT FK → core_module
can_read        BOOLEAN DEFAULT false
can_write       BOOLEAN DEFAULT false

-- core_branch
id              SERIAL PK
name            VARCHAR(100)
address         TEXT
phone           VARCHAR(20)
is_active       BOOLEAN DEFAULT true
created_at      TIMESTAMP

-- core_auditlog
id              BIGSERIAL PK
user_id         UUID FK → core_user (nullable)
action          VARCHAR(20)   -- CREATE / UPDATE / DELETE
model_name      VARCHAR(100)
object_id       VARCHAR(100)
before          JSONB
after           JSONB
ip_address      INET
created_at      TIMESTAMP

-- INDEX: core_auditlog(model_name, object_id)
-- INDEX: core_auditlog(user_id)
-- INDEX: core_auditlog(created_at)
```

### ۵.۲ Inventory

```sql
-- inventory_category  (سه‌لایه — self-referential)
id              SERIAL PK
name            VARCHAR(100)
parent_id       INT FK → inventory_category (nullable)
level           SMALLINT  -- 1, 2, 3
slug            VARCHAR(120) UNIQUE

-- inventory_product
id              SERIAL PK
name            VARCHAR(200)
category_id     INT FK → inventory_category
barcode_prefix  VARCHAR(50)
buy_price       DECIMAL(12,2)
sell_price      DECIMAL(12,2)
description     TEXT
is_active       BOOLEAN DEFAULT true
created_at      TIMESTAMP

-- inventory_stockitem  (هر واحد فیزیکی)
id              BIGSERIAL PK
product_id      INT FK → inventory_product
branch_id       INT FK → core_branch
barcode         VARCHAR(100) UNIQUE
serial_number   VARCHAR(100)
status          VARCHAR(20)  -- available / sold / returned / transferred / damaged
created_at      TIMESTAMP

-- INDEX: inventory_stockitem(branch_id, status)
-- INDEX: inventory_stockitem(barcode)

-- inventory_stockmovement
id              BIGSERIAL PK
item_id         BIGINT FK → inventory_stockitem
movement_type   VARCHAR(30)  -- purchase/sale/return/transfer_out/transfer_in/adjustment
from_branch_id  INT FK → core_branch (nullable)
to_branch_id    INT FK → core_branch (nullable)
order_id        BIGINT (nullable — اگر مرتبط به سفارش)
user_id         UUID FK → core_user
note            TEXT
created_at      TIMESTAMP

-- inventory_transfer
id              SERIAL PK
from_branch_id  INT FK → core_branch
to_branch_id    INT FK → core_branch
requested_by    UUID FK → core_user
approved_by     UUID FK → core_user (nullable)
status          VARCHAR(20)  -- pending/approved/in_transit/completed/cancelled
items           JSONB        -- [{item_id, product_name}]
notes           TEXT
requested_at    TIMESTAMP
completed_at    TIMESTAMP
```

### ۵.۳ Accounts (PS/Xbox/Nintendo)

```sql
-- accounts_gameaccount
id              SERIAL PK
name            VARCHAR(100)         -- نام اکانت
email           VARCHAR(200) UNIQUE
password        VARCHAR(200)         -- رمزگذاری‌شده
account_type    VARCHAR(20)          -- ps_online / ps_offline / xbox / nintendo
total_capacity  INT                  -- ظرفیت کل (تخمینی یا خالی)
sold_count      INT DEFAULT 0        -- تعداد فروش‌های انجام‌شده
notes           TEXT
is_active       BOOLEAN DEFAULT true
created_at      TIMESTAMP

-- accounts_game
id              SERIAL PK
name            VARCHAR(200)
platform        VARCHAR(20)          -- ps / xbox / nintendo
image_url       VARCHAR(500)
is_active       BOOLEAN DEFAULT true

-- accounts_accountgame  (Many-to-Many: GameAccount ↔ Game)
id              SERIAL PK
account_id      INT FK → accounts_gameaccount
game_id         INT FK → accounts_game

-- accounts_accountsale  (لاگ فروش هر اکانت)
id              BIGSERIAL PK
account_id      INT FK → accounts_gameaccount
order_id        BIGINT FK → orders_order
customer_id     UUID FK → core_user
sold_games      JSONB               -- لیست بازی‌های فروخته‌شده
sold_at         TIMESTAMP
```

### ۵.۴ Orders

```sql
-- orders_order
id              BIGSERIAL PK
order_number    VARCHAR(30) UNIQUE   -- ORD-1404-00001
order_type      VARCHAR(30)          -- physical_sale/account_sale/repair/xbox_sale
channel         VARCHAR(20)          -- online / in_store
branch_id       INT FK → core_branch
customer_id     UUID FK → core_user
cashier_id      UUID FK → core_user (nullable)
status          VARCHAR(30)
subtotal        DECIMAL(12,2)
discount_amount DECIMAL(12,2)
discount_note   TEXT
tax_amount      DECIMAL(12,2)
total           DECIMAL(12,2)
payment_status  VARCHAR(20)          -- unpaid / partial / paid
courier_name    VARCHAR(100)
courier_phone   VARCHAR(20)
courier_fee     DECIMAL(10,2)
notes           TEXT
created_at      TIMESTAMP
updated_at      TIMESTAMP

-- INDEX: orders_order(customer_id)
-- INDEX: orders_order(branch_id, created_at)
-- INDEX: orders_order(status)

-- orders_orderitem
id              BIGSERIAL PK
order_id        BIGINT FK → orders_order
item_type       VARCHAR(30)   -- product / game_account / game / repair
product_id      INT FK → inventory_product (nullable)
stock_item_id   BIGINT FK → inventory_stockitem (nullable)
account_id      INT FK → accounts_gameaccount (nullable)
game_ids        JSONB                -- برای فروش اکانت
quantity        INT DEFAULT 1
unit_price      DECIMAL(12,2)
total_price     DECIMAL(12,2)

-- orders_invoice
id              BIGSERIAL PK
invoice_number  VARCHAR(30) UNIQUE   -- INV-1404-00001
order_id        BIGINT FK → orders_order
issued_at       TIMESTAMP
tax_rate        DECIMAL(5,2)
tax_amount      DECIMAL(12,2)
total           DECIMAL(12,2)
pdf_url         VARCHAR(500)

-- orders_payment
id              BIGSERIAL PK
order_id        BIGINT FK → orders_order
method          VARCHAR(30)   -- online / wallet / cash / pos
amount          DECIMAL(12,2)
status          VARCHAR(20)   -- pending / completed / failed / refunded
reference_code  VARCHAR(100)
paid_by         UUID FK → core_user
paid_at         TIMESTAMP
note            TEXT

-- orders_refund
id              BIGSERIAL PK
order_id        BIGINT FK → orders_order
requested_by    UUID FK → core_user
approved_by     UUID FK → core_user (nullable)
reason          TEXT
amount          DECIMAL(12,2)
status          VARCHAR(20)   -- pending / approved / rejected / completed
refund_method   VARCHAR(30)   -- wallet / bank_transfer / cash
created_at      TIMESTAMP
completed_at    TIMESTAMP

-- orders_returnpolicy
id              SERIAL PK
category_id     INT FK → inventory_category
return_days     INT            -- تعداد روز مجاز برگشت
is_returnable   BOOLEAN DEFAULT true
notes           TEXT
```

### ۵.۵ Repair

```sql
-- repair_repairorder
id              BIGSERIAL PK
order_id        BIGINT FK → orders_order
device_type     VARCHAR(50)   -- console / controller / other
device_model    VARCHAR(100)
issue_description TEXT
technician_id   UUID FK → core_user (nullable)
technician_price DECIMAL(12,2)
markup_percent  DECIMAL(5,2)   -- از تنظیمات سیستم کپی می‌شود
final_price     DECIMAL(12,2)  -- technician_price × (1 + markup/100)
customer_approved BOOLEAN
approved_at     TIMESTAMP
status          VARCHAR(30)
notes           TEXT
created_at      TIMESTAMP

-- repair_settings
id              SERIAL PK
markup_percent  DECIMAL(5,2)  DEFAULT 20.00
updated_by      UUID FK → core_user
updated_at      TIMESTAMP
```

### ۵.۶ Procurement

```sql
-- procurement_supplier
id              SERIAL PK
company_name    VARCHAR(200)
contact_person  VARCHAR(100)
phone           VARCHAR(20)
email           VARCHAR(200)
address         TEXT
balance         DECIMAL(12,2) DEFAULT 0  -- بدهی به تأمین‌کننده
notes           TEXT
is_active       BOOLEAN DEFAULT true
created_at      TIMESTAMP

-- procurement_purchaserequest
id              SERIAL PK
request_number  VARCHAR(30) UNIQUE   -- PR-1404-00001
requested_by    UUID FK → core_user
branch_id       INT FK → core_branch
items           JSONB        -- [{product_name, quantity, notes}]
reason          TEXT
status          VARCHAR(20)  -- draft/submitted/approved/rejected/purchased
approved_by     UUID FK → core_user (nullable)
approved_at     TIMESTAMP
created_at      TIMESTAMP

-- procurement_purchaseorder
id              SERIAL PK
purchase_number VARCHAR(30) UNIQUE   -- PO-1404-00001
request_id      INT FK → procurement_purchaserequest (nullable)
supplier_id     INT FK → procurement_supplier
branch_id       INT FK → core_branch
items           JSONB        -- [{product_id, quantity, unit_price}]
total_amount    DECIMAL(12,2)
payment_method  VARCHAR(20)  -- cash / credit / cheque
supplier_invoice_no VARCHAR(100)
notes           TEXT
purchased_by    UUID FK → core_user
purchased_at    TIMESTAMP
```

### ۵.۷ Accounting

```sql
-- accounting_account  (Chart of Accounts)
id              SERIAL PK
code            VARCHAR(20) UNIQUE   -- 1100, 2100, 4000, ...
name            VARCHAR(200)
account_type    VARCHAR(20)          -- asset/liability/equity/revenue/expense
parent_id       INT FK → accounting_account (nullable)
is_system       BOOLEAN DEFAULT false  -- حساب‌های سیستمی قابل حذف نیستند
branch_id       INT FK → core_branch (nullable)  -- صندوق هر شعبه

-- accounting_journalentry
id              BIGSERIAL PK
entry_number    VARCHAR(30) UNIQUE
description     TEXT
reference_type  VARCHAR(50)   -- order/payment/salary/manual/procurement/refund
reference_id    VARCHAR(100)
created_by      UUID FK → core_user
entry_date      DATE
created_at      TIMESTAMP

-- accounting_journalline
id              BIGSERIAL PK
entry_id        BIGINT FK → accounting_journalentry
account_id      INT FK → accounting_account
debit           DECIMAL(14,2) DEFAULT 0
credit          DECIMAL(14,2) DEFAULT 0
note            TEXT

-- accounting_taxconfig
id              SERIAL PK
rate            DECIMAL(5,2)   -- درصد مالیات
effective_from  DATE
created_by      UUID FK → core_user

-- accounting_cashreconciliation  (صفرسازی روزانه صندوق)
id              SERIAL PK
branch_id       INT FK → core_branch
cashier_id      UUID FK → core_user
date            DATE
cash_amount     DECIMAL(12,2)
pos_amount      DECIMAL(12,2)
total_amount    DECIMAL(12,2)
notes           TEXT
journal_entry_id BIGINT FK → accounting_journalentry
created_at      TIMESTAMP

-- accounting_expensecategory  (سه‌لایه - self-referential)
id              SERIAL PK
name            VARCHAR(100)
parent_id       INT FK → accounting_expensecategory (nullable)
category_type   VARCHAR(10)   -- income / expense

-- accounting_transaction  (ساده‌سازی برای گزارش)
id              BIGSERIAL PK
type            VARCHAR(20)   -- income / expense
category_id     INT FK → accounting_expensecategory
amount          DECIMAL(12,2)
description     TEXT
branch_id       INT FK → core_branch
journal_entry_id BIGINT FK → accounting_journalentry
created_by      UUID FK → core_user
transaction_date DATE
```

### ۵.۸ HR

```sql
-- hr_employee
id              SERIAL PK
user_id         UUID FK → core_user UNIQUE
branch_id       INT FK → core_branch
national_id     VARCHAR(20) UNIQUE
hire_date       DATE
salary_type     VARCHAR(20)   -- fixed / commission / hybrid
base_salary     DECIMAL(12,2) DEFAULT 0
commission_rate DECIMAL(5,2)  DEFAULT 0
annual_leave_days INT DEFAULT 0
is_active       BOOLEAN DEFAULT true
contract_end    DATE (nullable)

-- hr_attendance
id              BIGSERIAL PK
employee_id     INT FK → hr_employee
date            DATE
check_in        TIMESTAMP
check_out       TIMESTAMP
status          VARCHAR(20)   -- present / absent / late / leave
note            TEXT

-- hr_leaverequest
id              SERIAL PK
employee_id     INT FK → hr_employee
leave_date      DATE
reason          TEXT
status          VARCHAR(20)   -- pending / approved / rejected
approved_by     UUID FK → core_user (nullable)
submitted_at    TIMESTAMP

-- hr_advancepayment
id              SERIAL PK
employee_id     INT FK → hr_employee
amount          DECIMAL(12,2)
remaining       DECIMAL(12,2)   -- مانده کسرنشده
reason          TEXT
status          VARCHAR(20)     -- pending / approved / rejected / settled
approved_by     UUID FK → core_user (nullable)
approved_at     TIMESTAMP
created_at      TIMESTAMP

-- hr_salaryrecord
id              SERIAL PK
employee_id     INT FK → hr_employee
period_month    INT
period_year     INT
base_salary     DECIMAL(12,2)
commission      DECIMAL(12,2)
task_reward     DECIMAL(12,2)
bonus           DECIMAL(12,2)
advance_deduct  DECIMAL(12,2)
penalty         DECIMAL(12,2)
tax_deduct      DECIMAL(12,2)
net_salary      DECIMAL(12,2)
journal_entry_id BIGINT FK → accounting_journalentry
paid_at         TIMESTAMP

-- hr_recruitment
id              SERIAL PK
full_name       VARCHAR(100)
phone           VARCHAR(20)
role_applied    VARCHAR(100)
resume_file     VARCHAR(500)
status          VARCHAR(20)   -- pending / reviewed / hired / rejected
notes           TEXT
submitted_at    TIMESTAMP
```

### ۵.۹ Tasks

```sql
-- tasks_task
id              SERIAL PK
title           VARCHAR(200)
description     TEXT
created_by      UUID FK → core_user
branch_id       INT FK → core_branch (nullable)
start_datetime  TIMESTAMP
deadline_datetime TIMESTAMP
status          VARCHAR(20)   -- open / in_progress / done / cancelled
reward_type     VARCHAR(20)   -- money / points / none
reward_value    DECIMAL(10,2) DEFAULT 0
is_bulk         BOOLEAN DEFAULT false
created_at      TIMESTAMP

-- tasks_taskassignment
id              SERIAL PK
task_id         INT FK → tasks_task
employee_id     INT FK → hr_employee
status          VARCHAR(20)   -- assigned / in_progress / done / cancelled
completed_at    TIMESTAMP
reward_paid     BOOLEAN DEFAULT false

-- INDEX: tasks_task(deadline_datetime) برای Celery Beat
```

### ۵.۱۰ CRM

```sql
-- crm_customerprofile
id              SERIAL PK
user_id         UUID FK → core_user UNIQUE
customer_type   VARCHAR(20)   -- b2c / b2b
company_name    VARCHAR(200)  (nullable — فقط B2B)
national_id     VARCHAR(30)   (nullable — فقط B2B)
credit_limit    DECIMAL(12,2) DEFAULT 0   -- سقف بدهی
current_debt    DECIMAL(12,2) DEFAULT 0
b2b_discount_rate DECIMAL(5,2) DEFAULT 0  -- درصد تخفیف روی بازی
is_credit_blocked BOOLEAN DEFAULT false
notes           TEXT

-- crm_wallettransaction
id              BIGSERIAL PK
user_id         UUID FK → core_user
transaction_type VARCHAR(20)  -- credit / debit
amount          DECIMAL(12,2)
balance_after   DECIMAL(12,2)
description     TEXT
reference_type  VARCHAR(50)
reference_id    VARCHAR(100)
created_by      UUID FK → core_user
created_at      TIMESTAMP

-- crm_smscampaign
id              SERIAL PK
title           VARCHAR(200)
message         TEXT
target          VARCHAR(20)   -- all / b2c / b2b / specific
target_users    JSONB         -- آرایه UUID برای specific
status          VARCHAR(20)   -- draft / sent / failed
sent_count      INT DEFAULT 0
created_by      UUID FK → core_user
sent_at         TIMESTAMP
```

### ۵.۱۱ Notifications

```sql
-- notifications_notification
id              BIGSERIAL PK
user_id         UUID FK → core_user
title           VARCHAR(200)
message         TEXT
notification_type VARCHAR(50)  -- order_update / task_deadline / repair_price / ...
reference_type  VARCHAR(50)
reference_id    VARCHAR(100)
is_read         BOOLEAN DEFAULT false
read_at         TIMESTAMP
created_at      TIMESTAMP

-- INDEX: notifications_notification(user_id, is_read)
-- INDEX: notifications_notification(created_at) برای پاک‌سازی ماهانه

-- notifications_preference
id              SERIAL PK
user_id         UUID FK → core_user UNIQUE
sms_order_update      BOOLEAN DEFAULT true
sms_task_deadline     BOOLEAN DEFAULT true
sms_repair_update     BOOLEAN DEFAULT true
```

### ۵.۱۲ E-commerce

```sql
-- ecommerce_cart
id              UUID PK
user_id         UUID FK → core_user (nullable — session cart)
session_key     VARCHAR(100) (nullable)
created_at      TIMESTAMP
updated_at      TIMESTAMP

-- ecommerce_cartitem
id              BIGSERIAL PK
cart_id         UUID FK → ecommerce_cart
item_type       VARCHAR(30)   -- product / game_account
product_id      INT FK → inventory_product (nullable)
game_ids        JSONB         (nullable — برای اکانت)
quantity        INT DEFAULT 1
unit_price      DECIMAL(12,2)

-- ecommerce_shippingaddress
id              SERIAL PK
user_id         UUID FK → core_user
full_name       VARCHAR(100)
phone           VARCHAR(20)
province        VARCHAR(100)
city            VARCHAR(100)
address         TEXT
postal_code     VARCHAR(20)
is_default      BOOLEAN DEFAULT false
```

### ۵.۱۳ Documents & Assets

```sql
-- documents_documentcategory  (سه‌لایه)
id              SERIAL PK
name            VARCHAR(100)
parent_id       INT FK → documents_documentcategory (nullable)

-- documents_document
id              SERIAL PK
title           VARCHAR(200)
category_id     INT FK → documents_documentcategory
doc_type        VARCHAR(50)
doc_date        DATE
file_url        VARCHAR(500)
description     TEXT
created_by      UUID FK → core_user
created_at      TIMESTAMP

-- documents_assetcategory  (دولایه)
id              SERIAL PK
name            VARCHAR(100)
parent_id       INT FK → documents_assetcategory (nullable)

-- documents_asset
id              SERIAL PK
name            VARCHAR(200)
category_id     INT FK → documents_assetcategory
purchase_price  DECIMAL(12,2)
purchase_date   DATE
branch_id       INT FK → core_branch
status          VARCHAR(30)  -- active / under_repair / retired
notes           TEXT
created_at      TIMESTAMP
```

---

## ۶. طراحی API

> پایه URL: `/api/v1/`  
> احراز هویت: `Authorization: Bearer <access_token>`  
> فرمت: JSON

### ۶.۱ Auth

```
POST   /auth/request-otp/          → ارسال OTP به شماره تلفن
POST   /auth/verify-otp/           → تأیید OTP و دریافت Token
POST   /auth/token/refresh/        → Refresh Access Token
POST   /auth/logout/               → لغو Refresh Token
GET    /auth/me/                   → اطلاعات کاربر جاری
GET    /auth/me/roles/             → نقش‌های کاربر جاری
```

### ۶.۲ Core / Admin

```
# Branch
GET    /branches/
POST   /branches/
GET    /branches/{id}/
PUT    /branches/{id}/
DELETE /branches/{id}/

# Role & Permission
GET    /roles/
POST   /roles/
GET    /roles/{id}/permissions/
PUT    /roles/{id}/permissions/    → آپدیت ماتریس دسترسی

# Audit Log
GET    /audit-logs/                → فیلتر: model, user, date_range
```

### ۶.۳ Inventory

```
# Category
GET    /inventory/categories/
POST   /inventory/categories/
PUT    /inventory/categories/{id}/

# Product
GET    /inventory/products/        → فیلتر: category, branch, status
POST   /inventory/products/
GET    /inventory/products/{id}/
PUT    /inventory/products/{id}/
DELETE /inventory/products/{id}/

# Stock Items
GET    /inventory/stock/           → فیلتر: product, branch, status
POST   /inventory/stock/bulk/      → افزودن دسته‌ای موجودی
GET    /inventory/stock/{id}/
PUT    /inventory/stock/{id}/status/

# Stock Movements
GET    /inventory/movements/       → فیلتر: branch, type, date_range

# Branch Transfer
GET    /inventory/transfers/
POST   /inventory/transfers/
PUT    /inventory/transfers/{id}/status/
```

### ۶.۴ Accounts

```
GET    /accounts/ps/               → فیلتر: type, is_active
POST   /accounts/ps/
GET    /accounts/ps/{id}/
PUT    /accounts/ps/{id}/
DELETE /accounts/ps/{id}/

GET    /accounts/ps/{id}/sales/    → لاگ فروش‌های اکانت

GET    /accounts/games/            → فیلتر: platform, account_id
POST   /accounts/games/
PUT    /accounts/games/{id}/

POST   /accounts/calculate-price/  → محاسبه قیمت اکانت بر اساس بازی‌های انتخابی
```

### ۶.۵ Orders

```
# Orders
GET    /orders/                    → فیلتر: type, status, channel, branch, date_range
POST   /orders/                    → ثبت سفارش
GET    /orders/{id}/
PUT    /orders/{id}/status/        → تغییر وضعیت
PUT    /orders/{id}/courier/       → ثبت / ویرایش پیک
POST   /orders/{id}/cancel/        → لغو سفارش

# Invoice
GET    /orders/{id}/invoice/
GET    /orders/{id}/invoice/pdf/

# Payment
POST   /orders/{id}/payment/       → ثبت پرداخت
GET    /orders/{id}/payments/

# Refund & Return
POST   /orders/{id}/refund/        → درخواست استرداد
PUT    /refunds/{id}/approve/
PUT    /refunds/{id}/reject/

# Return Policy
GET    /return-policies/
PUT    /return-policies/{category_id}/
```

### ۶.۶ Repair

```
GET    /repair/orders/             → فیلتر: status, technician, date_range
POST   /repair/orders/
GET    /repair/orders/{id}/
PUT    /repair/orders/{id}/accept/ → تعمیرکار قبول می‌کند
PUT    /repair/orders/{id}/price/  → تعمیرکار قیمت ثبت می‌کند
PUT    /repair/orders/{id}/customer-decision/  → تأیید/رد توسط مشتری
PUT    /repair/orders/{id}/complete/

GET    /repair/settings/
PUT    /repair/settings/           → تنظیم درصد سود مدیریت
```

### ۶.۷ Procurement

```
GET    /suppliers/
POST   /suppliers/
GET    /suppliers/{id}/
PUT    /suppliers/{id}/
GET    /suppliers/{id}/history/    → تاریخچه خرید

GET    /purchase-requests/
POST   /purchase-requests/
GET    /purchase-requests/{id}/
PUT    /purchase-requests/{id}/approve/
PUT    /purchase-requests/{id}/reject/

GET    /purchase-orders/
POST   /purchase-orders/           → ثبت خرید انجام‌شده
GET    /purchase-orders/{id}/
```

### ۶.۸ Accounting

```
# Chart of Accounts
GET    /accounting/accounts/
POST   /accounting/accounts/

# Journal Entries
GET    /accounting/journal/        → فیلتر: date_range, reference_type
POST   /accounting/journal/        → ورودی دستی
GET    /accounting/journal/{id}/

# Transactions (سطح ساده)
GET    /accounting/transactions/   → فیلتر: type, category, branch, date_range
POST   /accounting/transactions/

# Cash Reconciliation
GET    /accounting/reconciliation/
POST   /accounting/reconciliation/ → صفرسازی روزانه صندوق

# Tax Config
GET    /accounting/tax/
POST   /accounting/tax/

# Reports
GET    /reports/pnl/               → P&L با فیلتر date_range, branch
GET    /reports/cashflow/
GET    /reports/balance-sheet/
GET    /reports/vat/
GET    /reports/receivables/
GET    /reports/payables/

# Expense/Income Categories
GET    /accounting/categories/
POST   /accounting/categories/
```

### ۶.۹ HR

```
GET    /hr/employees/
POST   /hr/employees/
GET    /hr/employees/{id}/
PUT    /hr/employees/{id}/

GET    /hr/employees/{id}/attendance/
POST   /hr/attendance/             → ثبت ورود/خروج

GET    /hr/leave-requests/
POST   /hr/leave-requests/
PUT    /hr/leave-requests/{id}/approve/
PUT    /hr/leave-requests/{id}/reject/

GET    /hr/advance-payments/
POST   /hr/advance-payments/
PUT    /hr/advance-payments/{id}/approve/

GET    /hr/salaries/
POST   /hr/salaries/calculate/     → محاسبه حقوق ماه
POST   /hr/salaries/pay/           → ثبت پرداخت حقوق

GET    /hr/recruitment/
POST   /hr/recruitment/            → public endpoint برای ارسال رزومه
PUT    /hr/recruitment/{id}/hire/
DELETE /hr/recruitment/{id}/
```

### ۶.۱۰ Tasks

```
GET    /tasks/
POST   /tasks/
GET    /tasks/{id}/
PUT    /tasks/{id}/
DELETE /tasks/{id}/
POST   /tasks/bulk-assign/         → اساین دسته‌ای به چند کارمند
PUT    /tasks/{id}/status/
PUT    /tasks/assignments/{id}/complete/
```

### ۶.۱۱ CRM

```
GET    /customers/                 → فیلتر: type (b2c/b2b), debt, date_range
GET    /customers/{id}/
PUT    /customers/{id}/
GET    /customers/{id}/orders/
GET    /customers/{id}/wallet/

POST   /customers/{id}/wallet/credit/    → شارژ کیف پول
POST   /customers/{id}/wallet/debit/     → کسر از کیف پول

PUT    /customers/{id}/credit-limit/
PUT    /customers/{id}/b2b-discount/

POST   /sms/send/                  → ارسال پیامک تکی یا دسته‌ای
GET    /sms/campaigns/
```

### ۶.۱۲ Notifications

```
GET    /notifications/             → لیست با فیلتر is_read
PUT    /notifications/{id}/read/
POST   /notifications/mark-all-read/
GET    /notifications/preferences/
PUT    /notifications/preferences/

# WebSocket endpoint
WS     /ws/notifications/         → احراز هویت با JWT در header
```

### ۶.۱۳ E-commerce

```
# Cart
GET    /cart/
POST   /cart/items/
PUT    /cart/items/{id}/
DELETE /cart/items/{id}/
POST   /cart/merge/                → ادغام cart ناشناس با cart لاگین‌شده

# Checkout
POST   /checkout/                  → ایجاد سفارش از cart
POST   /payment/initiate/          → Placeholder → هدایت به درگاه

# Shipping Address
GET    /addresses/
POST   /addresses/
PUT    /addresses/{id}/
DELETE /addresses/{id}/

# Public Product Catalog
GET    /store/products/            → عمومی، بدون احراز هویت
GET    /store/products/{id}/
GET    /store/accounts/games/      → لیست بازی‌های موجود در اکانت‌ها
GET    /store/articles/
GET    /store/articles/{slug}/
GET    /store/videos/
GET    /store/about/
```

### ۶.۱۴ Reports (داشبورد مدیر)

```
GET    /reports/sales/             → فیلتر: branch, date_range, type
GET    /reports/employees/         → عملکرد کارمندان
GET    /reports/customers/         → گزارش مشتریان
GET    /reports/inventory/         → گردش انبار، موجودی
GET    /reports/b2b/               → گزارش مشتریان B2B
```

---

## ۷. سیستم نقش‌ها و دسترسی‌ها — RBAC

### ۷.۱ نقش‌های پیش‌فرض

| کد نقش | نام نمایشی | توضیح |
|--------|-----------|-------|
| `admin` | مدیر کل | دسترسی کامل — فقط یک نفر |
| `cashier` | صندوق‌دار | ثبت سفارش، تأیید پرداخت، مدیریت پیک |
| `account_setter` | اکانت‌ستر | ست‌کردن اکانت‌های اساین‌شده |
| `accountant` | حسابدار | حسابداری، دارایی، اسناد |
| `warehouse` | انباردار | انبار، درخواست خرید، انتقال |
| `repair_technician` | تعمیرکار | سفارش‌های تعمیر |
| `customer` | مشتری عادی B2C | پنل مشتری |
| `b2b_customer` | مشتری سازمانی | پنل مشتری + ویژگی‌های B2B |

### ۷.۲ ماتریس دسترسی پیش‌فرض

| ماژول | Admin | Cashier | Accountant | Warehouse | Account Setter |
|-------|-------|---------|-----------|-----------|----------------|
| orders | R+W | R+W | R | R | R |
| inventory | R+W | R | R | R+W | R |
| accounts | R+W | R | R | R | R+W |
| accounting | R+W | R | R+W | - | - |
| hr | R+W | - | R | - | - |
| tasks | R+W | R | R | R | R |
| crm | R+W | R+W | R | - | - |
| procurement | R+W | - | R | R+W | - |
| repair | R+W | R+W | R | - | - |
| documents | R+W | - | R+W | - | - |
| reports | R+W | R | R+W | R | - |
| site_management | R+W | - | - | - | - |
| branch | R+W | - | - | - | - |

> مدیر می‌تواند ماتریس را برای نقش‌های سفارشی یا پیش‌فرض تغییر دهد.

### ۷.۳ چند نقش برای یک کاربر

- یک کاربر می‌تواند چند نقش داشته باشد
- Admin فقط یک نفر است
- سوئیچ نقش از طریق تب در پنل یکپارچه
- بالاترین سطح دسترسی بین نقش‌های فعال اعمال می‌شود

---

## ۸. سرویس‌های جانبی و Placeholder ها

```python
# backend/apps/core/services/sms.py
def send_sms(phone: str, message: str) -> bool:
    """
    Placeholder: ارسال پیامک
    جایگزینی با سرویس واقعی (مثل کاوه‌نگار، ملی‌پیامک)
    """
    # TODO: implement real SMS provider
    import logging
    logging.info(f"SMS to {phone}: {message}")
    return True

# backend/apps/core/services/otp.py
def send_otp(phone: str, code: str) -> bool:
    """
    Placeholder: ارسال OTP
    """
    # TODO: implement OTP SMS delivery
    return send_sms(phone, f"کد ورود دکترگیم: {code}")

# backend/apps/core/services/payment.py
def initiate_payment(amount: int, order_id: str, callback_url: str) -> dict:
    """
    Placeholder: ایجاد لینک پرداخت و هدایت به درگاه
    Returns: {'payment_url': str, 'authority': str}
    """
    # TODO: implement Zarinpal / IDPay / etc.
    raise NotImplementedError("Payment gateway not implemented yet")

def verify_payment(authority: str) -> dict:
    """
    Placeholder: تأیید پرداخت پس از بازگشت از درگاه
    Returns: {'status': 'ok'|'failed', 'ref_id': str}
    """
    # TODO: implement payment verification
    raise NotImplementedError("Payment gateway not implemented yet")
```

---

## ۹. فازبندی و تسک‌بندی توسعه

> هر تسک شامل بخش **BackEnd** و **FrontEnd** است.  
> ترتیب: ابتدا BackEnd پیاده‌سازی می‌شود، سپس FrontEnd.

---

### فاز ۱ — زیرساخت، احراز هویت و Core

---

#### مرحله ۱.۱ — راه‌اندازی محیط و پروژه

**BackEnd**
- [ ] ایجاد ساختار Monorepo (backend / frontend / nginx)
- [ ] نوشتن `docker-compose.yml` با سرویس‌های: nginx, backend, celery, celery-beat, frontend, redis
- [ ] ایجاد پروژه Django با ساختار `config/settings/base.py` و `development.py`
- [ ] تنظیم `INSTALLED_APPS`، `DATABASES`، `CORS`، `REST_FRAMEWORK`
- [ ] نوشتن `.env.example` با تمام متغیرهای محیطی
- [ ] راه‌اندازی `Django Channels` با Redis Channel Layer
- [ ] راه‌اندازی `Celery` و `Celery Beat`
- [ ] تنظیم `Nginx` برای Reverse Proxy (api → Django, ws → Channels, / → Next.js)
- [ ] نوشتن Makefile با دستورات رایج (build, migrate, shell, logs)

**FrontEnd**
- [ ] ایجاد پروژه Next.js 14+ با TypeScript و App Router
- [ ] نصب و تنظیم Tailwind CSS + Shadcn/UI
- [ ] تنظیم Axios با interceptors برای JWT و Refresh Token
- [ ] ایجاد Zustand store برای Auth
- [ ] تنظیم WebSocket client با auto-reconnect
- [ ] ایجاد Layout اصلی (پنل Admin، Employee، Customer، Public)
- [ ] تنظیم متغیرهای محیطی Next.js

---

#### مرحله ۱.۲ — احراز هویت و مدیریت کاربران (Core)

**BackEnd**
- [ ] مدل `User` با شماره تلفن به عنوان شناسه اصلی
- [ ] مدل `OTPCode` با منطق انقضا و تعداد تلاش
- [ ] پیاده‌سازی `send_otp` Placeholder
- [ ] API: `POST /auth/request-otp/` و `POST /auth/verify-otp/`
- [ ] یکپارچه‌سازی `SimpleJWT` (Access + Refresh Token)
- [ ] API: `POST /auth/token/refresh/`، `POST /auth/logout/`، `GET /auth/me/`
- [ ] مدل `Role`، `Module`، `Permission` (RBAC)
- [ ] مدل `UserRole` با ارتباط به Branch
- [ ] API مدیریت نقش‌ها و دسترسی‌ها
- [ ] مدل `Branch` و API کامل CRUD
- [ ] مدل `AuditLog` و middleware لاگ‌گیری خودکار

**FrontEnd**
- [ ] صفحه ورود (ورود شماره تلفن → ارسال OTP → تأیید)
- [ ] ذخیره Token در memory + Cookie برای Refresh
- [ ] Guard برای صفحات محافظت‌شده
- [ ] صفحه پروفایل کاربری
- [ ] کامپوننت سوئیچ نقش (تب‌های مختلف برای نقش‌های متعدد)
- [ ] صفحه مدیریت شعبه‌ها (لیست + CRUD)
- [ ] صفحه مدیریت نقش‌ها و ماتریس دسترسی

---

### فاز ۲ — انبارداری و مدیریت اکانت‌ها

---

#### مرحله ۲.۱ — انبار کالا و بازی فیزیکی

**BackEnd**
- [ ] مدل `Category` (سه‌لایه self-referential)
- [ ] مدل `Product` با فیلدهای کامل
- [ ] مدل `StockItem` (هر واحد با بارکد یونیک، وابسته به شعبه)
- [ ] مدل `StockMovement` با تمام انواع عملیات
- [ ] Signal برای کسر خودکار موجودی هنگام فروش
- [ ] API کامل CRUD برای Category و Product
- [ ] API موجودی: لیست، افزودن تکی و دسته‌ای
- [ ] API گردش انبار با فیلترهای پیشرفته
- [ ] مدل `BranchTransfer` و API فرآیند انتقال

**FrontEnd**
- [ ] صفحه انبار کالا: لیست محصولات با جستجو و فیلتر
- [ ] کلیک روی محصول → نمایش موجودی‌های مجزا با بارکد
- [ ] فرم افزودن محصول و موجودی جدید
- [ ] صفحه گردش انبار (Stock Movement Log)
- [ ] صفحه درخواست انتقال بین شعبه

---

#### مرحله ۲.۲ — مدیریت اکانت‌ها

**BackEnd**
- [ ] مدل `GameAccount` (PS آنلاین/آفلاین، Xbox، Nintendo)
- [ ] مدل `Game` با پلتفرم‌های مختلف
- [ ] مدل `AccountGame` (Many-to-Many)
- [ ] مدل `AccountSale` (لاگ فروش اکانت)
- [ ] Signal برای افزایش `sold_count` پس از فروش
- [ ] API CRUD اکانت‌ها
- [ ] API `POST /accounts/calculate-price/` — محاسبه بر اساس بازی‌های انتخابی
- [ ] API لاگ فروش هر اکانت

**FrontEnd**
- [ ] صفحه انبار اکانت‌های آنلاین PS
- [ ] صفحه انبار اکانت‌های آفلاین PS
- [ ] کامپوننت مشاهده لاگ فروش اکانت
- [ ] فرم افزودن/ویرایش اکانت
- [ ] کامپوننت انتخاب بازی و محاسبه قیمت زنده

---

### فاز ۳ — سیستم سفارش‌ها و فاکتور

---

#### مرحله ۳.۱ — ثبت و مدیریت سفارش

**BackEnd**
- [ ] مدل `Order` با تمام انواع سفارش و فیلدهای کامل
- [ ] مدل `OrderItem` برای آیتم‌های متنوع
- [ ] منطق ثبت تخفیف + ثبت نام ثبت‌کننده
- [ ] منطق B2B: اعمال خودکار تخفیف بازی
- [ ] API `POST /orders/` برای انواع مختلف سفارش
- [ ] API تغییر وضعیت سفارش
- [ ] API ثبت مشخصات پیک
- [ ] API لغو سفارش با منطق برگشت موجودی
- [ ] مدل `ReturnPolicy` و API تنظیم

**FrontEnd**
- [ ] صفحه لیست سفارش‌ها (با تب‌های نوع سفارش)
- [ ] فرم ثبت سفارش حضوری (چندمرحله‌ای)
- [ ] صفحه جزئیات سفارش با Timeline وضعیت
- [ ] کامپوننت ثبت اطلاعات پیک
- [ ] کامپوننت تغییر وضعیت سفارش

---

#### مرحله ۳.۲ — فاکتور و پرداخت

**BackEnd**
- [ ] مدل `Invoice` با شماره‌گذاری پیوسته (INV-YYYY-NNNNN)
- [ ] منطق محاسبه VAT بر اساس `TaxConfig` جاری
- [ ] API تولید PDF فاکتور (WeasyPrint یا ReportLab)
- [ ] مدل `Payment` با انواع پرداخت
- [ ] API ثبت پرداخت (حضوری توسط صندوق‌دار / آنلاین)
- [ ] API `initiate_payment` Placeholder
- [ ] Journal Entry خودکار پس از ثبت پرداخت
- [ ] مدل `Refund` و API فرآیند استرداد

**FrontEnd**
- [ ] صفحه پیش‌نمایش فاکتور (قابل پرینت)
- [ ] کامپوننت ثبت پرداخت حضوری
- [ ] کامپوننت پرداخت آنلاین (placeholder)
- [ ] فرم درخواست استرداد
- [ ] صفحه مدیریت استرداد‌ها (پنل Admin)

---

### فاز ۴ — تعمیرات و Procurement

---

#### مرحله ۴.۱ — سیستم تعمیر

**BackEnd**
- [ ] مدل `RepairOrder` و `RepairSettings`
- [ ] API ثبت سفارش تعمیر (آنلاین و حضوری)
- [ ] API قبول سفارش توسط تعمیرکار
- [ ] API ثبت قیمت + محاسبه خودکار markup
- [ ] API تأیید/رد قیمت توسط مشتری
- [ ] API تکمیل تعمیر و تحویل
- [ ] API تنظیم درصد سود مدیریت
- [ ] Journal Entry برای درآمد تعمیر و حق‌الزحمه تعمیرکار

**FrontEnd**
- [ ] پنل تعمیرکار: لیست سفارش‌ها با تب وضعیت
- [ ] فرم ثبت قیمت تعمیر + نمایش قیمت نهایی با markup
- [ ] کامپوننت تأیید/رد قیمت در پنل مشتری
- [ ] صفحه تنظیم markup در پنل Admin

---

#### مرحله ۴.۲ — Procurement و مدیریت تأمین‌کنندگان

**BackEnd**
- [ ] مدل `Supplier` و API CRUD
- [ ] مدل `PurchaseRequest` و API گردش کار (draft→submit→approve→reject→purchase)
- [ ] مدل `PurchaseOrder` و API ثبت خرید
- [ ] Signal: ثبت خودکار StockMovement پس از ثبت خرید
- [ ] Journal Entry خودکار برای خرید

**FrontEnd**
- [ ] صفحه مدیریت تأمین‌کنندگان
- [ ] صفحه درخواست خرید (ثبت و پیگیری)
- [ ] صفحه تأیید درخواست‌های خرید (پنل Admin)
- [ ] صفحه ثبت خرید انجام‌شده

---

### فاز ۵ — حسابداری دوطرفه و گزارش‌های مالی

---

#### مرحله ۵.۱ — زیرساخت حسابداری

**BackEnd**
- [ ] مدل `Account` (نمودار حساب‌ها — Chart of Accounts)
- [ ] مدل `JournalEntry` و `JournalLine`
- [ ] سرویس `JournalService` برای تولید خودکار Journal از رویدادهای مختلف
- [ ] مدل `TaxConfig` و API تنظیم نرخ مالیات
- [ ] API دستی ثبت Journal Entry (برای ادمین/حسابدار)
- [ ] مدل `ExpenseIncomeCategory` (سه‌لایه) و API

**FrontEnd**
- [ ] صفحه نمودار حساب‌ها
- [ ] صفحه دفتر Journal (با فیلتر)
- [ ] فرم ثبت دستی Journal Entry
- [ ] صفحه دسته‌بندی هزینه/درآمد

---

#### مرحله ۵.۲ — صندوق و گزارش‌های مالی

**BackEnd**
- [ ] مدل `CashReconciliation` و API صفرسازی روزانه
- [ ] Journal Entry خودکار برای صفرسازی
- [ ] API گزارش P&L (سود و زیان) با فیلتر date_range و branch
- [ ] API گزارش Cash Flow
- [ ] API گزارش Balance Sheet
- [ ] API گزارش VAT
- [ ] API حساب‌های دریافتنی و پرداختنی

**FrontEnd**
- [ ] صفحه صفرسازی صندوق روزانه
- [ ] صفحه گزارش P&L با نمودار
- [ ] صفحه گزارش Cash Flow
- [ ] صفحه گزارش VAT
- [ ] کامپوننت فیلتر تاریخ شمسی جامع (date range picker)

---

### فاز ۶ — HR، تسک‌منیجر و CRM

---

#### مرحله ۶.۱ — ماژول HR

**BackEnd**
- [ ] مدل `Employee` با تمام فیلدها (قرارداد، حقوق، شعبه)
- [ ] مدل `Attendance` و API ثبت ورود/خروج
- [ ] مدل `LeaveRequest` و API گردش کار
- [ ] مدل `AdvancePayment` و API گردش کار
- [ ] مدل `SalaryRecord` و سرویس محاسبه حقوق (base + commission + reward − advance − penalty)
- [ ] Journal Entry خودکار برای پرداخت حقوق
- [ ] مدل `Recruitment` و API (شامل public endpoint)

**FrontEnd**
- [ ] صفحه لیست و جزئیات کارمندان
- [ ] فرم افزودن/ویرایش کارمند
- [ ] صفحه حضور و غیاب
- [ ] فرم درخواست مرخصی (پنل کارمند)
- [ ] صفحه مدیریت درخواست‌های مرخصی (پنل Admin)
- [ ] فرم درخواست مساعده
- [ ] صفحه محاسبه و پرداخت حقوق

---

#### مرحله ۶.۲ — Task Manager

**BackEnd**
- [ ] مدل `Task` با `start_datetime` و `deadline_datetime`
- [ ] مدل `TaskAssignment` برای اساین به چند کارمند
- [ ] API CRUD تسک + API اساین دسته‌ای
- [ ] API تغییر وضعیت تسک و ثبت تکمیل
- [ ] Celery Beat Task: هر روز بررسی deadlineها → ارسال نوتیف + SMS یک روز قبل

**FrontEnd**
- [ ] صفحه تسک‌منیجر با نمای تقویم (ماهانه + هفتگی)
- [ ] فرم افزودن تسک (تکی و دسته‌ای)
- [ ] صفحه تسک‌های کارمند در پنل خودش
- [ ] کامپوننت وضعیت و پیشرفت تسک

---

#### مرحله ۶.۳ — CRM و B2B

**BackEnd**
- [ ] مدل `CustomerProfile` (B2C و B2B)
- [ ] منطق سقف بدهی: بلاک خودکار هنگام تجاوز از `credit_limit`
- [ ] مدل `WalletTransaction` و API شارژ/کسر کیف پول
- [ ] API تنظیم `credit_limit` و `b2b_discount_rate` (کلی و به ازای هر مشتری)
- [ ] مدل `SMSCampaign` و API ارسال پیامک تکی/دسته‌ای
- [ ] `send_sms` Placeholder اتصال به کمپین‌ها

**FrontEnd**
- [ ] صفحه لیست مشتریان (جدا B2C / B2B)
- [ ] صفحه جزئیات مشتری (سفارش‌ها، بدهی، کیف پول)
- [ ] فرم تنظیم سقف بدهی و تخفیف B2B
- [ ] صفحه ارسال پیامک (تکی و دسته‌ای)
- [ ] پنل مشتری: کیف پول و تاریخچه تراکنش‌ها

---

### فاز ۷ — E-commerce و پنل مشتری

---

#### مرحله ۷.۱ — سایت عمومی و Cart

**BackEnd**
- [ ] API عمومی Catalog محصولات (بدون auth)
- [ ] API فروشگاه اکانت: لیست بازی‌ها → محاسبه قیمت
- [ ] مدل `Cart` و `CartItem` (Session-based + User-based)
- [ ] API `POST /cart/merge/` برای ادغام cart ناشناس
- [ ] API مقالات (CRUD از پنل + نمایش عمومی)
- [ ] API ویدیوهای آموزشی (CRUD از پنل + نمایش عمومی)
- [ ] API تنظیمات سایت (درباره ما، هدر، فوتر)

**FrontEnd**
- [ ] صفحه اصلی (بنر، اطلاعیه، اینترو)
- [ ] صفحه فروشگاه کالا (سرچ + فیلتر دسته‌بندی + فیلتر قیمت)
- [ ] صفحه فروشگاه اکانت (انتخاب بازی + محاسبه قیمت)
- [ ] صفحه سبد خرید
- [ ] صفحه مقالات و جزئیات مقاله
- [ ] صفحه ویدیوهای آموزشی
- [ ] صفحه درباره ما و ثبت رزومه
- [ ] هدر و فوتر ثابت

---

#### مرحله ۷.۲ — Checkout و پنل مشتری

**BackEnd**
- [ ] API `POST /checkout/` → ایجاد سفارش از cart → کسر موجودی
- [ ] API آدرس‌های تحویل (CRUD)
- [ ] API `POST /payment/initiate/` Placeholder
- [ ] API تأیید دریافت سفارش توسط مشتری
- [ ] API لیست سفارش‌های مشتری با وضعیت

**FrontEnd**
- [ ] فلوی Checkout چندمرحله‌ای (سبد → آدرس → پرداخت)
- [ ] هدایت به درگاه (Placeholder → صفحه موفقیت)
- [ ] پنل مشتری: صفحه سفارش‌ها (با تب‌های نوع و وضعیت)
- [ ] کامپوننت وضعیت سفارش با آیکون و متن
- [ ] دکمه «تحویل گرفتم»
- [ ] کامپوننت پرداخت آنلاین از پنل

---

### فاز ۸ — نوتیفیکیشن، Audit و داشبورد

---

#### مرحله ۸.۱ — سیستم نوتیفیکیشن

**BackEnd**
- [ ] مدل `Notification` و `NotificationPreference`
- [ ] سرویس `NotificationService` با متدهای ارسال به هر رول
- [ ] WebSocket Consumer در Django Channels
- [ ] ارسال نوتیف Real-time پس از رویدادهای کلیدی
- [ ] Celery Task برای ارسال SMS در رویدادهای مهم
- [ ] Celery Beat: پاک‌سازی ماهانه تاریخچه نوتیف‌ها
- [ ] API لیست، Mark as Read، و تنظیمات ترجیح

**FrontEnd**
- [ ] کامپوننت Notification Bell در هدر پنل (Real-time)
- [ ] Dropdown لیست نوتیف‌ها با Mark as Read
- [ ] صفحه تاریخچه نوتیف‌ها
- [ ] صفحه تنظیمات ترجیح نوتیف‌ها

---

#### مرحله ۸.۲ — داشبورد مدیر

**BackEnd**
- [ ] API گزارش فروش (تفکیکی: نوع، شعبه، بازه تاریخ)
- [ ] API گزارش عملکرد کارمندان (سفارش، تسک، درآمد)
- [ ] API گزارش مشتریان (خرید، بدهی، B2B vs B2C)
- [ ] API گزارش گردش انبار
- [ ] API آمار کلی داشبورد (KPI cards)

**FrontEnd**
- [ ] داشبورد مدیر با KPI Cards
- [ ] نمودار فروش (خطی — بازه زمانی)
- [ ] نمودار عملکرد کارمندان (میله‌ای)
- [ ] نمودار دسته‌بندی سفارش‌ها (دایره‌ای)
- [ ] نمودار مقایسه شعبه‌ها
- [ ] پیشخوان کارمند (خلاصه عملکرد شخصی)
- [ ] پیشخوان تعمیرکار

---

### فاز ۹ — مدیریت سایت و بهینه‌سازی

---

#### مرحله ۹.۱ — مدیریت محتوای سایت

**BackEnd**
- [ ] API مقالات CRUD (از پنل Admin)
- [ ] API ویدیوهای آموزشی CRUD
- [ ] API بنرهای سایت CRUD
- [ ] API تنظیمات سایت (درباره ما، اطلاعات تماس، لینک‌های شبکه اجتماعی)
- [ ] مدیریت رزومه‌ها: لیست، تغییر وضعیت، حذف

**FrontEnd**
- [ ] صفحه مدیریت مقالات (CRUD کامل)
- [ ] صفحه مدیریت ویدیوها
- [ ] صفحه مدیریت بنرها
- [ ] صفحه تنظیمات سایت
- [ ] صفحه رزومه‌های استخدام

---

#### مرحله ۹.۲ — اسناد، دارایی و Audit Log UI

**BackEnd**
- [ ] مدل `DocumentCategory` و `Document` با CRUD کامل
- [ ] مدل `AssetCategory` و `Asset` با CRUD کامل
- [ ] API جستجو و فیلتر پیشرفته برای اسناد
- [ ] AuditLog: اطمینان از لاگ تمام رویدادهای مهم در تمام ماژول‌ها

**FrontEnd**
- [ ] صفحه مدیریت اسناد (با دسته‌بندی سه‌لایه)
- [ ] صفحه مدیریت دارایی‌های حقیقی
- [ ] صفحه Audit Log (با جستجو و فیلتر)

---

#### مرحله ۹.۳ — بهینه‌سازی و استقرار

**BackEnd**
- [ ] بهینه‌سازی Query های N+1 با `select_related` و `prefetch_related`
- [ ] پیاده‌سازی Cache با Redis برای گزارش‌های سنگین
- [ ] تنظیم `Database Connection Pooling`
- [ ] نوشتن Index های مهم دیتابیس (بررسی EXPLAIN ANALYZE)
- [ ] نوشتن Unit Tests برای ماژول‌های حیاتی (Auth, Orders, Accounting)
- [ ] تولید مستندات API با `drf-spectacular` (Swagger/OpenAPI)
- [ ] تنظیم Production settings (DEBUG=False، ALLOWED_HOSTS، Static Files)

**FrontEnd**
- [ ] پیاده‌سازی Lazy Loading برای صفحات پنل
- [ ] بهینه‌سازی Image Loading (next/image)
- [ ] بهینه‌سازی SEO صفحات عمومی (metadata، OpenGraph)
- [ ] پیاده‌سازی Error Boundary ها
- [ ] تست نهایی فلوهای اصلی (ثبت سفارش، پرداخت، تعمیر)
- [ ] Bug Fix و Polish نهایی UI

---

## پیوست — قوانین کلی توسعه

### استانداردهای API
- پاسخ‌ها همیشه ساختار `{data, message, status}` دارند
- Pagination با `{count, next, previous, results}`
- خطاها با کد HTTP مناسب و `{error, detail, field_errors}`
- تمام endpoint ها نیاز به auth دارند — به جز مسیرهای public

### استانداردهای کد
- Backend: Black + isort + Flake8
- Frontend: ESLint + Prettier + TypeScript strict mode
- Commit messages: Conventional Commits (`feat:`, `fix:`, `refactor:`)

### امنیت
- OTP با انقضا (مثلاً ۵ دقیقه) و محدودیت تعداد تلاش
- JWT Access Token کوتاه‌مدت (مثلاً ۱۵ دقیقه) + Refresh Token بلندمدت
- Rate Limiting روی endpoint های auth
- تمام input ها Validate می‌شوند قبل از پردازش
- فایل‌های آپلودشده (رزومه، تصویر) Validate می‌شوند

---

*آخرین ویرایش: بر اساس نیازمندی‌نامه دکترگیم — نسخه نهایی*