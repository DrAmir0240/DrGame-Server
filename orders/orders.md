# Orders App — Endpoints Implementation

## معماری کلی

- تمام view ها از `rest_framework.generics` استفاده می‌کنند
- تمام serializer ها `ModelSerializer` استاندارد هستند
- تمام view ها `@extend_schema` فقط با دو فیلد `tags` و `summary` دارند
- فعلاً فقط `IsAuthenticated` روی همه view ها
- تمام delete ها soft delete هستند
- فیلترینگ با `django-filters`
- هر سفارش endpoint های کاملاً جداگانه دارد

---

## مدل‌های آپدیت شده

### BaseOrderStageAction

فیلد `target_value` از مدل حذف شده — مقدار را کارمند موقع execute می‌فرستد نه مدیر از قبل.

```python
class BaseOrderStageAction(models.Model):

    ACTION_TYPE_CHOICES = (
        ('update_order_field',      'آپدیت فیلد سفارش'),
        ('update_order_item_field', 'آپدیت فیلد آیتم سفارش'),
        ('manual_confirm',          'تایید دستی'),
        ('add_note',                'افزودن یادداشت'),
    )

    title        = models.CharField(max_length=100)
    action_type  = models.CharField(max_length=50, choices=ACTION_TYPE_CHOICES)
    description  = models.TextField(blank=True)
    is_required  = models.BooleanField(default=True)
    order        = models.PositiveIntegerField(default=0)
    target_field = models.CharField(max_length=50, blank=True)
    # target_field معنادار فقط وقتی action_type == update_order_field یا update_order_item_field
    # مقدارهای مجاز برای سونی اکانت:
    #   update_order_field      → 'description'
    #   update_order_item_field → 'sony_account', 'is_done'
    # مقدارهای مجاز برای repair:
    #   update_order_field      → 'description', 'repair_fee', 'final_amount'
    #   update_order_item_field → 'is_done'
    # مقدارهای مجاز برای product:
    #   update_order_field      → 'description'
    #   update_order_item_field → 'is_done'
    is_deleted   = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['order']
```

---

## بخش ۱ — سفارش اکانت سونی

### ۱.۱ مدیریت Category و Stage (مدیر)

#### Serializers

```python
# --- Category ---
class SonyAccountOrderCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SonyAccountOrderCategory
        fields = ['id', 'title', 'type', 'account_capacity', 'rent_time_days']


class SonyAccountOrderCategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SonyAccountOrderCategory
        fields = '__all__'


# --- Stage ---
class SonyAccountOrderStageActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SonyAccountOrderStageAction
        fields = [
            'id', 'title', 'action_type', 'description',
            'is_required', 'order', 'target_field'
        ]

    def validate(self, attrs):
        action_type = attrs.get('action_type')
        target_field = attrs.get('target_field', '')

        if action_type in ('update_order_field', 'update_order_item_field') and not target_field:
            raise serializers.ValidationError(
                {'target_field': 'این فیلد برای این نوع اکشن الزامی است.'}
            )

        VALID_ORDER_FIELDS = {'description'}
        VALID_ITEM_FIELDS = {'sony_account', 'is_done'}

        if action_type == 'update_order_field' and target_field not in VALID_ORDER_FIELDS:
            raise serializers.ValidationError(
                {'target_field': f'مقدار مجاز: {VALID_ORDER_FIELDS}'}
            )

        if action_type == 'update_order_item_field' and target_field not in VALID_ITEM_FIELDS:
            raise serializers.ValidationError(
                {'target_field': f'مقدار مجاز: {VALID_ITEM_FIELDS}'}
            )

        return attrs


class SonyAccountOrderStageListSerializer(serializers.ModelSerializer):
    employee_role_detail = EmployeeRoleListSerializer(source='employee_role', read_only=True)

    class Meta:
        model = SonyAccountOrderStage
        fields = [
            'id', 'title', 'order', 'is_start', 'is_end',
            'employee_role', 'employee_role_detail'
        ]


class SonyAccountOrderStageDetailSerializer(serializers.ModelSerializer):
    actions = SonyAccountOrderStageActionSerializer(many=True, read_only=True)
    employee_role_detail = EmployeeRoleListSerializer(source='employee_role', read_only=True)

    class Meta:
        model = SonyAccountOrderStage
        fields = [
            'id', 'title', 'description', 'order',
            'is_start', 'is_end',
            'employee_role', 'employee_role_detail',
            'actions', 'created_at', 'updated_at'
        ]
```

#### Views

```python
# --- Category ---
@extend_schema(tags=['Orders — Sony Account — Config'], summary='لیست دسته‌بندی‌های اکانت سونی')
class SonyAccountOrderCategoryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SonyAccountOrderCategoryListSerializer
    queryset = SonyAccountOrderCategory.objects.all()


@extend_schema(tags=['Orders — Sony Account — Config'], summary='ایجاد دسته‌بندی')
class SonyAccountOrderCategoryCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SonyAccountOrderCategoryDetailSerializer
    queryset = SonyAccountOrderCategory.objects.all()


@extend_schema(tags=['Orders — Sony Account — Config'], summary='ویرایش دسته‌بندی')
class SonyAccountOrderCategoryUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SonyAccountOrderCategoryDetailSerializer
    queryset = SonyAccountOrderCategory.objects.all()
    http_method_names = ['patch']


@extend_schema(tags=['Orders — Sony Account — Config'], summary='حذف دسته‌بندی')
class SonyAccountOrderCategoryDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SonyAccountOrderCategory.objects.all()

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


# --- Stage ---
@extend_schema(tags=['Orders — Sony Account — Config'], summary='لیست مراحل یک دسته‌بندی')
class SonyAccountOrderStageListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SonyAccountOrderStageListSerializer

    def get_queryset(self):
        return SonyAccountOrderStage.objects.filter(
            category_id=self.kwargs['category_id'],
            is_deleted=False
        ).select_related('employee_role').order_by('order')


@extend_schema(tags=['Orders — Sony Account — Config'], summary='ایجاد مرحله')
class SonyAccountOrderStageCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SonyAccountOrderStageDetailSerializer
    queryset = SonyAccountOrderStage.objects.filter(is_deleted=False)


@extend_schema(tags=['Orders — Sony Account — Config'], summary='جزئیات مرحله')
class SonyAccountOrderStageDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SonyAccountOrderStageDetailSerializer
    queryset = SonyAccountOrderStage.objects.filter(is_deleted=False)


@extend_schema(tags=['Orders — Sony Account — Config'], summary='ویرایش مرحله')
class SonyAccountOrderStageUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SonyAccountOrderStageDetailSerializer
    queryset = SonyAccountOrderStage.objects.filter(is_deleted=False)
    http_method_names = ['patch']


@extend_schema(tags=['Orders — Sony Account — Config'], summary='حذف مرحله')
class SonyAccountOrderStageDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SonyAccountOrderStage.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


# --- Action ---
@extend_schema(tags=['Orders — Sony Account — Config'], summary='ایجاد اکشن برای مرحله')
class SonyAccountOrderStageActionCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SonyAccountOrderStageActionSerializer
    queryset = SonyAccountOrderStageAction.objects.filter(is_deleted=False)


@extend_schema(tags=['Orders — Sony Account — Config'], summary='ویرایش اکشن')
class SonyAccountOrderStageActionUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SonyAccountOrderStageActionSerializer
    queryset = SonyAccountOrderStageAction.objects.filter(is_deleted=False)
    http_method_names = ['patch']


@extend_schema(tags=['Orders — Sony Account — Config'], summary='حذف اکشن')
class SonyAccountOrderStageActionDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SonyAccountOrderStageAction.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])
```

---

### ۱.۲ پنل کارمند — صف کاری

این بخش endpoint هایی است که کارمند روزانه باهاشون کار می‌کند.

#### Serializers

```python
class SonyAccountOrderStageQueueSerializer(serializers.ModelSerializer):
    """
    لیست stage هایی که این کارمند (با رول خودش) بهشون دسترسی داره
    سبک — فقط id و title
    """
    class Meta:
        model = SonyAccountOrderStage
        fields = ['id', 'title', 'order']


class SonyAccountOrderCardSerializer(serializers.ModelSerializer):
    """
    کارت سفارش در لیست — اطلاعات کافی برای نمایش کارتی
    """
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    category_title = serializers.CharField(source='category.title', read_only=True)
    stage_title = serializers.CharField(source='stage.title', read_only=True)
    pending_actions_count = serializers.SerializerMethodField()

    def get_pending_actions_count(self, obj):
        completed_ids = obj.action_logs.values_list('action_id', flat=True)
        return obj.stage.actions.filter(
            is_required=True, is_deleted=False
        ).exclude(id__in=completed_ids).count()

    class Meta:
        model = SonyAccountOrder
        fields = [
            'id', 'customer_name', 'category_title',
            'stage_title', 'source', 'type',
            'amount', 'pending_actions_count', 'created_at'
        ]


class SonyAccountOrderDetailSerializer(serializers.ModelSerializer):
    """
    جزئیات کامل سفارش برای صفحه کار کارمند
    """
    customer_detail = CustomerSerializer(source='customer', read_only=True)
    category_detail = SonyAccountOrderCategoryListSerializer(source='category', read_only=True)
    stage_detail = SonyAccountOrderStageDetailSerializer(source='stage', read_only=True)
    items = SonyAccountOrderItemSerializer(many=True, read_only=True)
    consoles = SonyAccountOrderConsoleSerializer(many=True, read_only=True)
    action_logs = SonyAccountOrderActionLogSerializer(many=True, read_only=True)
    stage_logs = SonyAccountOrderStageLogSerializer(many=True, read_only=True)

    class Meta:
        model = SonyAccountOrder
        fields = [
            'id', 'customer', 'customer_detail',
            'category', 'category_detail',
            'stage', 'stage_detail',
            'source', 'type', 'amount',
            'items', 'consoles',
            'action_logs', 'stage_logs',
            'created_at', 'updated_at'
        ]


class SonyAccountOrderActionSerializer(serializers.ModelSerializer):
    """
    لیست اکشن‌های stage فعلی سفارش + وضعیت انجام شدن
    """
    is_done = serializers.SerializerMethodField()

    def get_is_done(self, obj):
        order_id = self.context.get('order_id')
        if not order_id:
            return False
        return SonyAccountOrderActionLog.objects.filter(
            order_id=order_id,
            action=obj
        ).exists()

    class Meta:
        model = SonyAccountOrderStageAction
        fields = [
            'id', 'title', 'action_type',
            'target_field', 'is_required',
            'order', 'is_done'
        ]


class ExecuteActionSerializer(serializers.Serializer):
    """
    Execute یک اکشن روی سفارش
    value بسته به action_type متفاوته:
      update_order_field + target_field=description  → value: string
      update_order_item_field + target_field=sony_account → value: sony_account_id (int)
      update_order_item_field + target_field=is_done → value: true/false + item_id
      manual_confirm → value: اختیاری
      add_note → value: string
    """
    action_id = serializers.IntegerField()
    value = serializers.JSONField(required=False, allow_null=True)
    item_id = serializers.IntegerField(required=False, allow_null=True)
    note = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        try:
            action = SonyAccountOrderStageAction.objects.get(
                id=attrs['action_id'],
                is_deleted=False
            )
        except SonyAccountOrderStageAction.DoesNotExist:
            raise serializers.ValidationError({'action_id': 'اکشن یافت نشد.'})

        attrs['action'] = action

        if action.action_type in ('update_order_field', 'update_order_item_field'):
            if attrs.get('value') is None:
                raise serializers.ValidationError({'value': 'برای این نوع اکشن value الزامی است.'})

        if action.action_type == 'update_order_item_field':
            if not attrs.get('item_id'):
                raise serializers.ValidationError({'item_id': 'برای آپدیت آیتم، item_id الزامی است.'})

        return attrs


class AdvanceStageSerializer(serializers.Serializer):
    """بررسی می‌کنه همه required action ها انجام شدن بعد stage رو آپدیت می‌کنه"""
    note = serializers.CharField(required=False, allow_blank=True)
```

#### Service — Execute Action

```python
# orders/services/sony_account_order_service.py

from orders.models import (
    SonyAccountOrder, SonyAccountOrderItem,
    SonyAccountOrderActionLog, SonyAccountOrderStageLog,
    SonyAccountOrderStage
)


VALID_ORDER_FIELDS = {'description'}
VALID_ITEM_FIELDS = {'sony_account', 'is_done'}


def execute_sony_account_order_action(order: SonyAccountOrder, validated_data: dict, performed_by) -> dict:
    action = validated_data['action']
    value = validated_data.get('value')
    item_id = validated_data.get('item_id')
    note = validated_data.get('note', '')

    if action.stage != order.stage:
        raise ValueError('این اکشن متعلق به stage فعلی سفارش نیست.')

    if action.action_type == 'update_order_field':
        _update_order_field(order, action.target_field, value)

    elif action.action_type == 'update_order_item_field':
        _update_order_item_field(order, item_id, action.target_field, value)

    elif action.action_type == 'add_note':
        note = str(value) if value else note

    # در همه حالت‌ها لاگ ثبت میشه
    SonyAccountOrderActionLog.objects.create(
        order=order,
        action=action,
        performed_by=performed_by,
        note=note
    )

    return {'status': 'ok', 'action_type': action.action_type}


def _update_order_field(order: SonyAccountOrder, field: str, value):
    if field not in VALID_ORDER_FIELDS:
        raise ValueError(f'فیلد {field} مجاز نیست.')
    setattr(order, field, value)
    order.save(update_fields=[field])


def _update_order_item_field(order: SonyAccountOrder, item_id: int, field: str, value):
    if field not in VALID_ITEM_FIELDS:
        raise ValueError(f'فیلد {field} مجاز نیست.')

    try:
        item = SonyAccountOrderItem.objects.get(id=item_id, sony_account_order=order)
    except SonyAccountOrderItem.DoesNotExist:
        raise ValueError('آیتم یافت نشد.')

    if field == 'sony_account':
        # چک: این اکانت قبلاً assign نشده باشه
        already_assigned = SonyAccountOrderItem.objects.filter(
            sony_account_id=value
        ).exclude(id=item_id).exists()
        if already_assigned:
            raise ValueError('این اکانت قبلاً به سفارش دیگری assign شده.')

    setattr(item, field, value)
    item.save(update_fields=[field])


def advance_sony_account_order_stage(order: SonyAccountOrder, note: str, changed_by) -> dict:
    current_stage = order.stage

    # چک: همه required action ها انجام شدن؟
    completed_ids = set(
        order.action_logs.filter(
            action__stage=current_stage
        ).values_list('action_id', flat=True)
    )
    required_ids = set(
        current_stage.actions.filter(
            is_required=True, is_deleted=False
        ).values_list('id', flat=True)
    )

    missing = required_ids - completed_ids
    if missing:
        raise ValueError('همه اکشن‌های اجباری انجام نشده‌اند.')

    if current_stage.is_end:
        raise ValueError('سفارش در آخرین مرحله است.')

    next_stage = SonyAccountOrderStage.objects.filter(
        category=current_stage.category,
        order=current_stage.order + 1,
        is_deleted=False
    ).first()

    if not next_stage:
        raise ValueError('مرحله بعدی یافت نشد.')

    SonyAccountOrderStageLog.objects.create(
        order=order,
        from_stage=current_stage,
        to_stage=next_stage,
        changed_by=changed_by,
        note=note
    )

    order.stage = next_stage
    order.save(update_fields=['stage'])

    return {
        'status': 'ok',
        'new_stage': {'id': next_stage.id, 'title': next_stage.title}
    }
```

#### Views — پنل کارمند

```python
@extend_schema(tags=['Orders — Sony Account — Worker'], summary='لیست stage های قابل دسترس این کارمند')
class MySonyAccountStagesView(generics.ListAPIView):
    """
    فرانت اول این رو صدا میزنه — لیست stage هایی که رول این کارمند بهشون دسترسی داره
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SonyAccountOrderStageQueueSerializer

    def get_queryset(self):
        employee = self.request.user.employee
        role_ids = employee.roles.values_list('id', flat=True)
        return SonyAccountOrderStage.objects.filter(
            employee_role_id__in=role_ids,
            is_deleted=False
        ).order_by('order')


@extend_schema(tags=['Orders — Sony Account — Worker'], summary='لیست سفارشات یک stage')
class SonyAccountOrderByStageView(generics.ListAPIView):
    """
    فرانت به ازای هر stage_id که از endpoint قبلی گرفته، این رو صدا میزنه
    خروجی: لیست کارتی سفارشات
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SonyAccountOrderCardSerializer

    def get_queryset(self):
        return SonyAccountOrder.objects.filter(
            stage_id=self.kwargs['stage_id'],
            is_deleted=False
        ).select_related(
            'customer', 'category', 'stage'
        ).prefetch_related('action_logs').order_by('-created_at')


@extend_schema(tags=['Orders — Sony Account — Worker'], summary='جزئیات سفارش')
class SonyAccountOrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SonyAccountOrderDetailSerializer
    queryset = SonyAccountOrder.objects.filter(is_deleted=False).select_related(
        'customer', 'category', 'stage'
    ).prefetch_related(
        'items', 'consoles', 'action_logs', 'stage_logs'
    )


@extend_schema(tags=['Orders — Sony Account — Worker'], summary='لیست اکشن‌های stage فعلی سفارش')
class SonyAccountOrderActionsView(generics.ListAPIView):
    """
    اکشن‌های stage فعلی سفارش + وضعیت انجام شدن هر اکشن
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SonyAccountOrderActionSerializer

    def get_queryset(self):
        order = get_object_or_404(SonyAccountOrder, pk=self.kwargs['order_id'], is_deleted=False)
        return order.stage.actions.filter(is_deleted=False)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['order_id'] = self.kwargs['order_id']
        return context


@extend_schema(tags=['Orders — Sony Account — Worker'], summary='اجرای یک اکشن روی سفارش')
class SonyAccountOrderExecuteActionView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ExecuteActionSerializer

    def post(self, request, order_id):
        order = get_object_or_404(SonyAccountOrder, pk=order_id, is_deleted=False)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = execute_sony_account_order_action(
                order=order,
                validated_data=serializer.validated_data,
                performed_by=request.user.employee
            )
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result)


@extend_schema(tags=['Orders — Sony Account — Worker'], summary='انتقال سفارش به مرحله بعدی')
class SonyAccountOrderAdvanceStageView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AdvanceStageSerializer

    def post(self, request, order_id):
        order = get_object_or_404(SonyAccountOrder, pk=order_id, is_deleted=False)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = advance_sony_account_order_stage(
                order=order,
                note=serializer.validated_data.get('note', ''),
                changed_by=request.user.employee
            )
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result)
```

#### URLs — سونی اکانت

```python
# orders/urls/sony_account_urls.py

urlpatterns = [
    # --- Config (مدیر) ---
    path('sony-account/categories/', SonyAccountOrderCategoryListView.as_view()),
    path('sony-account/categories/create/', SonyAccountOrderCategoryCreateView.as_view()),
    path('sony-account/categories/<int:pk>/update/', SonyAccountOrderCategoryUpdateView.as_view()),
    path('sony-account/categories/<int:pk>/delete/', SonyAccountOrderCategoryDeleteView.as_view()),

    path('sony-account/categories/<int:category_id>/stages/', SonyAccountOrderStageListView.as_view()),
    path('sony-account/stages/create/', SonyAccountOrderStageCreateView.as_view()),
    path('sony-account/stages/<int:pk>/', SonyAccountOrderStageDetailView.as_view()),
    path('sony-account/stages/<int:pk>/update/', SonyAccountOrderStageUpdateView.as_view()),
    path('sony-account/stages/<int:pk>/delete/', SonyAccountOrderStageDeleteView.as_view()),

    path('sony-account/stage-actions/create/', SonyAccountOrderStageActionCreateView.as_view()),
    path('sony-account/stage-actions/<int:pk>/update/', SonyAccountOrderStageActionUpdateView.as_view()),
    path('sony-account/stage-actions/<int:pk>/delete/', SonyAccountOrderStageActionDeleteView.as_view()),

    # --- Worker (کارمند) ---
    path('sony-account/my-stages/', MySonyAccountStagesView.as_view()),
    path('sony-account/orders/by-stage/<int:stage_id>/', SonyAccountOrderByStageView.as_view()),
    path('sony-account/orders/<int:pk>/', SonyAccountOrderDetailView.as_view()),
    path('sony-account/orders/<int:order_id>/actions/', SonyAccountOrderActionsView.as_view()),
    path('sony-account/orders/<int:order_id>/execute-action/', SonyAccountOrderExecuteActionView.as_view()),
    path('sony-account/orders/<int:order_id>/advance-stage/', SonyAccountOrderAdvanceStageView.as_view()),
]
```

---

## بخش ۲ — سفارش تعمیر

> ساختار کاملاً مشابه سونی اکانت است. تفاوت‌ها:
> - مدل‌های مرتبط: `RepairOrder`, `RepairOrderDevice`, `RepairOrderStage`, `RepairOrderStageAction`
> - فیلدهای مجاز update روی order: `description`, `repair_fee`, `final_amount`
> - فیلدهای مجاز update روی item (device): `is_done`
> - `update_order_item_field` روی `RepairOrderDevice` اعمال می‌شود نه OrderItem

### VALID_FIELDS برای Repair

```python
# orders/services/repair_order_service.py

VALID_ORDER_FIELDS = {'description', 'repair_fee', 'final_amount'}
VALID_ITEM_FIELDS = {'is_done'}
```

### URLs — تعمیر

```python
# orders/urls/repair_urls.py — همان pattern سونی اکانت با prefix repair
urlpatterns = [
    path('repair/categories/', ...),
    path('repair/categories/create/', ...),
    path('repair/categories/<int:pk>/update/', ...),
    path('repair/categories/<int:pk>/delete/', ...),
    path('repair/categories/<int:category_id>/stages/', ...),
    path('repair/stages/create/', ...),
    path('repair/stages/<int:pk>/', ...),
    path('repair/stages/<int:pk>/update/', ...),
    path('repair/stages/<int:pk>/delete/', ...),
    path('repair/stage-actions/create/', ...),
    path('repair/stage-actions/<int:pk>/update/', ...),
    path('repair/stage-actions/<int:pk>/delete/', ...),
    path('repair/my-stages/', ...),
    path('repair/orders/by-stage/<int:stage_id>/', ...),
    path('repair/orders/<int:pk>/', ...),
    path('repair/orders/<int:order_id>/actions/', ...),
    path('repair/orders/<int:order_id>/execute-action/', ...),
    path('repair/orders/<int:order_id>/advance-stage/', ...),
]
```

---

## بخش ۳ — سفارش محصول

> ساختار کاملاً مشابه سونی اکانت است. تفاوت‌ها:
> - مدل‌های مرتبط: `ProductOrder`, `ProductOrderItem`, `ProductOrderStage`, `ProductOrderStageAction`
> - فیلدهای مجاز update روی order: `description`
> - فیلدهای مجاز update روی item: `is_done`

### VALID_FIELDS برای Product

```python
# orders/services/product_order_service.py

VALID_ORDER_FIELDS = {'description'}
VALID_ITEM_FIELDS = {'is_done'}
```

### URLs — محصول

```python
# orders/urls/product_urls.py — همان pattern با prefix product
urlpatterns = [
    path('product/categories/', ...),
    # ... همان ساختار
    path('product/orders/<int:order_id>/advance-stage/', ...),
]
```

---

## خلاصه جریان فرانت

```
۱. GET /orders/sony-account/my-stages/
   ← لیست stage هایی که این کارمند بهشون دسترسی داره
   ← [{id: 3, title: 'اکانت‌ستتر', order: 2}, ...]

۲. به ازای هر stage:
   GET /orders/sony-account/orders/by-stage/{stage_id}/
   ← لیست کارتی سفارشات آن stage

۳. کارمند روی یک سفارش کلیک می‌کند:
   GET /orders/sony-account/orders/{order_id}/

۴. لیست اکشن‌های stage فعلی:
   GET /orders/sony-account/orders/{order_id}/actions/
   ← [{id: 7, title: 'اختصاص اکانت', action_type: 'update_order_item_field',
       target_field: 'sony_account', is_required: true, is_done: false}, ...]
   فرانت از action_type و target_field می‌فهمه چه کامپوننتی نشون بده

۵. کارمند اکشن را انجام می‌دهد:
   POST /orders/sony-account/orders/{order_id}/execute-action/
   {"action_id": 7, "value": 42, "item_id": 15}

۶. بعد از انجام همه اکشن‌های required:
   POST /orders/sony-account/orders/{order_id}/advance-stage/
   {"note": "انجام شد"}
   ← {"status": "ok", "new_stage": {"id": 4, "title": "تحویل"}}
```

---

## نکات پیاده‌سازی

۱. سرویس‌های هر نوع سفارش کاملاً از هم جدا هستند — فایل جداگانه در `orders/services/`
۲. `execute_action` و `advance_stage` هر دو در `try/except ValueError` پیچیده شده‌اند
۳. هر `ValueError` با `status=400` به فرانت برمی‌گردد
۴. لاگ در هر حالت (موفق یا ناموفق نبودن اکشن) ثبت نمی‌شود — فقط بعد از موفقیت
۵. `advance_stage` قبل از انتقال چک می‌کند که stage فعلی `is_end=False` باشد