from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters
from rest_framework.response import Response

from hr.filters import RealAssetsSubCatFilter, RealAssetsFilter, EmployeeProductFilter

from inventory.models import RealAssetsCategory, RealAssetsSubCategory, RealAssets, Product, ProductColor, \
    ProductCategory, ProductCompany
from inventory.serializers import RealAssetsCategorySerializer, RealAssetsSubCategorySerializer, RealAssetsSerializer, \
    EmployeeProductSerializer, EmployeeProductCategorySerializer, EmployeeProductCompanySerializer, \
    EmployeeProductColorSerializer
from users.auth import CustomJWTAuthentication
from users.permissions import IsEmployee, IsMainManager


# Create your views here.

# ==================== Real Assets Views ====================
class RealAssetsCategoryListAPIView(generics.ListAPIView):
    queryset = RealAssetsCategory.objects.filter(is_deleted=False)
    serializer_class = RealAssetsCategorySerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    pagination_class = None


class RealAssetsCategoryCreateAPIView(generics.CreateAPIView):
    serializer_class = RealAssetsCategorySerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class RealAssetsSubCategoryListAPIView(generics.ListAPIView):
    serializer_class = RealAssetsSubCategorySerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RealAssetsSubCatFilter
    pagination_class = None

    def get_queryset(self):
        return RealAssetsSubCategory.objects.filter(is_deleted=False)


class RealAssetsSubCategoryCreateAPIView(generics.CreateAPIView):
    serializer_class = RealAssetsSubCategorySerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class RealAssetsListAPIView(generics.ListAPIView):
    serializer_class = RealAssetsSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RealAssetsFilter
    search_fields = ["title"]
    ordering_fields = ["created_at", "price"]

    def get_queryset(self):
        return (
            RealAssets.objects
            .filter(is_deleted=False)
            .select_related("category", "category__category")
        )


class RealAssetsCreateAPIView(generics.CreateAPIView):
    serializer_class = RealAssetsSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class RealAssetsDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RealAssetsSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    queryset = (
        RealAssets.objects
        .filter(is_deleted=False)
        .select_related("category", "category__category")
    )



# ==================== Product Views ====================
class EmployeePanelProductList(generics.ListAPIView):
    serializer_class = EmployeeProductSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EmployeeProductFilter
    search_fields = [
        "title",
        "category__title",
        "company__title",
        "color__title",
    ]
    ordering_fields = [
        "created_at",
        "price",
        "stock",
        "units_sold",
    ]
    ordering = ["-created_at"]

    def get_queryset(self):
        return (
            Product.objects
            .filter(is_deleted=False)
            .select_related("category", "company", "color")
            .prefetch_related("images")
        )


class EmployeePanelProductDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeProductSerializer
    queryset = Product.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class EmployeePanelAddProduct(generics.CreateAPIView):
    serializer_class = EmployeeProductSerializer
    queryset = Product.objects.filter(is_deleted=False)
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class EmployeePanelProductChoices(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        colors = ProductColor.objects.all()
        categories = ProductCategory.objects.all()
        companies = ProductCompany.objects.all()

        response_data = {
            'colors': EmployeeProductColorSerializer(colors, many=True).data,
            'categories': EmployeeProductCategorySerializer(categories, many=True).data,
            'companies': EmployeeProductCompanySerializer(companies, many=True).data,
        }

        return Response(response_data)


