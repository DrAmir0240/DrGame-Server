from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters

from docs.serializers import DocCategorySerializer, DocSubCategorySerializer, DocumentSerializer, \
    RealAssetsCategorySerializer, RealAssetsSubCategorySerializer, RealAssetsSerializer
from docs.filters import DocumentFilter, DocumentSubCatFilter, RealAssetsSubCatFilter, RealAssetsFilter
from docs.models import Document, DocSubCategory, DocCategory, RealAssetsCategory, RealAssetsSubCategory, RealAssets
from users.auth import CustomJWTAuthentication
from users.permissions import IsMainManager, IsEmployee


# Create your views here.
# ==================== Docs Views ====================
class DocCategoryListAPIView(generics.ListAPIView):
    queryset = DocCategory.objects.filter(is_deleted=False)
    serializer_class = DocCategorySerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    pagination_class = None


class DocCategoryCreateAPIView(generics.CreateAPIView):
    serializer_class = DocCategorySerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class DocSubCategoryListAPIView(generics.ListAPIView):
    serializer_class = DocSubCategorySerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DocumentSubCatFilter
    pagination_class = None

    def get_queryset(self):
        return DocSubCategory.objects.filter(is_deleted=False)


class DocSubCategoryCreateAPIView(generics.CreateAPIView):
    serializer_class = DocSubCategorySerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class DocumentListAPIView(generics.ListAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DocumentFilter
    search_fields = ["title"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        return (
            Document.objects
            .filter(is_deleted=False)
            .select_related("category", "category__category")
        )


class DocumentCreateAPIView(generics.CreateAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class DocumentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    queryset = (
        Document.objects
        .filter(is_deleted=False)
        .select_related("category", "category__category")
    )


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
