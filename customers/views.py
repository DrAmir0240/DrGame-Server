from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.auth import CustomJWTAuthentication
from .models import Customer, BusinessCustomer
from .serializers import (
    CustomerProfileSerializer,
    BusinessCustomerUpgradeSerializer,
    OrderSerializer,
    GameOrderSerializer,
    RepairOrderSerializer,
    TransactionSerializer, BusinessCustomerProfileSerializer, CustomerProfileCreateSerializer, CourseOrderSerializer
)

from payments.models import Order, GameOrder, RepairOrder, Transaction, CourseOrder
from django.db.models import Q


class CustomerProfileCreateAPIView(generics.CreateAPIView):
    serializer_class = CustomerProfileCreateSerializer
    queryset = Customer.objects.select_related('user').filter(is_deleted=False).all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]


class CustomerProfileRetrieveAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def get_object(self):
        try:

            return BusinessCustomer.objects.get(user=self.request.user, is_deleted=False)
        except BusinessCustomer.DoesNotExist:

            return get_object_or_404(Customer, user=self.request.user, is_deleted=False)

    def get_serializer_class(self):
        obj = self.get_object()
        if isinstance(obj, BusinessCustomer):
            return BusinessCustomerProfileSerializer
        return CustomerProfileSerializer


class UpgradeToBusinessCustomerCreateAPIView(generics.CreateAPIView):
    serializer_class = BusinessCustomerUpgradeSerializer
    queryset = BusinessCustomer.objects.select_related('user').all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def create(self, request, *args, **kwargs):
        customer = get_object_or_404(Customer, user=request.user)
        serializer = BusinessCustomerUpgradeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        customer.is_deleted = True
        customer.save()

        return Response(
            {'status': 'success', 'message': 'Upgraded to business customer successfully'},
            status=status.HTTP_201_CREATED
        )


class CustomerOrderListAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        return Order.objects.select_related('product', 'order_type', 'customer').filter(customer=customer,
                                                                                        is_deleted=False)


class CustomerOrderRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        return Order.objects.select_related('product', 'order_type', 'customer').filter(customer=customer,
                                                                                        is_deleted=False)


class CustomerGameOrderListAPIView(generics.ListAPIView):
    serializer_class = GameOrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        return GameOrder.objects.select_related('product', 'order_type', 'customer').filter(customer=customer,
                                                                                            is_deleted=False)


class CustomerGameOrderRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = GameOrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        return GameOrder.objects.select_related('product', 'order_type', 'customer').filter(customer=customer,
                                                                                            is_deleted=False)


class CustomerRepairOrderListAPIView(generics.ListAPIView):
    serializer_class = RepairOrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        return RepairOrder.objects.select_related('product', 'order_type', 'customer').filter(customer=customer,
                                                                                              is_deleted=False)


class CustomerRepairOrderRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = RepairOrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        return RepairOrder.objects.select_related('product', 'order_type', 'customer').filter(customer=customer,
                                                                                              is_deleted=False)


class CustomerCourseOrderListAPIView(generics.ListAPIView):
    serializer_class = CourseOrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        return CourseOrder.objects.select_related('course', 'customer').filter(customer=customer,
                                                                               is_deleted=False).all()


class CustomerCourseOrderRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = CourseOrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        return CourseOrder.objects.select_related('course', 'customer').filter(customer=customer,
                                                                               is_deleted=False).all()


class CustomerTransactionListAPIView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        return Transaction.objects.filter(
            (Q(payer=self.request.user) | Q(receiver=self.request.user)),
            is_deleted=False
        ).select_related('transaction_type', 'game_order', 'repair_order', 'order').distinct()


class CustomerTransactionRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        return Transaction.objects.filter(
            (Q(payer=self.request.user) | Q(receiver=self.request.user)),
            is_deleted=False
        ).select_related('transaction_type', 'game_order', 'repair_order', 'order').distinct()

