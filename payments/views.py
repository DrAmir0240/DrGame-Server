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
from employees.serializers import EmployeeGameOrderSerializer
from payments.models import Order, Transaction, OrderItem, GameOrder, DeliveryMan
from home.models import Cart, GameCart
from payments.serializers import OrderSerializer, TransactionSerializer, GameOrderSerializer, DeliveryManSerializer
from django.core.exceptions import ValidationError
from rest_framework import status

# callback url
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


# Product Order
class OrderCreateAPIView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def perform_create(self, serializer):
        try:
            cart = Cart.objects.get(user=self.request.user.customer, is_deleted=False)
            if not cart.cart_items.exists():
                raise ValidationError("سبد خرید خالی است.")

            total_amount = cart.total_price

            order = serializer.save(
                customer=self.request.user.customer,
                order_type='customer',
                amount=total_amount,
                description=self.request.data.get('description', '')
            )

            for item in cart.cart_items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            cart.cart_items.all().delete()
            cart.delete()

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
        return Response(result,
                        status=status.HTTP_200_OK if result["status"] == "success" else status.HTTP_400_BAD_REQUEST)


# Game Order
class GameOrderCreate(generics.CreateAPIView):
    serializer_class = GameOrderSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def perform_create(self, serializer):
        try:
            customer = self.request.user.customer
            game_cart = GameCart.objects.get(user=customer, is_deleted=False)
            if not game_cart.games.exists():
                raise ValidationError("سبد خرید خالی است.")
            total_amount = game_cart.total_price()

            game_order = serializer.save(
                customer=customer,
                order_type='customer',
                games=game_cart.games.all(),
                amount=total_amount,
                status='waiting',
            )
            game_cart.delete()
            return game_order

        except GameCart.DoesNotExist:
            raise ValidationError("سبد خرید یافت نشد.")
        except Exception as e:
            raise ValidationError(f"خطا در ثبت سفارش: {str(e)}")

class AssignDeliveryToDrGame(APIView):
    def post(self, request, order_id):
        try:
            game_order = GameOrder.objects.get(pk=order_id)
        except GameOrder.DoesNotExist:
            return Response({"error": "سفارش پیدا نشد."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DeliveryManSerializer(data=request.data)
        if serializer.is_valid():
            deliveryman, created = DeliveryMan.objects.get_or_create(
                full_name=serializer.validated_data['full_name'],
                phone_number=serializer.validated_data['phone_number']
            )

            game_order.delivery_to_drgame = deliveryman
            game_order.save()

            return Response({"message": "پیک با موفقیت به سفارش متصل شد."}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Repair order
# Course Order
# Account Order
