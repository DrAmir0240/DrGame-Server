import django_filters

from docs.models import Document, DocSubCategory, RealAssets, RealAssetsSubCategory


class DocumentFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(
        field_name="category__category_id"
    )
    sub_category = django_filters.NumberFilter(
        field_name="category_id"
    )

    class Meta:
        model = Document
        fields = ["category", "sub_category"]


class DocumentSubCatFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(
        field_name="category_id"
    )

    class Meta:
        model = DocSubCategory
        fields = ["category"]


class RealAssetsFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(
        field_name="category__category_id"
    )
    sub_category = django_filters.NumberFilter(
        field_name="category_id"
    )
    min_price = django_filters.NumberFilter(
        field_name="price", lookup_expr="gte"
    )
    max_price = django_filters.NumberFilter(
        field_name="price", lookup_expr="lte"
    )
    employee = django_filters.NumberFilter(
        field_name="employee__id"
    )

    class Meta:
        model = RealAssets
        fields = ["category", "sub_category", "employee", "min_price", "max_price"]


class RealAssetsSubCatFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(
        field_name="category_id"
    )

    class Meta:
        model = RealAssetsSubCategory
        fields = ["category"]
