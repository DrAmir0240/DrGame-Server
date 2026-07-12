import django_filters
from django.utils import timezone

from accounting.models import Invoice, Transaction


class DateRangeFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    end_date = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte')


class TransactionFilter(DateRangeFilter):
    direction = django_filters.ChoiceFilter(choices=Transaction.DIRECTION_CHOICES)
    bank_account = django_filters.NumberFilter(field_name='bank_account__id')
    account_side = django_filters.NumberFilter(field_name='account_side__id')

    class Meta:
        model = Transaction
        fields = ['direction', 'bank_account', 'account_side', 'start_date', 'end_date']


class DailyTransactionFilter(django_filters.FilterSet):
    """فقط تراکنش‌های امروز — بدون نیاز به date range از کاربر"""
    class Meta:
        model = Transaction
        fields = []

    @property
    def qs(self):
        return super().qs.filter(
            created_at__date=timezone.localdate(),
            is_deleted=False,
        )


class InvoiceFilter(DateRangeFilter):
    status = django_filters.ChoiceFilter(choices=Invoice.STATUS_CHOICES)
    payment_status = django_filters.ChoiceFilter(choices=Invoice.PAYMENT_STATUS_CHOICES)
    account_side = django_filters.NumberFilter(field_name='account_side__id')
    category = django_filters.NumberFilter(field_name='category__id')

    class Meta:
        model = Invoice
        fields = ['status', 'payment_status', 'account_side', 'category', 'start_date', 'end_date']


class DailyInvoiceFilter(django_filters.FilterSet):
    """فقط فاکتورهای امروز"""
    class Meta:
        model = Invoice
        fields = []

    @property
    def qs(self):
        return super().qs.filter(
            created_at__date=timezone.localdate(),
            is_deleted=False,
        )


class IncomeInvoiceFilter(DateRangeFilter):
    """فاکتورهای درآمدی — direction=in"""
    status = django_filters.ChoiceFilter(choices=Invoice.STATUS_CHOICES)
    payment_status = django_filters.ChoiceFilter(choices=Invoice.PAYMENT_STATUS_CHOICES)
    account_side = django_filters.NumberFilter(field_name='account_side__id')

    class Meta:
        model = Invoice
        fields = ['status', 'payment_status', 'account_side', 'start_date', 'end_date']


class ExpenseInvoiceFilter(DateRangeFilter):
    """فاکتورهای هزینه‌ای — direction=out"""
    status = django_filters.ChoiceFilter(choices=Invoice.STATUS_CHOICES)
    payment_status = django_filters.ChoiceFilter(choices=Invoice.PAYMENT_STATUS_CHOICES)
    account_side = django_filters.NumberFilter(field_name='account_side__id')

    class Meta:
        model = Invoice
        fields = ['status', 'payment_status', 'account_side', 'start_date', 'end_date']


class PayrollInvoiceFilter(DateRangeFilter):
    payment_status = django_filters.ChoiceFilter(choices=Invoice.PAYMENT_STATUS_CHOICES)
    account_side = django_filters.NumberFilter(field_name='account_side__id')

    class Meta:
        model = Invoice
        fields = ['payment_status', 'account_side', 'start_date', 'end_date']