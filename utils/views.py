from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.auth import CustomJWTAuthentication
from accounts.permissions import IsMainManager, IsEmployee
from storage.models import SonyAccount
from .serializers import Set2FASecretSerializer, OTPSerializer


class Set2FASecretView(APIView):
    """
    ثبت secret ای که از سونی گرفتیم و فعال کردن 2FA
    """
    permission_classes = [IsMainManager | IsEmployee]
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request, pk):
        serializer = Set2FASecretSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            account = SonyAccount.objects.get(pk=pk)
        except SonyAccount.DoesNotExist:
            return Response({"detail": "SonyAccount not found"}, status=status.HTTP_404_NOT_FOUND)

        secret = serializer.validated_data['secret']
        account.set_totp_secret(secret)
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

        otp = account.get_otp()
        if not otp:
            return Response({"detail": "2FA is not enabled for this account"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = OTPSerializer(data=otp)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
