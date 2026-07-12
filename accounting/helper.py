import datetime

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from accounting.models import AccountSide, Invoice, InvoiceCategory, Transaction
from orders.models import (
    RepairOrder, ProductOrder, SonyAccountOrder,
    SonyAccountOrderCategory
)


class InvoiceDropdownHelper:

    @staticmethod
    def get_account_side():
        qs = AccountSide.objects.filter(is_deleted=False).values('id', 'name', 'type')
        return [
            {
                'key': obj['id'],
                'value': obj['name'] or f"{obj['type']} #{obj['id']}"
            }
            for obj in qs
        ]

    @staticmethod
    def get_category():
        qs = InvoiceCategory.objects.filter(is_deleted=False).values('id', 'title')
        return [{'key': obj['id'], 'value': obj['title']} for obj in qs]

    @staticmethod
    def get_status():
        return [{'key': k, 'value': v} for k, v in Invoice.STATUS_CHOICES]

    @staticmethod
    def get_payment_status():
        return [{'key': k, 'value': v} for k, v in Invoice.PAYMENT_STATUS_CHOICES]


WEEKDAY_MAP = {
    5: 'شنبه',
    6: 'یکشنبه',
    0: 'دوشنبه',
    1: 'سه‌شنبه',
    2: 'چهارشنبه',
    3: 'پنجشنبه',
    4: 'جمعه',
}


def get_current_week_range():
    """شنبه تا جمعه — هفته جاری"""
    today = timezone.localdate()
    # weekday(): Mon=0 ... Sat=5, Sun=6
    # شنبه = 5
    days_since_saturday = (today.weekday() - 5) % 7
    saturday = today - datetime.timedelta(days=days_since_saturday)
    friday = saturday + datetime.timedelta(days=6)
    return saturday, friday


def parse_date_range(request):
    start = request.query_params.get('start_date')
    end = request.query_params.get('end_date')
    try:
        start = (
            datetime.date.fromisoformat(start)
            if start
            else timezone.localdate().replace(day=1)  # اول ماه جاری
        )
        end = datetime.date.fromisoformat(end) if end else None
    except ValueError:
        from rest_framework.exceptions import ValidationError
        raise ValidationError({'detail': 'فرمت تاریخ باید YYYY-MM-DD باشه.'})
    return start, end


def apply_date_filter(qs, start, end, field='created_at'):
    if start:
        qs = qs.filter(**{f'{field}__date__gte': start})
    if end:
        qs = qs.filter(**{f'{field}__date__lte': end})
    return qs


def build_weekly_breakdown(qs, amount_field='final_amount'):
    """
    ورودی: queryset که هفته جاری فیلتر شده
    خروجی: لیست روز‌های شنبه تا جمعه با تعداد و مبلغ
    """
    saturday, friday = get_current_week_range()

    daily = (
        qs
        .filter(created_at__date__gte=saturday, created_at__date__lte=friday)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=Count('id'), total=Sum(amount_field))
        .order_by('day')
    )

    daily_map = {row['day']: row for row in daily}

    result = []
    for i in range(7):
        date = saturday + datetime.timedelta(days=i)
        row = daily_map.get(date)
        result.append({
            'date': date.isoformat(),
            'weekday': WEEKDAY_MAP[date.weekday()],
            'count': row['count'] if row else 0,
            'total_amount': row['total'] if row else 0,
        })
    return result


# ── Repair Order Reports ─────────────────────────────────────────────────────

class RepairOrderReportHelper:

    @staticmethod
    def get_summary(start, end):
        qs = apply_date_filter(
            RepairOrder.objects.filter(is_deleted=False),
            start, end
        )
        agg = qs.aggregate(count=Count('id'), total_amount=Sum('final_amount'))
        return {
            'count': agg['count'] or 0,
            'total_amount': agg['total_amount'] or 0,
        }

    @staticmethod
    def get_weekly_breakdown():
        qs = RepairOrder.objects.filter(is_deleted=False)
        return build_weekly_breakdown(qs, amount_field='final_amount')


# ── Product Order Reports ────────────────────────────────────────────────────

class ProductOrderReportHelper:

    @staticmethod
    def get_summary(start, end):
        qs = apply_date_filter(
            ProductOrder.objects.filter(is_deleted=False),
            start, end
        )
        agg = qs.aggregate(count=Count('id'), total_amount=Sum('amount'))
        return {
            'count': agg['count'] or 0,
            'total_amount': agg['total_amount'] or 0,
        }

    @staticmethod
    def get_weekly_breakdown():
        qs = ProductOrder.objects.filter(is_deleted=False)
        return build_weekly_breakdown(qs, amount_field='amount')

    @staticmethod
    def get_by_category(start, end):
        qs = apply_date_filter(
            ProductOrder.objects.filter(is_deleted=False),
            start, end
        )
        rows = (
            qs
            .values('product__category__title')
            .annotate(count=Count('id'), total_amount=Sum('amount'))
            .order_by('-total_amount')
        )
        return [
            {
                'category': row['product__category__title'] or 'نامشخص',
                'count': row['count'],
                'total_amount': row['total_amount'] or 0,
            }
            for row in rows
        ]


# ── Sony Account Order Reports ───────────────────────────────────────────────

class SonyAccountOrderReportHelper:

    @staticmethod
    def get_summary(start, end):
        qs = apply_date_filter(
            SonyAccountOrder.objects.filter(is_deleted=False),
            start, end
        )
        agg = qs.aggregate(count=Count('id'), total_amount=Sum('amount'))
        return {
            'count': agg['count'] or 0,
            'total_amount': agg['total_amount'] or 0,
        }

    @staticmethod
    def get_weekly_breakdown():
        qs = SonyAccountOrder.objects.filter(is_deleted=False)
        return build_weekly_breakdown(qs, amount_field='amount')

    @staticmethod
    def get_by_source(start, end):
        qs = apply_date_filter(
            SonyAccountOrder.objects.filter(is_deleted=False),
            start, end
        )
        rows = (
            qs
            .values('source')
            .annotate(count=Count('id'), total_amount=Sum('amount'))
            .order_by('-count')
        )
        source_map = dict(SonyAccountOrder.SOURCE_CHOICES)
        return [
            {
                'source': row['source'],
                'source_display': source_map.get(row['source'], row['source']),
                'count': row['count'],
                'total_amount': row['total_amount'] or 0,
            }
            for row in rows
        ]

    @staticmethod
    def get_by_type(start, end):
        qs = apply_date_filter(
            SonyAccountOrder.objects.filter(is_deleted=False),
            start, end
        )
        rows = (
            qs
            .values('type')
            .annotate(count=Count('id'), total_amount=Sum('amount'))
            .order_by('-count')
        )
        type_map = dict(SonyAccountOrder.TYPE_CHOICES)
        return [
            {
                'type': row['type'],
                'type_display': type_map.get(row['type'], row['type']),
                'count': row['count'],
                'total_amount': row['total_amount'] or 0,
            }
            for row in rows
        ]

    @staticmethod
    def get_by_category(start, end):
        qs = apply_date_filter(
            SonyAccountOrder.objects.filter(is_deleted=False),
            start, end
        )
        rows = (
            qs
            .values('category__id', 'category__title', 'category__type')
            .annotate(count=Count('id'), total_amount=Sum('amount'))
            .order_by('-count')
        )
        cat_type_map = dict(SonyAccountOrderCategory.TYPE_CHOICES)
        return [
            {
                'category_id': row['category__id'],
                'category_title': row['category__title'] or 'نامشخص',
                'category_type': cat_type_map.get(row['category__type'], ''),
                'count': row['count'],
                'total_amount': row['total_amount'] or 0,
            }
            for row in rows
        ]

    @staticmethod
    def get_by_stage(start, end):
        qs = apply_date_filter(
            SonyAccountOrder.objects.filter(is_deleted=False),
            start, end
        )
        rows = (
            qs
            .values('stage__id', 'stage__title')
            .annotate(count=Count('id'), total_amount=Sum('amount'))
            .order_by('-count')
        )
        return [
            {
                'stage_id': row['stage__id'],
                'stage_title': row['stage__title'] or 'نامشخص',
                'count': row['count'],
                'total_amount': row['total_amount'] or 0,
            }
            for row in rows
        ]


# ── Financial Reports ────────────────────────────────────────────────────────

class FinancialReportHelper:

    @staticmethod
    def _base_transaction_qs(start, end, direction):
        qs = Transaction.objects.filter(is_deleted=False, direction=direction)
        return apply_date_filter(qs, start, end)

    @staticmethod
    def get_income_summary(start, end):
        qs = FinancialReportHelper._base_transaction_qs(start, end, 'in')
        agg = qs.aggregate(count=Count('id'), total_amount=Sum('amount'))
        return {
            'direction': 'in',
            'direction_display': 'دریافت',
            'count': agg['count'] or 0,
            'total_amount': agg['total_amount'] or 0,
        }

    @staticmethod
    def get_expense_summary(start, end):
        qs = FinancialReportHelper._base_transaction_qs(start, end, 'out')
        agg = qs.aggregate(count=Count('id'), total_amount=Sum('amount'))
        return {
            'direction': 'out',
            'direction_display': 'پرداخت',
            'count': agg['count'] or 0,
            'total_amount': agg['total_amount'] or 0,
        }

    @staticmethod
    def get_net_summary(start, end):
        income = FinancialReportHelper.get_income_summary(start, end)
        expense = FinancialReportHelper.get_expense_summary(start, end)
        return {
            'income': income,
            'expense': expense,
            'net': income['total_amount'] - expense['total_amount'],
        }

    @staticmethod
    def get_weekly_breakdown(direction):
        qs = Transaction.objects.filter(is_deleted=False, direction=direction)
        return build_weekly_breakdown(qs, amount_field='amount')
