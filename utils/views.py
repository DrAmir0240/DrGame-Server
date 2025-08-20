from django.db.models import Count, Q
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, generics

from accounts.auth import CustomJWTAuthentication
from accounts.permissions import IsMainManager, IsEmployee
from payments.models import GameOrder
from utils.serializers import SonyAccountMatchedSerializer, GameOrderMatchedSerializer, SonyAccountAddFromFileSerializer
from storage.models import SonyAccount
from utils.serializers import Set2FAURISerializer, OTPSerializer, SonyAccountSerializer
from utils.crypto import encrypt_text, decrypt_text
import urllib.parse
import pyotp, time

from utils.services import fetch_account_with_games, build_account_message
from utils.telegram import send_telegram_message, TelegramError


class Set2FASecretView(APIView):
    """
    ثبت secret ای که از سونی گرفتیم و فعال کردن 2FA
    """
    permission_classes = [IsMainManager | IsEmployee]
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request, pk):
        serializer = Set2FAURISerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            account = SonyAccount.objects.get(pk=pk)
        except SonyAccount.DoesNotExist:
            return Response({"detail": "SonyAccount not found"}, status=status.HTTP_404_NOT_FOUND)

        uri = serializer.validated_data['uri']
        # استخراج secret از URI
        parsed = urllib.parse.urlparse(uri)
        params = urllib.parse.parse_qs(parsed.query)
        secret = params.get('secret')
        if not secret:
            return Response({"detail": "Secret not found in URI"}, status=status.HTTP_400_BAD_REQUEST)

        secret = secret[0]  # فقط رشته base32

        account.two_step_secret = encrypt_text(secret)
        account.two_step_enabled = True
        account.save(update_fields=['two_step_secret', 'two_step_enabled'])

        return Response({"detail": "2FA enabled successfully"}, status=status.HTTP_200_OK)


class GetOTPView(APIView):
    """
    دریافت کد OTP لحظه‌ای حساب
    """
    permission_classes = [IsMainManager | IsEmployee]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, pk):
        try:
            account = SonyAccount.objects.get(pk=pk)
        except SonyAccount.DoesNotExist:
            return Response({"detail": "SonyAccount not found"}, status=status.HTTP_404_NOT_FOUND)

        if not account.two_step_secret:
            return Response({"detail": "2FA is not enabled for this account"}, status=status.HTTP_400_BAD_REQUEST)

        # رمزگشایی secret
        secret = decrypt_text(account.two_step_secret)
        totp = pyotp.TOTP(secret)
        otp_data = {
            "code": totp.now(),
            "remaining": totp.interval - (int(time.time()) % totp.interval)
        }

        serializer = OTPSerializer(data=otp_data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class SonyAccountViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet نمونه برای SonyAccount.
    - list/retrieve به صورت پیش‌فرض
    - اکشن سفارشی: POST /sony-accounts/{id}/send-to-telegram/
    """
    queryset = SonyAccount.objects.filter(is_deleted=False)
    serializer_class = SonyAccountSerializer  # اگر نداری، موقت یک Serializer مینیمال بنویس
    permission_classes = [IsEmployee | IsMainManager]  # این را با پرمیشن‌های خودت (مثلاً IsEmployee) جایگزین کن

    @action(detail=True, methods=["post"], url_path="send-to-telegram")
    def send_to_telegram(self, request, pk=None):
        """
        اکانت را بارگذاری → پیام را بساز → به تلگرام بفرست.
        بدنهٔ درخواست نمی‌خواهد چیزی بفرستد.
        """
        # 1) کشیدن اکانت
        try:
            account = fetch_account_with_games(pk)
        except SonyAccount.DoesNotExist:
            return Response({"detail": "اکانت پیدا نشد."}, status=status.HTTP_404_NOT_FOUND)

        # 2) ساخت پیام
        message = build_account_message(account)

        # 3) ارسال به تلگرام
        try:
            resp = send_telegram_message(message)
        except TelegramError as e:
            return Response({"detail": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        # 4) پاسخ موفق
        return Response(
            {
                "detail": "پیام با موفقیت ارسال شد.",
                "telegram_response": resp,  # شامل message_id و ...
            },
            status=status.HTTP_200_OK,
        )


class SonyAccountByGameOrderView(generics.ListAPIView):
    serializer_class = SonyAccountMatchedSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        order_id = self.kwargs['order_id']

        try:
            order = GameOrder.objects.get(id=order_id, is_deleted=False)
        except GameOrder.DoesNotExist:
            return SonyAccount.objects.none()

        # فقط ID بازی‌ها رو بگیر
        selected_games = order.games.values_list('game', flat=True)

        queryset = SonyAccount.objects.filter(
            is_deleted=False,
            account_games__game__in=selected_games
        ).annotate(
            matching_games_count=Count('games')
        ).order_by('-matching_games_count')

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class GameOrdersBySonyAccountView(generics.ListAPIView):
    serializer_class = GameOrderMatchedSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        sony_account_id = self.kwargs['sony_account_id']
        try:
            sony_account = SonyAccount.objects.get(id=sony_account_id, is_deleted=False)
        except SonyAccount.DoesNotExist:
            return GameOrder.objects.none()

        selected_games = sony_account.games.all()

        queryset = GameOrder.objects.filter(
            is_deleted=False,
            games__game__in=selected_games  # 👈 اصلاح شد
        ).annotate(
            matching_games_count=Count(
                'games',
                filter=Q(games__game__in=selected_games),
                distinct=True
            )
        ).order_by('-matching_games_count')

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SonyAccountAdd(generics.CreateAPIView):
    queryset = SonyAccount.objects.all()
    serializer_class = SonyAccountSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]


class SonyAccountAddFromFile(generics.CreateAPIView):
    serializer_class = SonyAccountAddFromFileSerializer
