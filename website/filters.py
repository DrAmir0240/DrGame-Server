import django_filters
from django.db.models import Q

from website.models import Game, StoreProduct


class StoreProductFilter(django_filters.FilterSet):
    product__category = django_filters.NumberFilter(
        field_name="product__category", lookup_expr="exact"
    )
    min_price = django_filters.NumberFilter(
        field_name="product__price", lookup_expr="gte"
    )
    max_price = django_filters.NumberFilter(
        field_name="product__price", lookup_expr="lte"
    )
    in_stock = django_filters.BooleanFilter(method="filter_in_stock")

    class Meta:
        model = StoreProduct
        fields = ["product__category", "min_price", "max_price", "in_stock"]

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(product__stock__gt=0)
        return queryset


class GameFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name="category", lookup_expr="exact")
    min_volume = django_filters.NumberFilter(field_name="volume", lookup_expr="gte")
    max_volume = django_filters.NumberFilter(field_name="volume", lookup_expr="lte")

    class Meta:
        model = Game
        fields = ["category", "min_volume", "max_volume"]
