from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters

from docs.serializers import DocCategorySerializer, DocSubCategorySerializer, DocumentSerializer
from hr.filters import DocumentFilter, DocumentSubCatFilter
from inventory.models import Document, DocSubCategory, DocCategory
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
