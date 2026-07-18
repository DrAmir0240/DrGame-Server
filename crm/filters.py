import django_filters
from django.db.models import Count, Sum, Q

from crm.models import Customer


class CustomerFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(
        field_name='user__first_name',
        lookup_expr='icontains',
        label='نام'
    )
    last_name = django_filters.CharFilter(
        field_name='user__last_name',
        lookup_expr='icontains',
        label='نام خانوادگی'
    )
    phone = django_filters.CharFilter(
        field_name='user__phone',
        lookup_expr='icontains',
        label='شماره تلفن'
    )

    address = django_filters.CharFilter(
        lookup_expr='icontains',
        label='آدرس'
    )
    postal_code = django_filters.CharFilter(
        lookup_expr='icontains',
        label='کد پستی'
    )

    has_b2b = django_filters.BooleanFilter(
        method='filter_has_b2b',
        label='دارای پروفایل B2B'
    )
    business_title = django_filters.CharFilter(
        field_name='b2b_profile__business_title',
        lookup_expr='icontains',
        label='نام تجاری B2B'
    )

    created_at_from = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='date__gte',
        label='تاریخ ثبت از'
    )
    created_at_to = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='date__lte',
        label='تاریخ ثبت تا'
    )

    class Meta:
        model = Customer
        fields = [
            'first_name', 'last_name', 'phone',
            'address', 'postal_code',
            'has_b2b', 'business_title',
            'created_at_from', 'created_at_to',
        ]

    def filter_has_b2b(self, queryset, value):
        if value:
            return queryset.filter(b2b_profile__is_deleted=False)
        return queryset.exclude(b2b_profile__is_deleted=False)


class CustomerFinanceFilter(CustomerFilter):
    # ── Transaction filters ───────────────────────────────────
    min_transactions_amount = django_filters.NumberFilter(method='filter_min_transactions_amount',
                                                          label='حداقل جمع تراکنش‌ها')
    max_transactions_amount = django_filters.NumberFilter(method='filter_max_transactions_amount',
                                                          label='حداکثر جمع تراکنش‌ها')
    min_transactions_count = django_filters.NumberFilter(method='filter_min_transactions_count',
                                                         label='حداقل تعداد تراکنش‌ها')
    max_transactions_count = django_filters.NumberFilter(method='filter_max_transactions_count',
                                                         label='حداکثر تعداد تراکنش‌ها')

    # ── Invoice filters ───────────────────────────────────────
    min_invoices_count = django_filters.NumberFilter(method='filter_min_invoices_count', label='حداقل تعداد فاکتورها')
    max_invoices_count = django_filters.NumberFilter(method='filter_max_invoices_count', label='حداکثر تعداد فاکتورها')

    # ── Order filters ─────────────────────────────────────────
    min_product_orders = django_filters.NumberFilter(method='filter_min_product_orders', label='حداقل سفارش محصول')
    max_product_orders = django_filters.NumberFilter(method='filter_max_product_orders', label='حداکثر سفارش محصول')
    min_repair_orders = django_filters.NumberFilter(method='filter_min_repair_orders', label='حداقل سفارش تعمیر')
    max_repair_orders = django_filters.NumberFilter(method='filter_max_repair_orders', label='حداکثر سفارش تعمیر')
    min_sony_orders = django_filters.NumberFilter(method='filter_min_sony_orders', label='حداقل سفارش اکانت سونی')
    max_sony_orders = django_filters.NumberFilter(method='filter_max_sony_orders', label='حداکثر سفارش اکانت سونی')

    class Meta:
        model = Customer
        fields = []

    def _get_annotated_qs(self, queryset):
        """
        یه بار annotate میکنه و روی همون queryset کار میکنه
        تا چندبار annotate تکراری نزنیم
        """
        if not hasattr(self, '_annotated'):
            self._annotated = queryset.annotate(
                total_transactions_amount=Sum(
                    'account_side__transactions__amount',
                    filter=Q(
                        account_side__transactions__is_deleted=False,
                        account_side__transactions__direction='in',
                        account_side__content_type__model='customer',
                    )
                ),
                total_transactions_count=Count(
                    'account_side__transactions',
                    filter=Q(
                        account_side__transactions__is_deleted=False,
                        account_side__content_type__model='customer',
                    )
                ),
                total_invoices_count=Count(
                    'product_orders__invoice',
                    filter=Q(product_orders__is_deleted=False, product_orders__invoice__isnull=False),
                ) + Count(
                    'repair_orders__invoice',
                    filter=Q(repair_orders__is_deleted=False, repair_orders__invoice__isnull=False),
                ) + Count(
                    'sony_account_orders__invoice',
                    filter=Q(sony_account_orders__is_deleted=False, sony_account_orders__invoice__isnull=False),
                ),
                total_product_orders=Count(
                    'product_orders',
                    filter=Q(product_orders__is_deleted=False)
                ),
                total_repair_orders=Count(
                    'repair_orders',
                    filter=Q(repair_orders__is_deleted=False)
                ),
                total_sony_orders=Count(
                    'sony_account_orders',
                    filter=Q(sony_account_orders__is_deleted=False)
                ),
            )
        return self._annotated

    def filter_min_transactions_amount(self, queryset, name, value):
        return queryset.filter(total_transactions_amount__gte=value)

    def filter_max_transactions_amount(self, queryset, name, value):
        return queryset.filter(total_transactions_amount__lte=value)

    def filter_min_transactions_count(self, queryset, name, value):
        return queryset.filter(total_transactions_count__gte=value)

    def filter_max_transactions_count(self, queryset, name, value):
        return queryset.filter(total_transactions_count__lte=value)

    def filter_min_invoices_count(self, queryset, name, value):
        return queryset.filter(total_invoices_count__gte=value)

    def filter_max_invoices_count(self, queryset, name, value):
        return queryset.filter(total_invoices_count__lte=value)

    def filter_min_product_orders(self, queryset, name, value):
        return queryset.filter(total_product_orders__gte=value)

    def filter_max_product_orders(self, queryset, name, value):
        return queryset.filter(total_product_orders__lte=value)

    def filter_min_repair_orders(self, queryset, name, value):
        return queryset.filter(total_repair_orders__gte=value)

    def filter_max_repair_orders(self, queryset, name, value):
        return queryset.filter(total_repair_orders__lte=value)

    def filter_min_sony_orders(self, queryset, name, value):
        return queryset.filter(total_sony_orders__gte=value)

    def filter_max_sony_orders(self, queryset, name, value):
        return queryset.filter(total_sony_orders__lte=value)
