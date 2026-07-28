import django_filters
from django.db.models import Q

from website.models import BlogPost, BlogPostCategory, Game, StoreProduct, Video


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


# ============================================================
# CUSTOMER SECTION
# ============================================================


class CustomerBlogFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name="category", lookup_expr="exact")
    status = django_filters.CharFilter(field_name="status", lookup_expr="exact")
    author = django_filters.NumberFilter(field_name="author", lookup_expr="exact")

    class Meta:
        model = BlogPost
        fields = ["category", "status", "author"]


# ============================================================
# EMPLOYEE SECTION
# ============================================================


class EmployeeStoreProductFilter(django_filters.FilterSet):
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
    is_deleted = django_filters.BooleanFilter(field_name="is_deleted")

    class Meta:
        model = StoreProduct
        fields = [
            "product__category",
            "min_price",
            "max_price",
            "in_stock",
            "is_deleted",
        ]

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(product__stock__gt=0)
        return queryset


class EmployeeGameFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name="category", lookup_expr="exact")
    min_volume = django_filters.NumberFilter(field_name="volume", lookup_expr="gte")
    max_volume = django_filters.NumberFilter(field_name="volume", lookup_expr="lte")
    is_deleted = django_filters.BooleanFilter(field_name="is_deleted")

    class Meta:
        model = Game
        fields = ["category", "min_volume", "max_volume", "is_deleted"]


class BlogCategoryFilter(django_filters.FilterSet):
    is_deleted = django_filters.BooleanFilter(field_name="is_deleted")

    class Meta:
        model = BlogPostCategory
        fields = ["is_deleted"]


class EmployeeBlogFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name="category", lookup_expr="exact")
    status = django_filters.CharFilter(field_name="status", lookup_expr="exact")
    author = django_filters.NumberFilter(field_name="author", lookup_expr="exact")
    is_deleted = django_filters.BooleanFilter(field_name="is_deleted")

    class Meta:
        model = BlogPost
        fields = ["category", "status", "author", "is_deleted"]


class EmployeeVideoFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status", lookup_expr="exact")

    class Meta:
        model = Video
        fields = ["status"]
