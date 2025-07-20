from django.shortcuts import get_object_or_404, redirect
from django.utils.translation.trans_real import translation
from rest_framework import generics, permissions
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.auth import CustomJWTAuthentication
from accounts.models import MainManager
from accounts.permissions import IsCustomer
from payments.models import Order, Transaction
from home.models import Cart
from payments.serializers import OrderSerializer, TransactionSerializer
from django.core.exceptions import ValidationError
from rest_framework import status


# Product Order
class OrderCreateAPIView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def perform_create(self, serializer):
        try:
            # دریافت سبد خرید کاربر
            cart = Cart.objects.get(user=self.request.user.customer, is_deleted=False)
            if not cart.cart_items.exists():
                raise ValidationError("سبد خرید خالی است.")

            # محاسبه مبلغ کل از آیتم‌های سبد خرید
            total_amount = cart.total_price

            # ایجاد سفارش
            order = serializer.save(
                customer=self.request.user.customer,
                order_type='customer',
                amount=total_amount,
                description=self.request.data.get('description', '')
            )

            # افزودن محصولات از سبد خرید به سفارش
            products = [item.product for item in cart.cart_items.all()]
            order.product.set(products)
            # پاک کردن سبد خرید پس از ثبت سفارش
            cart.cart_items.all().delete()
            order.save()

        except Cart.DoesNotExist:
            raise ValidationError("سبد خرید یافت نشد.")
        except Exception as e:
            raise ValidationError(f"خطا در ثبت سفارش: {str(e)}")


class OrderDetailAPIView(generics.RetrieveAPIView):
    queryset = Order.objects.filter(is_deleted=False)
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return self.queryset.filter(customer=self.request.user.customer)


class RequestPaymentView(GenericAPIView):
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, customer=request.user.customer)
        manager = get_object_or_404(MainManager, id=1)
        transaction = Transaction.objects.create(
            payer=request.user,
            receiver=manager.user,
            order=order,
            amount=order.amount,
            description=order.description or "پرداخت سفارش"
        )
        result = transaction.request_payment()
        return Response(result, status=status.HTTP_200_OK if result["status"] == "success" else status.HTTP_400_BAD_REQUEST)

class ZarinpalCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        status_param = request.GET.get("Status")
        authority = request.GET.get("Authority")

        if status_param != "OK":
            return Response({"status": "error", "message": "پرداخت توسط کاربر لغو شد."})
        transaction = get_object_or_404(Transaction, authority=authority)
        result = transaction.verify_payment()
        return redirect("https://gamedr.ir/customer/transactions")
# Game Order
# Course Order
# Account Order
