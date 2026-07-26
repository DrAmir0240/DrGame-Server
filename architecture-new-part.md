# DrGame — Customer Interface: Full Architecture Document
> **هدف این فایل:** راهنمای کامل پیاده‌سازی رابط کاربری مشتری پروژه DrGame برای Open Code.
> تمام مدل‌ها، API endpointها، UX flow و تنظیمات ادمین در این فایل آمده‌اند.

---

## ۱. بررسی وضعیت موجود (Existing Models Audit)

### ۱.۱ مدل‌های کاربری موجود

```python
# users/models.py — وضعیت فعلی
class CustomUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name  = models.CharField(max_length=100, blank=True, null=True)
    phone      = models.CharField(max_length=11, unique=True)
    is_active  = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_staff   = models.BooleanField(default=False)
    USERNAME_FIELD = 'phone'

# crm/models.py — وضعیت فعلی
class Customer(models.Model):
    user         = models.OneToOneField(CustomUser, ...)
    address      = models.TextField(null=True, blank=True)
    postal_code  = models.CharField(max_length=10, ...)
    profile_pic  = models.ImageField(...)
    is_deleted   = models.BooleanField(default=False)

class B2BProfile(models.Model):
    customer        = models.OneToOneField(Customer, ...)
    business_title  = models.CharField(max_length=100)
    debt_amount_max = models.PositiveIntegerField(default=0)
    discount        = models.PositiveIntegerField(default=0)
```

### ۱.۲ مدل‌های موجود که کاربر مشتری از آن‌ها استفاده می‌کند

| مدل | اپ | نقش در Customer Interface |
|---|---|---|
| `ProductOrder` | orders | سفارش کالای فیزیکی |
| `SonyAccountOrder` | orders | سفارش/اجاره اکانت سونی |
| `RepairOrder` | orders | سفارش تعمیر |
| `Product` | inventory | نمایش در فروشگاه |
| `ProductCategory` | inventory | فیلتر فروشگاه |
| `SonyAccountOrderCategory` | orders | نوع اکانت (خرید/اجاره) |
| `Invoice` | accounting | فاکتور قابل مشاهده مشتری |

---

## ۲. مدل‌های جدید مورد نیاز (New Models)

---

### ۲.۱ Wallet

```python
# crm/models.py — اضافه کن
class Wallet(models.Model):
    customer  = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='wallet')
    balance   = models.PositiveBigIntegerField(default=0, help_text="موجودی به تومان")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet of {self.customer} — {self.balance} T"


class WalletTransaction(models.Model):
    TYPE_CHOICES = (
        ('charge_admin',   'شارژ توسط ادمین'),
        ('charge_gateway', 'شارژ آنلاین'),
        ('debit_order',    'کسر بابت سفارش'),
        ('refund',         'برگشت وجه'),
    )
    STATUS_CHOICES = (
        ('pending',   'در انتظار'),
        ('success',   'موفق'),
        ('failed',    'ناموفق'),
        ('cancelled', 'لغو شده'),
    )

    wallet          = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    type            = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount          = models.PositiveBigIntegerField(help_text="مبلغ به تومان")
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description     = models.CharField(max_length=300, blank=True)
    # برای charge_gateway
    gateway_ref     = models.CharField(max_length=100, blank=True, null=True, help_text="شناسه پرداخت درگاه")
    gateway_name    = models.CharField(max_length=50, blank=True, null=True, help_text="مثال: zarinpal")
    # برای debit_order — Generic FK به هر نوع سفارش
    order_content_type = models.ForeignKey(
        'contenttypes.ContentType', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    order_object_id    = models.PositiveIntegerField(null=True, blank=True)
    # performed by
    performed_by    = models.ForeignKey(
        'hr.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, help_text="فقط برای charge_admin"
    )
    balance_before  = models.PositiveBigIntegerField(help_text="موجودی قبل از تراکنش")
    balance_after   = models.PositiveBigIntegerField(help_text="موجودی بعد از تراکنش")
    created_at      = models.DateTimeField(auto_now_add=True)
    is_deleted      = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
```

**نکات پیاده‌سازی:**
- `balance` هیچوقت مستقیم آپدیت نشه — همیشه از طریق `WalletTransaction` و یک `select_for_update()` transaction اتمیک
- `balance_before` و `balance_after` در لحظه ایجاد transaction ثبت بشن (audit trail)
- برای درگاه: در فاز اول Zarinpal یا IDPay. Callback URL باید HTTPS باشه

---

### ۲.۳ Wishlist

```python
# crm/models.py — اضافه کن
class CustomerWishlist(models.Model):
    customer    = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='wishlist_items')
    # Generic FK — محصول فیزیکی یا دسته بازی باری اکانت سونی
    content_type  = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id     = models.PositiveIntegerField()
    created_at    = models.DateTimeField(auto_now_add=True)
    is_deleted    = models.BooleanField(default=False)

    class Meta:
        unique_together = ('customer', 'content_type', 'object_id')
        indexes = [models.Index(fields=['customer', 'content_type'])]
```

**نکات پیاده‌سازی:**
- `content_type` می‌تواند به `inventory.Product` یا `e_commerce.StoreGame` اشاره کند
- در serializer، `object_type` را به صورت string برگردان: `"product"` یا `"store_game"`

---

### ۲.۴ Support Tickets

```python
# support/models.py — اپ جدید بساز
class Ticket(models.Model):
    STATUS_CHOICES = (
        ('open',        'باز'),
        ('in_progress', 'در حال بررسی'),
        ('waiting',     'منتظر پاسخ مشتری'),
        ('closed',      'بسته'),
    )
    PRIORITY_CHOICES = (
        ('low',    'کم'),
        ('medium', 'متوسط'),
        ('high',   'زیاد'),
    )
    CATEGORY_CHOICES = (
        ('order',    'مشکل سفارش'),
        ('payment',  'مشکل پرداخت'),
        ('account',  'مشکل اکانت'),
        ('general',  'عمومی'),
    )

    customer    = models.ForeignKey('crm.Customer', on_delete=models.CASCADE, related_name='tickets')
    assigned_to = models.ForeignKey(
        'hr.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_tickets'
    )
    title       = models.CharField(max_length=200)
    category    = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority    = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    # ارتباط اختیاری با یک سفارش
    order_content_type = models.ForeignKey(
        'contenttypes.ContentType', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    order_object_id = models.PositiveIntegerField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    closed_at   = models.DateTimeField(null=True, blank=True)
    is_deleted  = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']


class TicketMessage(models.Model):
    SENDER_TYPE_CHOICES = (
        ('customer', 'مشتری'),
        ('employee', 'کارمند'),
        ('system',   'سیستم'),
    )

    ticket      = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages')
    sender_type = models.CharField(max_length=10, choices=SENDER_TYPE_CHOICES)
    sender_customer  = models.ForeignKey(
        'crm.Customer', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    sender_employee  = models.ForeignKey(
        'hr.Employee', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    body        = models.TextField()
    attachment  = models.FileField(upload_to='tickets/attachments/', null=True, blank=True)
    is_internal = models.BooleanField(default=False, help_text="یادداشت داخلی — مشتری نمی‌بینه")
    created_at  = models.DateTimeField(auto_now_add=True)
    is_deleted  = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']
```

---

### ۲.۵ Blog (  فاز ۲)

```python
# blog/models.py — اپ جدید، فاز ۲
class BlogPostCategory(models.Model):
    title       = models.CharField(max_length=200)
    description = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    is_deleted  = models.BooleanField(default=False)



class BlogPost(models.Model):
    title       = models.CharField(max_length=200)
    slug        = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    body        = models.TextField()
    cover_image = models.ImageField(upload_to='blog/covers/', null=True, blank=True)
    author      = models.ForeignKey('hr.Employee', on_delete=models.SET_NULL, null=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    is_deleted  = models.BooleanField(default=False)

    class Meta:
        ordering = ['-published_at']


class BlogPostImages(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    image = models.ImageField(uploade_to='blogs/images')
    
```

---

## ۳. ساختار URL و API Endpoints

### ۳.۱ Auth API — `/api/v1/auth/`

```
POST   /users/request-otp/       # درخواست کد OTP
POST   /users/verify-otp/        # تایید کد و دریافت JWT
POST   /users/refresh-token/     # رفرش توکن
POST   /users/logout/            # blacklist کردن توکن
```

**Request — OTP Request:**
```json
{ "phone": "09121234567" }
```
**Response:**
```json
{ "detail": "کد به شماره شما ارسال شد", "expires_in": 120 }
```

**Request — OTP Verify:**
```json
{ "phone": "09121234567", "code": "123456" }
```
**Response:**
```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "is_new_customer": true
}
```

**نکته:** اگر `is_new_customer: true` باشد، فرانت‌اند باید فرم تکمیل پروفایل را نشان دهد.

---

### ۳.۲ Store API — `/api/v1/store/`

```
GET    /e_commerce/store/products/                  # لیست محصولات فیزیکی
GET    /e_commerce/store/products/{id}/             # جزئیات محصول
GET    /e_commerce/store/products/{id}/images/      # تصاویر محصول
GET    /e_commerce/store/categories/                # دسته‌بندی‌ها
GET    /e_commerce/store/games/           # دسته‌بندی‌های اکانت سونی
GET    /e_commerce/store/games-category/ # لیست دسته بندی های بازی
```

**Query Params — Products:**
```
?category=<id>
?search=<str>
?min_price=<int>&max_price=<int>
?in_stock=true
?ordering=price|-price|created_at|-created_at
?page=1&page_size=20
```

**Response — Product List Item:**
```json
{
  "id": 1,
  "title": "DualSense White",
  "main_img": "/media/...",
  "price": 4500000,
  "stock": 12,
  "category_id": 3,
  "category_title": "دسته PS5",
  "is_in_wishlist": false
}
```

**نکته:** فیلد `is_in_wishlist` فقط وقتی کاربر authenticated هست پر می‌شه، وگرنه `null`.

---

### ۳.۳ Customer Profile API — `/api/v1/customer/`

> همه endpoint های این بخش نیاز به `IsAuthenticated` دارند.

```
GET    /api/v1/customer/profile/        # اطلاعات پروفایل
PATCH  /api/v1/customer/profile/        # ویرایش پروفایل
POST   /api/v1/customer/profile/pic/    # آپلود عکس پروفایل
```

**Response — Profile:**
```json
{
  "id": 1,
  "phone": "09121234567",
  "first_name": "امیر",
  "last_name": "رضایی",
  "address": "تهران، ...",
  "postal_code": "1234567890",
  "profile_pic": "/media/profile_pics/...",
  "wallet_balance": 1500000,
  "is_b2b": false
}
```

---

### ۳.۴ Orders API — `/api/v1/customer/orders/`

```
GET    /orders/customer/orders/                      # لیست همه سفارشات
GET    /orders/customer/orders/products/             # سفارشات کالای فیزیکی
GET    /orders/customer/orders/products/{id}/        # جزئیات
POST   /orders/customer/orders/products/             # ثبت سفارش کالا
GET    /orders/customer/orders/sony/                 # سفارشات اکانت سونی
GET    /orders/customer/orders/sony/{id}/            # جزئیات
POST   /orders/customer/orders/sony/                 # ثبت سفارش اکانت
GET    /orders/customer/orders/repair/               # سفارشات تعمیر
GET    /orders/customer/orders/repair/{id}/          # جزئیات
POST   /orders/customer/orders/repair/               # ثبت سفارش تعمیر
```

**Query Params — Orders List:**
```
?type=product|sony|repair
?status=<stage_id>
?from_date=YYYY-MM-DD&to_date=YYYY-MM-DD
?page=1&page_size=10
```

**Response — Sony Order Detail:**
```json
{
  "id": 42,
  "category": { "id": 2, "title": "اجاره آنلاین ۱ ماهه", "type": "rent" },
  "stage": { "id": 5, "title": "در حال پردازش" },
  "source": "telegram",
  "amount": 850000,
  "created_at": "2025-01-15T10:30:00Z",
  "consoles": [{ "serial_number": "PS5-XXX" }],
  "items": [{ "sony_account": "psn_user@example.com" }],
  "stage_logs": [
    { "from_stage": "ثبت سفارش", "to_stage": "در حال پردازش", "created_at": "..." }
  ]
}
```

**نکته مهم:** مشتری فقط stage_logs می‌بینه — اکشن لاگ‌ها و جزئیات internal مثل `employee` مخفی بمانند.

---

### ۳.۵ Wallet API — `/api/v1/customer/wallet/`

```
GET    /wallet/customer/                      # موجودی + آخرین ۵ تراکنش
GET    /wallet/customer/transactions/         # لیست کامل تراکنش‌ها
POST   /wallet/customer/charge/               # شارژ آنلاین (ایجاد payment request)
GET    /accounting//verify/        # callback درگاه پرداخت
```

**Request — Charge:**
```json
{ "amount": 500000 }
```
**Response:**
```json
{ "payment_url": "https://zarinpal.com/pg/StartPay/..." }
```

**Response — Transactions List Item:**
```json
{
  "id": 10,
  "type": "charge_admin",
  "type_display": "شارژ توسط ادمین",
  "amount": 500000,
  "status": "success",
  "description": "شارژ دستی",
  "balance_before": 100000,
  "balance_after": 600000,
  "created_at": "2025-01-10T09:00:00Z"
}
```

---

### ۳.۶ Wishlist API — `/api/v1/customer/wishlist/`

```
GET    /e_commerce/customer/wishlist/              # لیست علاقه‌مندی‌ها
POST   /e_commerce/customer/wishlist/              # اضافه کردن
DELETE /e_commerce/customer/wishlist/{id}/         # حذف
POST   /e_commerce/customer/wishlist/toggle/       # toggle (add if not exists, remove if exists)
```

**Request — Toggle:**
```json
{
  "object_type": "product",
  "object_id": 5
}
```
`object_type` می‌تواند `"product"` یا `"game"` باشد.

**Response — Wishlist Item:**
```json
{
  "id": 1,
  "object_type": "product",
  "object_id": 5,
  "object_detail": {
    "title": "DualSense White",
    "main_img": "/media/...",
    "price": 4500000,
    "in_stock": true
  },
  "created_at": "2025-01-12T08:00:00Z"
}
```

---

### ۳.۷ Support Tickets API — `/api/v1/customer/tickets/`

```
GET    /tickets/customer/list/               # لیست تیکت‌های من
GET    /tickets/customer/{id}/          # جزئیات تیکت + پیام‌ها
POST   /tickets/customer/create/               # ایجاد تیکت جدید
POST   /tickets/customer/{id}/reply/    # ارسال پیام جدید
GET    /tickets/customer/{id}/messages/ # پیام‌های تیکت
```

**Request — Create Ticket:**
```json
{
  "title": "اکانت سونی کار نمی‌کنه",
  "category": "account",
  "body": "بعد از دریافت اکانت نمی‌تونم وارد بشم...",
  "order_type": "sony",
  "order_id": 42
}
```

**Response — Ticket Detail:**
```json
{
  "id": 8,
  "title": "اکانت سونی کار نمی‌کنه",
  "status": "in_progress",
  "status_display": "در حال بررسی",
  "category": "account",
  "priority": "medium",
  "created_at": "2025-01-15T12:00:00Z",
  "messages": [
    {
      "id": 1,
      "sender_type": "customer",
      "body": "بعد از دریافت اکانت نمی‌تونم وارد بشم...",
      "attachment": null,
      "created_at": "2025-01-15T12:00:00Z"
    },
    {
      "id": 2,
      "sender_type": "employee",
      "body": "سلام، بررسی می‌کنیم",
      "is_internal": false,
      "created_at": "2025-01-15T13:00:00Z"
    }
  ]
}
```

**نکته:** پیام‌هایی که `is_internal: true` هستند در response مشتری ظاهر نشوند.

---

### ۳.۸ Blog API — `/blog/`

```
GET    /blog/posts/             # لیست پست‌های منتشر شده
GET    /blog/posts/{slug}/      # جزئیات پست
```

---

## ۴. Permission Classes

```python
# core/permissions.py
from rest_framework.permissions import BasePermission

class IsCustomer(BasePermission):
    """فقط کاربری که Customer profile داره"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'customer') and
            not request.user.customer.is_deleted
        )

class IsCustomerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'customer')
        )

class IsTicketOwner(BasePermission):
    """فقط صاحب تیکت می‌تواند پیام بفرستد"""
    def has_object_permission(self, request, view, obj):
        return obj.customer.user == request.user
```

---

## ۵. Serializer Patterns

### ۵.۱ الگوی کلی

```python
# همه serializer ها از این pattern پیروی کنند:
class ProductListSerializer(serializers.ModelSerializer):
    category_title = serializers.CharField(source='category.title', read_only=True)
    is_in_wishlist = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'main_img', 'price',
            'stock', 'category_id', 'category_title', 'is_in_wishlist'
        ]

    def get_is_in_wishlist(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        try:
            customer = request.user.customer
            ct = ContentType.objects.get_for_model(obj)
            return CustomerWishlist.objects.filter(
                customer=customer, content_type=ct, object_id=obj.id, is_deleted=False
            ).exists()
        except:
            return None
```

### ۵.۲ Nested Serializer برای سفارشات

```python
class SonyOrderDetailSerializer(serializers.ModelSerializer):
    category = SonyOrderCategorySerializer(read_only=True)
    stage = StageMinimalSerializer(read_only=True)
    consoles = ConsoleSerializer(many=True, read_only=True)
    stage_logs = StageLogSerializer(many=True, read_only=True)
    # items را فقط بعد از تحویل نشان بده
    items = serializers.SerializerMethodField()

    def get_items(self, obj):
        if obj.stage and obj.stage.is_end:
            return SonyOrderItemSerializer(
                obj.items.filter(is_deleted=False), many=True
            ).data
        return []
```

---

## ۶. View Patterns

```python
# همه views از generics استفاده کنند — هیچ ViewSet نداریم

class CustomerOrderListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = OrderSummarySerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = CustomerOrderFilter

    def get_queryset(self):
        customer = self.request.user.customer
        order_type = self.request.query_params.get('type')

        if order_type == 'sony':
            return SonyAccountOrder.objects.filter(
                customer=customer, is_deleted=False
            ).select_related('stage', 'category').order_by('-created_at')
        elif order_type == 'product':
            return ProductOrder.objects.filter(
                customer=customer, is_deleted=False
            ).select_related('stage').prefetch_related('items').order_by('-created_at')
        elif order_type == 'repair':
            return RepairOrder.objects.filter(
                customer=customer, is_deleted=False
            ).select_related('stage', 'category').order_by('-created_at')
        # اگر type نداد، همه را با annotate برگردان
        return self._get_all_orders(customer)
```

---

## ۷. Wallet Transaction Logic

```python
# crm/services.py — atomic wallet operations
from django.db import transaction as db_transaction

class WalletService:

    @staticmethod
    @db_transaction.atomic
    def charge(wallet, amount, type_='charge_admin', **kwargs):
        wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)
        balance_before = wallet.balance
        wallet.balance += amount
        wallet.save(update_fields=['balance', 'updated_at'])

        return WalletTransaction.objects.create(
            wallet=wallet,
            type=type_,
            amount=amount,
            status='success',
            balance_before=balance_before,
            balance_after=wallet.balance,
            **kwargs
        )

    @staticmethod
    @db_transaction.atomic
    def debit(wallet, amount, description='', order_ct=None, order_id=None):
        wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)
        if wallet.balance < amount:
            raise ValueError("موجودی کافی نیست")
        balance_before = wallet.balance
        wallet.balance -= amount
        wallet.save(update_fields=['balance', 'updated_at'])

        return WalletTransaction.objects.create(
            wallet=wallet,
            type='debit_order',
            amount=amount,
            status='success',
            balance_before=balance_before,
            balance_after=wallet.balance,
            description=description,
            order_content_type=order_ct,
            order_object_id=order_id,
        )
```

---

## ۸. تنظیمات Admin Panel

### ۸.۱ Customer Management

```python
# crm/admin.py
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display  = ['id', 'get_phone', 'get_full_name', 'get_wallet_balance', 'is_deleted']
    list_filter   = ['is_deleted']
    search_fields = ['user__phone', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [WalletInline, B2BProfileInline]

    def get_phone(self, obj): return obj.user.phone
    def get_full_name(self, obj): return obj.user.full_name()
    def get_wallet_balance(self, obj):
        try: return f"{obj.wallet.balance:,} T"
        except: return "—"
```

### ۸.۲ Wallet Admin (ادمین شارژ دستی)

```python
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['customer', 'balance', 'is_active']
    readonly_fields = ['balance', 'created_at', 'updated_at']
    # شارژ دستی از طریق custom action
    actions = ['charge_wallet_action']

    def charge_wallet_action(self, request, queryset):
        # باز کردن یک intermediate form برای ورود مبلغ
        ...

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display  = ['id', 'wallet', 'type', 'amount', 'status', 'created_at']
    list_filter   = ['type', 'status']
    readonly_fields = [f.name for f in WalletTransaction._meta.fields]  # همه readonly
    # هیچ تراکنشی از ادمین حذف یا ویرایش نمی‌شود
    def has_delete_permission(self, request, obj=None): return False
    def has_change_permission(self, request, obj=None): return False
```

### ۸.۳ Ticket Admin

```python
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display  = ['id', 'title', 'customer', 'category', 'status', 'priority', 'assigned_to', 'created_at']
    list_filter   = ['status', 'priority', 'category']
    search_fields = ['title', 'customer__user__phone']
    list_editable = ['status', 'assigned_to']
    inlines       = [TicketMessageInline]
    readonly_fields = ['created_at', 'updated_at', 'closed_at']

    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data and obj.status == 'closed':
            from django.utils import timezone
            obj.closed_at = timezone.now()
        super().save_model(request, obj, form, change)
```

### ۸.۴ Store Settings در ادمین

```python
# inventory/admin.py — تنظیمات فروشگاه
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ['title', 'price', 'stock', 'min_stock', 'category', 'is_deleted']
    list_filter   = ['category', 'is_deleted']
    list_editable = ['price', 'stock']
    search_fields = ['title']
    inlines       = [ProductImageInline, ProductEntityInline]

@admin.register(SonyAccountOrderCategory)
class SonyAccountOrderCategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'account_capacity', 'rent_time_days', 'is_deleted']
    list_editable = ['is_deleted']
```

---

## ۹. UX Flow ها

### ۹.۱ Auth Flow

```
[صفحه اصلی]
     |
     |-- کاربر شماره وارد می‌کنه
     v
[POST /auth/otp/request/]
     |
     |-- SMS ارسال می‌شه
     v
[صفحه ورود کد OTP]
     |
     |-- [POST /auth/otp/verify/]
     |         |
     |    is_new_customer=true -------> [فرم تکمیل پروفایل]
     |         |                              |
     |    is_new_customer=false         [PATCH /customer/profile/]
     |         |                              |
     v         v-------------------------------
[Dashboard مشتری]
```

### ۹.۲ Store Purchase Flow

```
[فروشگاه] --> [صفحه محصول] --> [انتخاب و سفارش]
                                       |
                              [چک موجودی Wallet]
                                       |
                          کافی --------|-------- ناکافی
                            |                      |
                    [ثبت سفارش]            [صفحه شارژ کیف پول]
                            |                      |
                    [Stage Log نمایش]       [درگاه پرداخت]
                            |                      |
                    [پیگیری در پنل]         [بازگشت به سفارش]
```

### ۹.۳ Ticket Flow

```
[پنل مشتری - تیکت‌ها]
         |
[ایجاد تیکت جدید] -------> [انتخاب دسته‌بندی]
         |                          |
         |               [انتخاب سفارش مرتبط (اختیاری)]
         |                          |
         |                 [توضیح مشکل + ارسال]
         |                          |
         v                          v
[لیست تیکت‌ها] <------- [Ticket ایجاد شد - status: open]
         |
[ادمین پاسخ می‌دهد] ----> [نوتیفیکیشن به مشتری]
         |
[مشتری reply می‌دهد]
         |
[بسته شدن تیکت]
```

---

## ۱۰. Redis Cache Strategy

```python
# cache keys — همه در Redis
CACHE_KEYS = {
    'otp': 'otp:{phone}',                    # TTL: 120s
    'otp_attempts': 'otp_attempts:{phone}',  # TTL: 600s (rate limit)
    'product_list': 'store:products:{hash}', # TTL: 300s
    'category_list': 'store:categories',     # TTL: 3600s
    'customer_profile': 'customer:{id}:profile',  # TTL: 600s — invalidate on update
    'wallet_balance': 'wallet:{customer_id}:balance',  # TTL: 60s
}

# OTP را در Redis نگه دار، نه DB
def send_otp(phone: str) -> None:
    code = generate_6_digit_code()
    cache.set(f"otp:{phone}", hashlib.sha256(code.encode()).hexdigest(), timeout=120)
    cache.set(f"otp_attempts:{phone}", cache.get(f"otp_attempts:{phone}", 0) + 1, timeout=600)
    # SMS send...

def verify_otp(phone: str, code: str) -> bool:
    stored = cache.get(f"otp:{phone}")
    if not stored:
        return False
    if stored != hashlib.sha256(code.encode()).hexdigest():
        return False
    cache.delete(f"otp:{phone}")
    return True
```

---

## ۱۱. فایل‌ساختار اپ‌های جدید

```
project/
├── users/
│   ├── models.py         # CustomUser (موجود)
│   ├── views.py          # OTP views
│   ├── serializers.py
│   ├── urls.py
│   └── services.py       # OTP logic با Redis
├── crm/
│   ├── models.py         # Customer + B2BProfile + Wallet + Wishlist (جدید)
│   ├── admin.py
│   ├── views/
│   │   ├── profile.py
│   │   ├── wallet.py
│   │   └── wishlist.py
│   ├── serializers/
│   │   ├── profile.py
│   │   ├── wallet.py
│   │   └── wishlist.py
│   ├── services.py       # WalletService
│   └── urls.py
├── support/              # اپ جدید
│   ├── models.py         # Ticket + TicketMessage
│   ├── admin.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
├── store/                # اپ جدید — لایه فروشگاه عمومی (public)
│   ├── views.py          # ProductListView, SonyCategoryListView
│   ├── serializers.py
│   └── urls.py
└── blog/                 # فاز ۲
    ├── models.py
    ├── admin.py
    ├── views.py
    └── urls.py
```

---

## ۱۲. نکات مهم پیاده‌سازی

### Security
- همه Customer endpoint ها باید `IsAuthenticated` + `IsCustomer` permission داشته باشند
- هیچ endpoint ای نباید Customer دیگری را expose کند — همیشه `request.user.customer` استفاده شود
- `is_internal` messages در تیکت هرگز به مشتری برگردانده نشود

### Performance
- در `CustomerOrderListView`، از `select_related` و `prefetch_related` استفاده کن
- Product List باید cache شود (Redis, TTL=5min)
- Wallet balance باید cache شود و فقط بعد از هر transaction invalidate شود

### Migrations
- اپ `support` را به `INSTALLED_APPS` اضافه کن
- اپ `store` اگر view-only است، می‌تواند بدون models باشد (از inventory استفاده می‌کند)
- برای `Wallet`، یک `post_save signal` روی `Customer` بنویس تا wallet اتوماتیک ساخته شود:

```python
@receiver(post_save, sender=Customer)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.get_or_create(customer=instance)
```

### extend_schema
- همه views باید `@extend_schema` داشته باشند
- برای views که response شرطی دارند (مثل `items` در sony order)، از `@extend_schema(responses=...)` با توضیح استفاده کن

---

## ۱۳. ترتیب پیاده‌سازی (Implementation Order)

```
Phase 1 — Foundation
  1. OTP Auth (users app) + Redis OTP service
  2. مدل‌های جدید CRM: Wallet + WalletTransaction + CustomerWishlist
  3. migrations + signals

Phase 2 — Store & Profile
  4. store app — public product & sony category endpoints
  5. customer profile endpoints
  6. wishlist endpoints

Phase 3 — Orders & Wallet
  7. customer orders endpoints (read-only + create)
  8. wallet endpoints + WalletService
  9. درگاه پرداخت integration

Phase 4 — Support & Admin
  10. support app — Ticket + TicketMessage models + views
  11. ادمین تیکت
  12. ادمین wallet شارژ دستی

Phase 5 — Blog (فاز ۲)
  13. blog app
```