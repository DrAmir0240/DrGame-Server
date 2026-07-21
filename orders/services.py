"""
Order workflow services.

هر نوع سفارش سرویس کاملاً جدا دارد اما در همین یک فایل با کامنت از هم جدا شده‌اند.
منطق مشترک: execute_action یک اکشن را روی سفارش اجرا می‌کند و لاگ ثبت می‌کند،
advance_stage بعد از اطمینان از انجام همه اکشن‌های اجباری، سفارش را به مرحله بعد می‌برد.

نکته درباره‌ی مدل‌ها (منبع حقیقت):
- هیچ‌کدام از item model ها فیلد `is_done` ندارند، پس از VALID_ITEM_FIELDS حذف شده.
- برای Repair و Product هیچ فیلد آیتم قابل‌آپدیتی باقی نمی‌ماند (VALID_ITEM_FIELDS خالی).

نکات امنیتی/صحت:
- execute و advance هر دو داخل transaction.atomic اجرا می‌شوند تا نوشتن ناقص + لاگ رخ ندهد.
- قبل از هر عملیات، رول کارمند با employee_role مرحله چک می‌شود.
- اکشن‌های required دوباره اجرا نمی‌شوند (جلوگیری از لاگ تکراری).
"""

from django.db import transaction

from psn.models import SonyAccount
from orders.models import (
    # Sony
    SonyAccountOrder, SonyAccountOrderItem,
    SonyAccountOrderActionLog, SonyAccountOrderStageLog, SonyAccountOrderStage,
    # Repair
    RepairOrder, RepairOrderDevice,
    RepairOrderActionLog, RepairOrderStageLog, RepairOrderStage,
    # Product
    ProductOrder, ProductOrderItem,
    ProductOrderActionLog, ProductOrderStageLog, ProductOrderStage,
)


# ======================================================================
# Generic helpers (shared implementation, called by each order service)
# ======================================================================
def _check_employee_role_for_stage(stage, performed_by):
    """
    اگر مرحله employee_role داشته باشد، کارمند باید همان رول را داشته باشد.
    مرحله بدون employee_role برای همه کارمندها باز است.
    """
    if stage is None:
        raise ValueError('سفارش در هیچ مرحله‌ای نیست.')
    if stage.employee_role_id is None:
        return
    role_ids = performed_by.roles.values_list('id', flat=True)
    if stage.employee_role_id not in role_ids:
        raise ValueError('رول شما برای انجام اکشن در این مرحله مجاز نیست.')


def _check_not_duplicate(action, order, action_log_model, item_id=None):
    """اکشن required نباید دوبار روی یک سفارش اجرا شود."""
    if not action.is_required:
        return
    qs = action_log_model.objects.filter(order=order, action=action)
    if action.action_type == 'update_order_item_field' and item_id:
        qs = qs.filter(item_id=item_id)
    if qs.exists():
        raise ValueError('این اکشن قبلاً انجام شده است.')


def _advance_stage_generic(order, current_stage, note, changed_by,
                           stage_model, stage_log_model):
    """
    چک می‌کند همه اکشن‌های اجباری stage فعلی انجام شده باشند،
    سپس سفارش را به مرحله بعدی همان category منتقل می‌کند و لاگ ثبت می‌کند.
    """
    with transaction.atomic():
        _check_employee_role_for_stage(current_stage, changed_by)

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

        if required_ids - completed_ids:
            raise ValueError('همه اکشن‌های اجباری انجام نشده‌اند.')

        if current_stage.is_end:
            raise ValueError('سفارش در آخرین مرحله است.')

        next_stage = stage_model.objects.filter(
            category=current_stage.category,
            order__gt=current_stage.order,
            is_deleted=False
        ).order_by('order').first()

        if not next_stage:
            raise ValueError('مرحله بعدی یافت نشد.')

        stage_log_model.objects.create(
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


# ======================================================================
# Sony Account order service
# ======================================================================
SONY_VALID_ORDER_FIELDS = {'description'}
SONY_VALID_ITEM_FIELDS = {'sony_account'}


def execute_sony_account_order_action(order: SonyAccountOrder, validated_data: dict, performed_by) -> dict:
    action = validated_data['action']
    value = validated_data.get('value')
    item_id = validated_data.get('item_id')
    note = validated_data.get('note', '')

    with transaction.atomic():
        if action.stage != order.stage:
            raise ValueError('این اکشن متعلق به stage فعلی سفارش نیست.')
        _check_employee_role_for_stage(order.stage, performed_by)
        _check_not_duplicate(action, order, SonyAccountOrderActionLog, item_id=item_id)

        if action.action_type == 'update_order_field':
            _sony_update_order_field(order, action.target_field, value)

        elif action.action_type == 'update_order_item_field':
            _sony_update_order_item_field(order, item_id, action.target_field, value)

        elif action.action_type == 'add_note':
            note = str(value).strip() if value else (note or '').strip()
            if not note:
                raise ValueError('برای ثبت یادداشت، متن یادداشت الزامی است.')

        SonyAccountOrderActionLog.objects.create(
            order=order,
            action=action,
            performed_by=performed_by,
            item_id=item_id,
            note=note
        )

    return {'status': 'ok', 'action_type': action.action_type}


def _sony_update_order_field(order: SonyAccountOrder, field: str, value):
    if field not in SONY_VALID_ORDER_FIELDS:
        raise ValueError(f'فیلد {field} مجاز نیست.')
    setattr(order, field, value)
    order.save(update_fields=[field])


def _sony_update_order_item_field(order: SonyAccountOrder, item_id: int, field: str, value):
    if field not in SONY_VALID_ITEM_FIELDS:
        raise ValueError(f'فیلد {field} مجاز نیست.')

    try:
        item = SonyAccountOrderItem.objects.get(id=item_id, sony_account_order=order)
    except SonyAccountOrderItem.DoesNotExist:
        raise ValueError('آیتم یافت نشد.')

    if field == 'sony_account':
        # چک وجود اکانت سونی
        if not SonyAccount.objects.filter(id=value, is_deleted=False).exists():
            raise ValueError('اکانت سونی یافت نشد یا حذف شده است.')
        # چک assign نشده بودن به سفارش دیگر
        already_assigned = SonyAccountOrderItem.objects.filter(
            sony_account_id=value, is_deleted=False
        ).exclude(id=item_id).exists()
        if already_assigned:
            raise ValueError('این اکانت قبلاً به سفارش دیگری assign شده.')
        item.sony_account_id = value
        item.save(update_fields=['sony_account'])
        return

    setattr(item, field, value)
    item.save(update_fields=[field])


def advance_sony_account_order_stage(order: SonyAccountOrder, note: str, changed_by) -> dict:
    return _advance_stage_generic(
        order, order.stage, note, changed_by,
        SonyAccountOrderStage, SonyAccountOrderStageLog
    )


# ======================================================================
# Repair order service
# ======================================================================
REPAIR_VALID_ORDER_FIELDS = {'description', 'repair_fee', 'final_amount'}
# مدل RepairOrderDevice فیلد is_done ندارد → هیچ فیلد آیتمی قابل آپدیت نیست
REPAIR_VALID_ITEM_FIELDS = set()


def execute_repair_order_action(order: RepairOrder, validated_data: dict, performed_by) -> dict:
    action = validated_data['action']
    value = validated_data.get('value')
    item_id = validated_data.get('item_id')
    note = validated_data.get('note', '')

    with transaction.atomic():
        if action.stage != order.stage:
            raise ValueError('این اکشن متعلق به stage فعلی سفارش نیست.')
        _check_employee_role_for_stage(order.stage, performed_by)
        _check_not_duplicate(action, order, RepairOrderActionLog, item_id=item_id)

        if action.action_type == 'update_order_field':
            _repair_update_order_field(order, action.target_field, value)

        elif action.action_type == 'update_order_item_field':
            _repair_update_order_item_field(order, item_id, action.target_field, value)

        elif action.action_type == 'add_note':
            note = str(value).strip() if value else (note or '').strip()
            if not note:
                raise ValueError('برای ثبت یادداشت، متن یادداشت الزامی است.')

        RepairOrderActionLog.objects.create(
            order=order,
            action=action,
            performed_by=performed_by,
            item_id=item_id,
            note=note
        )

    return {'status': 'ok', 'action_type': action.action_type}


def _repair_update_order_field(order: RepairOrder, field: str, value):
    if field not in REPAIR_VALID_ORDER_FIELDS:
        raise ValueError(f'فیلد {field} مجاز نیست.')
    setattr(order, field, value)
    order.save(update_fields=[field])


def _repair_update_order_item_field(order: RepairOrder, item_id: int, field: str, value):
    if field not in REPAIR_VALID_ITEM_FIELDS:
        raise ValueError(f'فیلد {field} مجاز نیست.')

    try:
        item = RepairOrderDevice.objects.get(id=item_id, repair_order=order)
    except RepairOrderDevice.DoesNotExist:
        raise ValueError('دستگاه یافت نشد.')

    setattr(item, field, value)
    item.save(update_fields=[field])


def advance_repair_order_stage(order: RepairOrder, note: str, changed_by) -> dict:
    return _advance_stage_generic(
        order, order.stage, note, changed_by,
        RepairOrderStage, RepairOrderStageLog
    )


# ======================================================================
# Product order service
# ======================================================================
PRODUCT_VALID_ORDER_FIELDS = {'description'}
# مدل ProductOrderItem فیلد is_done ندارد → هیچ فیلد آیتمی قابل آپدیت نیست
PRODUCT_VALID_ITEM_FIELDS = set()


def execute_product_order_action(order: ProductOrder, validated_data: dict, performed_by) -> dict:
    action = validated_data['action']
    value = validated_data.get('value')
    item_id = validated_data.get('item_id')
    note = validated_data.get('note', '')

    with transaction.atomic():
        if action.stage != order.stage:
            raise ValueError('این اکشن متعلق به stage فعلی سفارش نیست.')
        _check_employee_role_for_stage(order.stage, performed_by)
        _check_not_duplicate(action, order, ProductOrderActionLog, item_id=item_id)

        if action.action_type == 'update_order_field':
            _product_update_order_field(order, action.target_field, value)

        elif action.action_type == 'update_order_item_field':
            _product_update_order_item_field(order, item_id, action.target_field, value)

        elif action.action_type == 'add_note':
            note = str(value).strip() if value else (note or '').strip()
            if not note:
                raise ValueError('برای ثبت یادداشت، متن یادداشت الزامی است.')

        ProductOrderActionLog.objects.create(
            order=order,
            action=action,
            performed_by=performed_by,
            item_id=item_id,
            note=note
        )

    return {'status': 'ok', 'action_type': action.action_type}


def _product_update_order_field(order: ProductOrder, field: str, value):
    if field not in PRODUCT_VALID_ORDER_FIELDS:
        raise ValueError(f'فیلد {field} مجاز نیست.')
    setattr(order, field, value)
    order.save(update_fields=[field])


def _product_update_order_item_field(order: ProductOrder, item_id: int, field: str, value):
    if field not in PRODUCT_VALID_ITEM_FIELDS:
        raise ValueError(f'فیلد {field} مجاز نیست.')

    try:
        item = ProductOrderItem.objects.get(id=item_id, product_order=order)
    except ProductOrderItem.DoesNotExist:
        raise ValueError('آیتم یافت نشد.')

    setattr(item, field, value)
    item.save(update_fields=[field])


def advance_product_order_stage(order: ProductOrder, note: str, changed_by) -> dict:
    return _advance_stage_generic(
        order, order.stage, note, changed_by,
        ProductOrderStage, ProductOrderStageLog
    )