from django.db import transaction
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
from payments.models import Order, Transaction, OrderItem, GameOrder, DeliveryMan, RepairOrder, CourseOrder, \
    PaymentMethod, GameOrderItem
from home.models import Cart, GameCart
from payments.serializers import OrderSerializer, TransactionSerializer, GameOrderSerializer, DeliveryManSerializer, \
    RepairOrderSerializer, CourseOrderSerializer, GameOrderCreateSerializer
from django.core.exceptions import ValidationError
from rest_framework import status


# orders
class ZarinpalCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        status_param = request.GET.get("Status")
        authority = request.GET.get("Authority")
        transaction = get_object_or_404(Transaction, authority=authority)

        if status_param != "OK":
            if transaction.order:
                transaction.order.delete()
                transaction.payer.customer.balance += transaction.amount
                transaction.payer.customer.save()
            if transaction.game_order:
                transaction.game_order.delete()
                transaction.payer.customer.balance += transaction.amount
                transaction.payer.customer.save()
            if transaction.repair:
                transaction.repair.delete()
                transaction.payer.customer.balance += transaction.amount
                transaction.payer.customer.save()
            if transaction.course_order:
                transaction.course_order.delete()
                transaction.payer.customer.balance += transaction.amount
                transaction.payer.customer.save()
            # اینجا باید موجودی کاربر برگشت بخوره و سفارشش حذف بشه و موحودیش برگرده به حالت اولیه
            return Response({"status": "error", "message": "پرداخت توسط کاربر لغو شد."})

        if transaction.order:
            transaction.order.payment_status = 'paid'
            transaction.order.save()
        if transaction.game_order:
            transaction.game_order.payment_status = 'paid'
            transaction.game_order.save()
        if transaction.repair:
            transaction.repair.status = 'paid'
            transaction.repair.save()
        if transaction.course_order:
            transaction.course_order.customer.has_access_to_course = True
            transaction.course_order.customer.save()
        transaction.payer.customer.balance += transaction.amount
        transaction.payer.customer.save()
        result = transaction.verify_payment()
        print(result)
        return redirect("https://gamedr.ir/customer/transactions")


# ==================== ProductOrder Views ====================
class OrderCreate(generics.CreateAPIView):
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
            order.customer.balance -= order.amount
            order.customer.save()

        except Cart.DoesNotExist:
            raise ValidationError("سبد خرید یافت نشد.")
        except Exception as e:
            raise ValidationError(f"خطا در ثبت سفارش: {str(e)}")


class OrderDetail(generics.RetrieveAPIView):
    queryset = Order.objects.filter(is_deleted=False)
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return self.queryset.filter(customer=self.request.user.customer)


class RequestPaymentForOrder(GenericAPIView):
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, customer=request.user.customer)
        manager = get_object_or_404(MainManager, id=1)
        payment_method = PaymentMethod.objects.filter(is_online=True).first()
        transaction = Transaction.objects.create(
            payer=request.user,
            receiver=manager.user,
            payment_method=payment_method,
            amount=order.amount,
            description=order.description or "پرداخت سفارش"
        )
        order.transaction = transaction
        order.save()

        result = transaction.request_payment()
        return Response(result,
                        status=status.HTTP_200_OK if result["status"] == "success" else status.HTTP_400_BAD_REQUEST)


# ==================== GameOrder Views ====================
class GameOrderCreate(generics.CreateAPIView):
    serializer_class = GameOrderCreateSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data_serializer = self.get_serializer(data=request.data)
        data_serializer.is_valid(raise_exception=True)

        console = data_serializer.validated_data.get('console')
        cart_type = data_serializer.validated_data['type']

        try:
            customer = request.user.customer
            game_cart = GameCart.objects.get(user=customer, is_deleted=False)

            if not game_cart.games.exists():
                raise ValidationError("سبد خرید خالی است.")

            # ست کردن نوع سبد روی cart
            game_cart.type = cart_type
            game_cart.save()

            total_amount = 0
            game_order = GameOrder.objects.create(
                customer=customer,
                order_type='customer',
                amount=0,  # مقدار اولیه، بعداً آپدیت میشه
                status='waiting_for_delivery',
                order_console_type=cart_type,
                console=console
            )

            for game in game_cart.games.all():
                if cart_type == 'online_ps4':
                    if game.game.online_ps4_price:
                        amount = game.game.online_ps4_price
                    else:
                        raise ValidationError(f'{game.game.title} برای {cart_type} موجود نیست ')
                elif cart_type == 'online_ps5':
                    if game.game.online_ps5_price:
                        amount = game.game.online_ps5_price
                    else:
                        raise ValidationError(f'{game.game.title} برای {cart_type} موجود نیست ')
                elif cart_type == 'offline_ps4':
                    if game.game.offline_ps4_price:
                        amount = game.game.offline_ps4_price
                    else:
                        raise ValidationError(f'{game.game.title} برای {cart_type} موجود نیست ')
                elif cart_type == 'offline_ps5':
                    if game.game.offline_ps5_price:
                        amount = game.game.offline_ps5_price
                    else:
                        raise ValidationError(f'{game.game.title} برای {cart_type} موجود نیست ')
                elif cart_type == 'data_ps4':
                    if game.game.data_ps4_price:
                        amount = game.game.data_ps4_price
                    else:
                        raise ValidationError(f'{game.game.title} برای {cart_type} موجود نیست ')
                elif cart_type == 'data_ps5':
                    if game.game.data_ps5_price:
                        amount = game.game.data_ps5_price
                    else:
                        raise ValidationError(f'{game.game.title} برای {cart_type} موجود نیست ')
                elif cart_type == 'xbox':
                    if game.game.xbox_price:
                        amount = game.game.xbox_price
                    else:
                        raise ValidationError(f'{game.game.title} برای {cart_type} موجود نیست ')
                elif cart_type == 'nintendo':
                    if game.game.nintendo_price:
                        amount = game.game.nintendo_price
                    else:
                        raise ValidationError(f'{game.game.title} برای {cart_type} موجود نیست ')
                else:
                    raise ValidationError("نوع سبد خرید نامعتبر است.")

                GameOrderItem.objects.create(
                    game_order=game_order,
                    game=game.game,
                    amount=amount
                )
                total_amount += amount

            game_order.amount = total_amount
            game_order.save()

            game_cart.delete()
            game_order.customer.balance -= game_order.amount
            game_order.customer.save()

            response_serializer = GameOrderSerializer(game_order)
            return Response(response_serializer.data, status=201)

        except GameCart.DoesNotExist:
            raise ValidationError("سبد خرید یافت نشد.")
        except Exception as e:
            raise ValidationError(f"خطا در ثبت سفارش: {str(e)}")


class GameOrderDetail(generics.RetrieveAPIView):
    queryset = GameOrder.objects.filter(is_deleted=False)
    serializer_class = GameOrderSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]
    lookup_field = 'id'

    def get_queryset(self):
        return self.queryset.filter(customer=self.request.user.customer)


class RequestPaymentForGameOrder(generics.GenericAPIView):
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request, game_order_id):
        game_order = get_object_or_404(GameOrder, id=game_order_id)
        manager = get_object_or_404(MainManager, id=1)
        payment_method = PaymentMethod.objects.filter(is_online=True).first()
        transaction = Transaction.objects.create(
            payer=request.user,
            receiver=manager.user,
            payment_method=payment_method,
            amount=game_order.amount,
            description=f'پرداخت شفارش {request.user.customer}'
        )
        game_order.transaction = transaction
        game_order.save()
        result = transaction.request_payment()
        return Response(result,
                        status=status.HTTP_200_OK if result["status"] == "success" else status.HTTP_400_BAD_REQUEST)


class AssignDeliveryToDrGameForGameOrder(APIView):
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

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


class DeliveredGameOrderToCustomer(generics.UpdateAPIView):
    queryset = GameOrder.objects.filter(is_deleted=False, status='done')
    serializer_class = RepairOrderSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]
    lookup_field = 'id'

    def get_queryset(self):
        return self.queryset.filter(self.request.user.customer)

    def perform_update(self, serializer):
        serializer.save(status='delivered_to_customer')
        return Response(serializer.data, status=status.HTTP_200_OK)


# ==================== RepairOrder Views ====================
class RepairOrderCreate(generics.CreateAPIView):
    queryset = RepairOrder.objects.filter(is_deleted=False)
    serializer_class = RepairOrderSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer,
                        console=self.request.data.get('console'),
                        description=self.request.data.get('description'))


class RepairOrderDetail(generics.RetrieveAPIView):
    queryset = RepairOrder.objects.filter(is_deleted=False)
    serializer_class = RepairOrderSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]
    lookup_field = 'id'

    def get_queryset(self):
        return self.queryset.filter(customer=self.request.user.customer)


class AssignDeliveryToDrGameForRepairOrder(APIView):
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request, order_id):
        try:
            repair_order = RepairOrder.objects.get(pk=order_id)
        except GameOrder.DoesNotExist:
            return Response({"error": "سفارش پیدا نشد."}, status=status.HTTP_404_NOT_FOUND)
        serializer = DeliveryManSerializer(data=request.data)
        if serializer.is_valid():
            deliveryman, created = DeliveryMan.objects.get_or_create(
                full_name=serializer.validated_data['full_name'],
                phone_number=serializer.validated_data['phone_number']
            )
            repair_order.delivery_to_drgame = deliveryman
            repair_order.save()
            return Response({"message": "پیک با موفقیت به سفارش متصل شد."}, status=status.HTTP_200_OK)


class RequestPaymentForRepairOrder(generics.GenericAPIView):
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request, repair_order_id):
        repair_order = get_object_or_404(RepairOrder, id=repair_order_id)
        manager = get_object_or_404(MainManager, id=1)
        payment_method = PaymentMethod.objects.filter(is_online=True).first()
        transaction = Transaction.objects.create(
            payer=request.user,
            receiver=manager.user,
            payment_method=payment_method,
            amount=repair_order.amount,
            description=f'پرداخت شفارش تعمیر {request.user.customer}'
        )
        repair_order.transaction = transaction
        repair_order.save()

        result = transaction.request_payment()
        return Response(result,
                        status=status.HTTP_200_OK if result["status"] == "success" else status.HTTP_400_BAD_REQUEST)


class DeliveredRepairOrderToCustomer(generics.UpdateAPIView):
    queryset = RepairOrder.objects.filter(is_deleted=False, status='done')
    serializer_class = GameOrderSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]
    lookup_field = 'id'

    def get_queryset(self):
        return self.queryset.filter(self.request.user.customer)

    def perform_update(self, serializer):
        serializer.save(status='delivered_to_customer')
        return Response(serializer.data, status=status.HTTP_200_OK)


# Course Order
class CourseOrderCreate(generics.CreateAPIView):
    serializer_class = CourseOrderSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def perform_create(self, serializer):
        serializer.save(
            customer=self.request.user.customer,
        )


class CourseOrderDetail(generics.RetrieveAPIView):
    queryset = CourseOrder.objects.filter(is_deleted=False)
    serializer_class = CourseOrderSerializer
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        return self.queryset.filter(customer=self.request.user.customer)


class RequestPaymentForCourseOrder(generics.RetrieveAPIView):
    permission_classes = [IsCustomer]
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request, repair_id):
        course_order = get_object_or_404(RepairOrder, id=repair_id)
        manager = get_object_or_404(MainManager, id=1)
        payment_method = PaymentMethod.objects.filter(is_online=True).first()
        transaction = Transaction.objects.create(
            payer=request.user,
            receiver=manager.user,
            payment_method=payment_method,
            amount=course_order.amount,
            description=f'پرداخت شفارش دوره {request.user.customer}'
        )
        course_order.transaction = transaction
        course_order.save()

        result = transaction.request_payment()
        return Response(result,
                        status=status.HTTP_200_OK if result["status"] == "success" else status.HTTP_400_BAD_REQUEST)

# Account Order
