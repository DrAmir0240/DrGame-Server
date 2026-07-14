import django_filters

from inventory.models import Product, InventoryMovement


class ProductFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains")
    description = django_filters.CharFilter(lookup_expr="icontains")
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    stock_min = django_filters.NumberFilter(field_name="stock", lookup_expr="gte")
    stock_max = django_filters.NumberFilter(field_name="stock", lookup_expr="lte")
    units_sold_min = django_filters.NumberFilter(field_name="units_sold", lookup_expr="gte")
    units_sold_max = django_filters.NumberFilter(field_name="units_sold", lookup_expr="lte")
    created_at_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_at_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")
    category = django_filters.NumberFilter(field_name="category__id")
    category_title = django_filters.CharFilter(field_name="category__title", lookup_expr="icontains")
    supplier = django_filters.NumberFilter(field_name="supplier__id")
    is_deleted = django_filters.BooleanFilter()

    class Meta:
        model = Product
        fields = (
            "title",
            "description",
            "price_min",
            "price_max",
            "stock_min",
            "stock_max",
            "units_sold_min",
            "units_sold_max",
            "created_at_after",
            "created_at_before",
            "category",
            "category_title",
            "supplier",
            "is_deleted",
        )


class InventoryMovementFilter(django_filters.FilterSet):
    direction = django_filters.ChoiceFilter(choices=(("in", "ورودی"), ("out", "خروجی")))
    product = django_filters.NumberFilter(field_name="product__id")
    product_title = django_filters.CharFilter(field_name="product__title", lookup_expr="icontains")
    product_entity = django_filters.NumberFilter(field_name="product_entity__id")
    product_entity_uni_id = django_filters.CharFilter(
        field_name="product_entity__uni_id", lookup_expr="icontains"
    )
    created_at_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_at_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")
    is_deleted = django_filters.BooleanFilter()

    class Meta:
        model = InventoryMovement
        fields = (
            "direction",
            "product",
            "product_title",
            "product_entity",
            "product_entity_uni_id",
            "created_at_after",
            "created_at_before",
            "is_deleted",
        )
