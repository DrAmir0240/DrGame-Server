from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.auth import CustomJWTAuthentication
from accounts.permissions import IsMainManager, IsEmployee
from storage.models import SonyAccount
from utils.serializers import Set2FAURISerializer, OTPSerializer
from utils.crypto import encrypt_text, decrypt_text
import urllib.parse
import pyotp, time


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
