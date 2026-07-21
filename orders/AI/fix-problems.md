# Orders App — Fixes & Next Steps

## وضعیت فعلی

- پرمیژن سیستم HR پیاده‌سازی شده و آماده استفاده است
- endpoint های workflow سه نوع سفارش پیاده‌سازی شده
- مشکلات زیر باید به ترتیب اولویت رفع شوند

---

## 🔴 اولویت اول — بحرانی

### ۱. اضافه کردن `IsEmployee` Permission Class

فایل `hr/permissions.py` را باز کن و این کلاس را اضافه کن:

```python
class IsEmployee(BasePermission):
    """
    فقط کاربرانی که Employee دارند مجاز هستند
    از این روی تمام worker endpoint های orders استفاده می‌شود
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'employee') and
            not request.user.employee.is_deleted
        )
```

بعد در `orders/views.py` تمام worker view ها را آپدیت کن:

```python
# این import اضافه کن
from hr.permissions import IsEmployee, employee_permission

# روی تمام worker view ها — my-stages, by-stage, detail, actions, execute, advance
permission_classes = [IsAuthenticated, IsEmployee]

# روی config view ها (مدیر) — categories, stages, stage-actions
permission_classes = [IsAuthenticated, IsEmployee, employee_permission('orders', 'write')]
```

> **توجه:** پرمیژن `orders` باید به `seed_permissions` اضافه شود — ادامه را ببین.

---

### ۲. اضافه کردن پرمیژن `orders` به seed

فایل `hr/management/commands/seed_permissions.py` را باز کن و این موارد را به لیست `PERMISSIONS` اضافه کن:

```python
('orders', 'read',  None),
('orders', 'write', None),
```

بعد اجرا کن:

```bash
python manage.py seed_permissions
```

---

### ۳. اضافه کردن `transaction.atomic()` به execute_action

در `orders/services.py` تابع `execute_*_order_action` برای هر سه نوع سفارش را پیدا کن و کل بدنه را داخل `transaction.atomic()` بذار:

```python
from django.db import transaction

def execute_sony_account_order_action(order, validated_data, performed_by):
    with transaction.atomic():
        action = validated_data['action']
        value = validated_data.get('value')
        item_id = validated_data.get('item_id')
        note = validated_data.get('note', '')

        if action.stage != order.stage:
            raise ValueError('این اکشن متعلق به stage فعلی سفارش نیست.')

        # بقیه منطق...

        SonyAccountOrderActionLog.objects.create(
            order=order,
            action=action,
            performed_by=performed_by,
            note=note
        )
```

همین تغییر را برای `execute_repair_order_action` و `execute_product_order_action` هم اعمال کن.

---

### ۴. چک رول کارمند در execute_action

در `orders/services.py` داخل هر `execute_*_order_action`، قبل از هر منطقی این چک را اضافه کن:

```python
# چک رول کارمند
if order.stage.employee_role:
    employee_role_ids = performed_by.roles.values_list('id', flat=True)
    if order.stage.employee_role_id not in employee_role_ids:
        raise ValueError('رول شما برای انجام اکشن در این مرحله مجاز نیست.')
```

همین چک را در `_advance_stage_generic` یا هر تابع advance مربوطه هم اضافه کن.

---

### ۵. اعتبارسنجی `sony_account_id` در execute

در `orders/services.py` داخل `_sony_update_order_item_field` (یا هر جایی که `sony_account` assign می‌شود):

```python
from psn.models import SonyAccount

if field == 'sony_account':
    # چک وجود اکانت
    if not SonyAccount.objects.filter(id=value, is_deleted=False).exists():
        raise ValueError('اکانت سونی یافت نشد یا حذف شده است.')
    # چک assign نشده بودن به سفارش دیگر
    already_assigned = SonyAccountOrderItem.objects.filter(
        sony_account_id=value
    ).exclude(id=item_id).exists()
    if already_assigned:
        raise ValueError('این اکانت سونی قبلاً به سفارش دیگری اختصاص داده شده.')
```

---

## 🟠 اولویت دوم — مهم

### ۶. جلوگیری از اجرای تکراری اکشن

در `orders/services.py` داخل هر `execute_*_order_action`، بعد از چک رول:

```python
# چک تکراری نبودن — فقط برای اکشن‌های required
if action.is_required:
    already_done = SonyAccountOrderActionLog.objects.filter(
        order=order,
        action=action
    ).exists()
    if already_done:
        raise ValueError('این اکشن قبلاً انجام شده است.')
```

همین را برای Repair و Product هم اعمال کن با مدل لاگ مربوطه.

---

### ۷. validation خالی بودن `add_note`

در `orders/serializers.py` داخل `ExecuteActionSerializer.validate`:

```python
def validate(self, attrs):
    action = attrs.get('action')  # یا از validated_data بگیر

    # اگه action_type == add_note، value نمی‌تونه خالی باشه
    if action and action.action_type == 'add_note':
        value = attrs.get('value')
        if not value or (isinstance(value, str) and not value.strip()):
            raise serializers.ValidationError(
                {'value': 'برای ثبت یادداشت، متن یادداشت الزامی است.'}
            )

    return attrs
```

---

### ۸. اضافه کردن `item_id` به BaseOrderActionLog

در `orders/models.py` کلاس `BaseOrderActionLog` را آپدیت کن:

```python
class BaseOrderActionLog(models.Model):
    performed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    item_id      = models.IntegerField(null=True, blank=True)  # ← اضافه شد
    note         = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
```

بعد migration بگیر:

```bash
python manage.py makemigrations orders
python manage.py migrate
```

و در سرویس موقع ثبت لاگ `item_id` را پاس بده:

```python
SonyAccountOrderActionLog.objects.create(
    order=order,
    action=action,
    performed_by=performed_by,
    item_id=item_id,  # ← اضافه شد
    note=note
)
```

---

## 🟡 اولویت سوم — کیفیت کد

### ۹. اضافه کردن `is_deleted` به Category های ناقص

مدل‌های `SonyAccountOrderCategory` و `ProductOrderCategory` در `orders/models.py` فیلد `is_deleted` ندارند. اضافه کن:

```python
class SonyAccountOrderCategory(models.Model):
    # فیلدهای موجود...
    is_deleted = models.BooleanField(default=False)  # ← اضافه شد
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ProductOrderCategory(models.Model):
    # فیلدهای موجود...
    is_deleted = models.BooleanField(default=False)  # ← اضافه شد
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

بعد queryset های مربوطه در views را آپدیت کن:

```python
# قبل
queryset = SonyAccountOrderCategory.objects.all()

# بعد
queryset = SonyAccountOrderCategory.objects.filter(is_deleted=False)
```

و `perform_destroy` را هم soft delete کن مثل بقیه.

Migration:

```bash
python manage.py makemigrations orders
python manage.py migrate
```

---

### ۱۰. رفع warning های drf-spectacular

در `orders/views.py` روی تمام `DestroyAPIView` ها این serializer را اضافه کن:

```python
from rest_framework.serializers import Serializer

class SonyAccountOrderCategoryDeleteView(generics.DestroyAPIView):
    serializer_class = Serializer  # ← رفع warning
    # ...
```

در `orders/serializers.py` روی method field های `SerializerMethodField` این decorator را اضافه کن:

```python
from drf_spectacular.utils import extend_schema_field

class SonyAccountOrderCardSerializer(serializers.ModelSerializer):

    @extend_schema_field(serializers.IntegerField())
    def get_pending_actions_count(self, obj):
        ...

class SonyAccountOrderActionSerializer(serializers.ModelSerializer):

    @extend_schema_field(serializers.BooleanField())
    def get_is_done(self, obj):
        ...
```

---

### ۱۱. اضافه کردن filter به لیست سفارشات

در `orders/views.py` روی `*OrderByStageView` ها فیلتر اضافه کن:

```python
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

# Filter class
class SonyAccountOrderFilter(django_filters.FilterSet):
    source   = django_filters.ChoiceFilter(choices=SonyAccountOrder.SOURCE_CHOICES)
    type     = django_filters.ChoiceFilter(choices=SonyAccountOrder.TYPE_CHOICES)
    customer = django_filters.NumberFilter(field_name='customer__id')
    date_from = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    date_to   = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte')

    class Meta:
        model = SonyAccountOrder
        fields = ['source', 'type', 'customer', 'date_from', 'date_to']


# View
class SonyAccountOrderByStageView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    serializer_class   = SonyAccountOrderCardSerializer
    filterset_class    = SonyAccountOrderFilter
    filter_backends    = [DjangoFilterBackend, OrderingFilter]
    ordering_fields    = ['created_at', 'amount']
    ordering           = ['-created_at']

    def get_queryset(self):
        return SonyAccountOrder.objects.filter(
            stage_id=self.kwargs['stage_id'],
            is_deleted=False
        ).select_related('customer', 'category', 'stage').prefetch_related('action_logs')
```

همین pattern را برای `RepairOrderByStageView` و `ProductOrderByStageView` هم اعمال کن.

---

## ترتیب اجرا

```
۱. IsEmployee permission class → hr/permissions.py
۲. seed_permissions آپدیت → اجرای manage.py seed_permissions
۳. transaction.atomic در سرویس‌ها
۴. چک رول در execute و advance
۵. اعتبارسنجی sony_account_id
۶. چک تکراری اکشن
۷. validation add_note
۸. item_id به BaseOrderActionLog + migration
۹. is_deleted به Category ها + migration
۱۰. warning های schema
۱۱. filter های لیست
```