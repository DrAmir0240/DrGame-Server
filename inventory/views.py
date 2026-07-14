from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Q, Sum

from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from inventory.filters import ProductFilter, InventoryMovementFilter
from inventory.models import (
    Product,
    ProductCategory,
    ProductEntity,
    ProductImage,
    Supplier, InventoryMovement,
)
from inventory.serializers import (
    ProductCategorySerializer,
    ProductDropdownSerializer,
    ProductEntitySerializer,
    ProductImageSerializer,
    ProductSerializer,
    SupplierSerializer,
    InventoryMovementDropdownSerializer,
    InventoryMovementSerializer,
    InventoryStatsSerializer,
)
from platform_settings.views import SoftDeleteViewMixin


# ---------------------------------------------------------------------------
# Supplier
# ---------------------------------------------------------------------------
@extend_schema(tags=['انبارداری - تامین کننده'], summary='لیست و ساخت')
class SupplierListCreateView(generics.ListCreateAPIView):
    serializer_class = SupplierSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ("type", "is_deleted")
    search_fields = ("name", "phone", "national_id", "tax_id")
    ordering_fields = ("name", "created_at")
    ordering = ("-created_at",)

    def get_queryset(self):
        return Supplier.objects.filter(is_deleted=False)


@extend_schema(tags=['انبارداری - تامین کننده'], summary='جزعیات و ویرایش و حذف')
class SupplierRetrieveUpdateDestroyView(SoftDeleteViewMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SupplierSerializer
    http_method_names = ("get", "patch", "delete")

    def get_queryset(self):
        return Supplier.objects.filter(is_deleted=False)

    def get_object(self):
        try:
            return super().get_object()
        except Supplier.DoesNotExist:
            raise NotFound(detail="تامین‌کننده یافت نشد.")


# ---------------------------------------------------------------------------
# ProductCategory
# ---------------------------------------------------------------------------
@extend_schema(tags=['انبارداری - دسته بندی کالاها'], summary='لیست و ساخت')
class ProductCategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductCategorySerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ("is_deleted",)
    search_fields = ("title", "description")
    ordering_fields = ("title", "created_at")
    ordering = ("-created_at",)

    def get_queryset(self):
        return ProductCategory.objects.filter(is_deleted=False)


@extend_schema(tags=['انبارداری - دسته بندی کالاها'], summary='جزعیات و ویرایش و حذف')
class ProductCategoryRetrieveUpdateDestroyView(SoftDeleteViewMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductCategorySerializer
    http_method_names = ("get", "patch", "delete")

    def get_queryset(self):
        return ProductCategory.objects.filter(is_deleted=False)

    def get_object(self):
        try:
            return super().get_object()
        except ProductCategory.DoesNotExist:
            raise NotFound(detail="دسته‌بندی یافت نشد.")


# ---------------------------------------------------------------------------
# Product
# ---------------------------------------------------------------------------
@extend_schema(tags=['انبارداری - کالاها'], summary='آمار')
class ProductStatsView(generics.GenericAPIView):
    serializer_class = InventoryStatsSerializer

    def get(self, request, *args, **kwargs):
        qs = Product.objects.filter(is_deleted=False)
        aggregated = qs.aggregate(
            total_inventory_value=Coalesce(
                Sum(ExpressionWrapper(F("price") * F("stock"), output_field=DecimalField())),
                0,
                output_field=DecimalField(),
            ),
            green_count=Count("id", filter=Q(stock__gt=F("min_stock"))),
            yellow_count=Count("id", filter=Q(stock__gt=0, stock__lte=F("min_stock"))),
            red_count=Count("id", filter=Q(stock=0)),
        )

        serializer = self.get_serializer(aggregated)
        return Response(serializer.data)


@extend_schema(tags=['انبارداری - کالاها'], summary='جستجوی کالاها')
class ProductSearchView(generics.ListAPIView):
    serializer_class = ProductSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("title", "description", "category__title")

    def get_queryset(self):
        return (
            Product.objects.select_related("category")
            .prefetch_related("supplier")
            .filter(is_deleted=False)
        )


@extend_schema(tags=['انبارداری - کالاها'], summary='لیست با فیلتربندی کامل و ساخت')
class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_class = ProductFilter
    search_fields = ("title", "description")
    ordering_fields = ("title", "price", "stock", "units_sold", "created_at")
    ordering = ("-created_at",)

    def get_queryset(self):
        return (
            Product.objects.select_related("category")
            .prefetch_related("supplier")
            .filter(is_deleted=False)
        )


@extend_schema(tags=['انبارداری - کالاها'], summary='جزعیات و ویرایش و حذف')
class ProductRetrieveUpdateDestroyView(SoftDeleteViewMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    http_method_names = ("get", "patch", "delete")

    def get_queryset(self):
        return (
            Product.objects.select_related("category")
            .prefetch_related("supplier")
            .filter(is_deleted=False)
        )

    def get_object(self):
        try:
            return super().get_object()
        except Product.DoesNotExist:
            raise NotFound(detail="محصول یافت نشد.")


@extend_schema(tags=['انبارداری - کالاها'], summary='چویسس برای دراپ‌داون ساخت کالا')
class ProductDropdownView(generics.GenericAPIView):
    serializer_class = ProductDropdownSerializer

    def get(self, request, *args, **kwargs):
        data = {
            "suppliers": Supplier.objects.filter(is_deleted=False).only("id", "name"),
            "categories": ProductCategory.objects.filter(is_deleted=False).only("id", "title"),
        }
        serializer = self.get_serializer(data)
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# ProductEntity
# ---------------------------------------------------------------------------
@extend_schema(tags=['انبارداری - موجودی کالاها'], summary='لیست بر اساس کالاها و ساخت')
class ProductEntityListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductEntitySerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ("color", "is_deleted")
    search_fields = ("uni_id", "color")
    ordering_fields = ("created_at",)
    ordering = ("-created_at",)

    def get_queryset(self):
        product_id = self.kwargs.get("product_id")
        if not Product.objects.filter(id=product_id, is_deleted=False).exists():
            raise NotFound(detail="محصول یافت نشد.")
        return ProductEntity.objects.filter(product_id=product_id, is_deleted=False)

    def perform_create(self, serializer):
        product_id = self.kwargs.get("product_id")
        try:
            product = Product.objects.get(id=product_id, is_deleted=False)
        except Product.DoesNotExist:
            raise NotFound(detail="محصول یافت نشد.")
        serializer.save(product=product)


@extend_schema(tags=['انبارداری - موجودی کالاها'], summary='جزعیات و ویرایش و حذف')
class ProductEntityRetrieveUpdateDestroyView(SoftDeleteViewMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductEntitySerializer
    http_method_names = ("get", "patch", "delete")

    def get_queryset(self):
        product_id = self.kwargs.get("product_id")
        return ProductEntity.objects.filter(product_id=product_id, is_deleted=False)

    def get_object(self):
        try:
            return super().get_object()
        except ProductEntity.DoesNotExist:
            raise NotFound(detail="موجودیت محصول یافت نشد.")


# ---------------------------------------------------------------------------
# ProductImage
# ---------------------------------------------------------------------------
@extend_schema(tags=['انبارداری - عکس کالاها'], summary='لیست و ساخت')
class ProductImageListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductImageSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("is_deleted",)

    def get_queryset(self):
        product_id = self.kwargs.get("product_id")
        if not Product.objects.filter(id=product_id, is_deleted=False).exists():
            raise NotFound(detail="محصول یافت نشد.")
        return ProductImage.objects.filter(product_id=product_id, is_deleted=False)

    def perform_create(self, serializer):
        product_id = self.kwargs.get("product_id")
        try:
            product = Product.objects.get(id=product_id, is_deleted=False)
        except Product.DoesNotExist:
            raise NotFound(detail="محصول یافت نشد.")
        serializer.save(product=product)


@extend_schema(tags=['انبارداری - عکس کالاها'], summary='جزعیات و ویرایش و حذف')
class ProductImageRetrieveUpdateDestroyView(SoftDeleteViewMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductImageSerializer
    http_method_names = ("get", "patch", "delete")

    def get_queryset(self):
        product_id = self.kwargs.get("product_id")
        return ProductImage.objects.filter(product_id=product_id, is_deleted=False)

    def get_object(self):
        try:
            return super().get_object()
        except ProductImage.DoesNotExist:
            raise NotFound(detail="تصویر محصول یافت نشد.")


# ---------------------------------------------------------------------------
# InventoryMovement
# ---------------------------------------------------------------------------
@extend_schema(tags=['انبارداری - گردش انبار'], summary='لیست و ساخت')
class InventoryMovementListCreateView(generics.ListCreateAPIView):
    serializer_class = InventoryMovementSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = InventoryMovementFilter
    ordering_fields = ("created_at", "direction")
    ordering = ("-created_at",)

    def get_queryset(self):
        return (
            InventoryMovement.objects.select_related("product", "product_entity")
            .filter(is_deleted=False)
        )


@extend_schema(tags=['انبارداری - گردش انبار'], summary='جزعیات و ویرایش و حذف')
class InventoryMovementRetrieveUpdateDestroyView(
    SoftDeleteViewMixin, generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = InventoryMovementSerializer
    http_method_names = ("get", "patch", "delete")

    def get_queryset(self):
        return (
            InventoryMovement.objects.select_related("product", "product_entity")
            .filter(is_deleted=False)
        )

    def get_object(self):
        try:
            return super().get_object()
        except InventoryMovement.DoesNotExist:
            raise NotFound(detail="حرکت انبار یافت نشد.")


@extend_schema(tags=['انبارداری - گردش انبار'], summary='چویسس برای دراپ‌داون')
class InventoryMovementDropdownView(generics.ListAPIView):
    serializer_class = InventoryMovementDropdownSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("direction",)

    def get_queryset(self):
        return (
            InventoryMovement.objects.select_related("product", "product_entity")
            .filter(is_deleted=False)
            .only("id", "direction", "product__title", "product_entity__uni_id")
        )
