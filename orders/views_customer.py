from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters
from rest_framework.response import Response

from users.permissions import IsCustomer
from orders.models import ProductOrder, SonyAccountOrder, RepairOrder
from orders.serializers_customer import (
    SonyOrderListSerializer,
    SonyOrderDetailSerializer,
    ProductOrderListSerializer,
    ProductOrderDetailSerializer,
    RepairOrderListSerializer,
    RepairOrderDetailSerializer,
)


class CustomerOrderListView(generics.ListAPIView):
    permission_classes = [IsCustomer]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        return None

    def get_queryset(self):
        customer = self.request.user.customer
        order_type = self.request.query_params.get("type")
        results = []
        if not order_type or order_type == "sony":
            sony_qs = (
                SonyAccountOrder.objects.filter(customer=customer, is_deleted=False)
                .select_related("stage", "category")
                .order_by("-created_at")
            )
            results.extend([("sony", o) for o in sony_qs])
        if not order_type or order_type == "product":
            product_qs = (
                ProductOrder.objects.filter(customer=customer, is_deleted=False)
                .select_related("stage")
                .order_by("-created_at")
            )
            results.extend([("product", o) for o in product_qs])
        if not order_type or order_type == "repair":
            repair_qs = (
                RepairOrder.objects.filter(customer=customer, is_deleted=False)
                .select_related("stage", "category")
                .order_by("-created_at")
            )
            results.extend([("repair", o) for o in repair_qs])
        return results

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = []
        for order_type, order in queryset:
            item = {"id": order.id, "type": order_type, "created_at": order.created_at}
            if hasattr(order, "stage") and order.stage:
                item["stage_id"] = order.stage.id
                item["stage_title"] = order.stage.title
            if hasattr(order, "amount"):
                item["amount"] = order.amount
            elif hasattr(order, "total_amount"):
                item["amount"] = order.total_amount
            elif hasattr(order, "final_amount"):
                item["amount"] = order.final_amount
            elif hasattr(order, "repair_fee"):
                item["amount"] = order.repair_fee
            data.append(item)
        return Response(data)


class CustomerSonyOrderListView(generics.ListAPIView):
    permission_classes = [IsCustomer]
    serializer_class = SonyOrderListSerializer

    def get_queryset(self):
        return (
            SonyAccountOrder.objects.filter(
                customer=self.request.user.customer, is_deleted=False
            )
            .select_related("stage", "category")
            .order_by("-created_at")
        )


class CustomerSonyOrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsCustomer]
    serializer_class = SonyOrderDetailSerializer

    def get_queryset(self):
        return (
            SonyAccountOrder.objects.filter(
                customer=self.request.user.customer, is_deleted=False
            )
            .select_related("stage", "category")
            .prefetch_related("stage_logs", "items")
        )


class CustomerProductOrderListView(generics.ListAPIView):
    permission_classes = [IsCustomer]
    serializer_class = ProductOrderListSerializer

    def get_queryset(self):
        return (
            ProductOrder.objects.filter(
                customer=self.request.user.customer, is_deleted=False
            )
            .select_related("stage")
            .order_by("-created_at")
        )


class CustomerProductOrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsCustomer]
    serializer_class = ProductOrderDetailSerializer

    def get_queryset(self):
        return (
            ProductOrder.objects.filter(
                customer=self.request.user.customer, is_deleted=False
            )
            .select_related("stage")
            .prefetch_related("stage_logs", "items")
        )


class CustomerRepairOrderListView(generics.ListAPIView):
    permission_classes = [IsCustomer]
    serializer_class = RepairOrderListSerializer

    def get_queryset(self):
        return (
            RepairOrder.objects.filter(
                customer=self.request.user.customer, is_deleted=False
            )
            .select_related("stage", "category")
            .order_by("-created_at")
        )


class CustomerRepairOrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsCustomer]
    serializer_class = RepairOrderDetailSerializer

    def get_queryset(self):
        return (
            RepairOrder.objects.filter(
                customer=self.request.user.customer, is_deleted=False
            )
            .select_related("stage", "category")
            .prefetch_related("stage_logs", "devices")
        )
