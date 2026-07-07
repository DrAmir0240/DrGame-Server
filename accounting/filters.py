import django_filters

from accounting.models import Invoice, Transaction


class DailyInvoiceFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(field_name='created_at', lookup_expr='date')

    class Meta:
        model = Invoice
        fields = ['date']


class DailyTransactionFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(field_name='created_at', lookup_expr='date')

    class Meta:
        model = Transaction
        fields = ['date']


class InvoiceFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    date_to = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte')
    status = django_filters.CharFilter(field_name='status')
    payment_status = django_filters.CharFilter(field_name='payment_status')
    is_payroll = django_filters.BooleanFilter(field_name='is_payroll')
    category = django_filters.NumberFilter(field_name='category__id')
    account_side = django_filters.NumberFilter(field_name='account_side__id')
    direction = django_filters.CharFilter(field_name='category__direction')
    amount_min = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    amount_max = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')

    class Meta:
        model = Invoice
        fields = [
            'date_from', 'date_to', 'status', 'payment_status',
            'is_payroll', 'category', 'account_side', 'direction',
            'amount_min', 'amount_max',
        ]


class TransactionFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    date_to = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte')
    account_side = django_filters.NumberFilter(field_name='account_side__id')
    bank_account = django_filters.NumberFilter(field_name='bank_account__id')
    invoice = django_filters.NumberFilter(field_name='invoice__id')
    amount_min = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    amount_max = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')

    class Meta:
        model = Transaction
        fields = [
            'date_from', 'date_to', 'account_side', 'bank_account',
            'invoice', 'amount_min', 'amount_max',
        ]


class PayableReceivableFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    date_to = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte')
    account_side = django_filters.NumberFilter(field_name='account_side__id')
    category = django_filters.NumberFilter(field_name='category__id')
    payment_status = django_filters.CharFilter(field_name='payment_status')

    class Meta:
        model = Invoice
        fields = ['date_from', 'date_to', 'account_side', 'category', 'payment_status']
