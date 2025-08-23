# your_app/views.py
import secrets
from datetime import timedelta
import requests
from django.contrib.auth import authenticate
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from DrGame import settings
from accounts.auth import CustomJWTAuthentication
from accounts.models import CustomUser, OTP, APIKey, MainManager
from accounts.serializers import VerifyOTPSerializer, VerifyOTPResponseSerializer, RefreshTokenSerializer, \
    RefreshTokenResponseSerializer, RequestOTPSerializer, RequestOTPResponseSerializer
from accounts.throttles import PhoneRateThrottle
from customers.models import Customer
from employees.models import Employee, Repairman


class CreateAPIKeyView(APIView):
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        phone = request.data.get('phone')
        password = request.data.get('password')
        client_name = request.data.get('client_name')

        if not phone or not password or not client_name:
            return Response(
                {"error": "شماره موبایل، رمز عبور و نام کلاینت الزامی است"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(phone=phone, password=password)
        if not user or not user.is_superuser:
            return Response(
                {"error": "فقط سوپریوزرها می‌توانند API Key تولید کنند"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        api_key = APIKey.objects.create(client_name=client_name)

        return Response(
            {
                "api_key": api_key.key,
                "client_name": api_key.client_name
            },
            status=status.HTTP_201_CREATED
        )

    def get(self, request):
        return Response(
            {"error": "فقط متد POST پشتیبانی می‌شود"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class RequestOTPView(APIView):
    throttle_classes = [AnonRateThrottle, PhoneRateThrottle]
    permission_classes = [AllowAny]

    @extend_schema(
        request=RequestOTPSerializer,
        responses={
            200: RequestOTPResponseSerializer,
            400: RequestOTPResponseSerializer,
            403: RequestOTPResponseSerializer,
            500: RequestOTPResponseSerializer
        },
        description="ارسال درخواست OTP با شماره موبایل"
    )
    def post(self, request):
        # (بقیه کد همونیه که فرستادی)
        api_key = request.headers.get('X-API-Key')
        if not api_key or not APIKey.objects.filter(key=api_key, is_active=True).exists():
            return Response(
                {"error": "API Key نامعتبر است"},
                status=status.HTTP_403_FORBIDDEN
            )
        phone = request.data.get('phone')
        if not phone:
            return Response(
                {"error": "شماره موبایل الزامی است"},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = CustomUser.objects.filter(phone=phone).first()
        if not user:
            user = CustomUser.objects.create(phone=phone, is_active=False)
        OTP.objects.filter(user=user).delete()
        otp_code = str(secrets.randbelow(100000)).zfill(5)
        print(otp_code)
        expires_at = timezone.now() + timedelta(minutes=2)
        otp = OTP.objects.create(user=user, code=otp_code, expires_at=expires_at)
        success, message = otp.send_otp(phone=phone, otp_code=otp_code)
        if not success:
            return Response(
                {"error": f"خطا در ارسال OTP: {message}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return Response(
            {"message": "لطفاً کد OTP را وارد کنید"},
            status=status.HTTP_200_OK
        )


class VerifyOTPView(APIView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]

    @extend_schema(
        request=VerifyOTPSerializer,
        responses={
            200: VerifyOTPResponseSerializer,
            400: VerifyOTPResponseSerializer,
            403: VerifyOTPResponseSerializer,
            404: VerifyOTPResponseSerializer
        },
        description="تأیید کد OTP و دریافت توکن‌های دسترسی"
    )
    def post(self, request):
        # (بقیه کد همونیه که فرستادی)
        api_key = request.headers.get('X-API-Key')
        if not api_key or not APIKey.objects.filter(key=api_key, is_active=True).exists():
            return Response(
                {"error": "Invalid API Key"},
                status=status.HTTP_403_FORBIDDEN
            )
        phone = request.data.get('phone')
        code = request.data.get('code')
        if not phone or not code:
            return Response(
                {"error": "Phone Parents and OTP code are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = CustomUser.objects.get(phone=phone)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        try:
            otp = OTP.objects.filter(user=user).latest('created_at')
            if otp.code != code or not otp.is_valid():
                return Response(
                    {"error": "Invalid or expired OTP"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            otp.delete()
            if not user.is_active:
                user.is_active = True
                user.save()
        except OTP.DoesNotExist:
            return Response(
                {"error": "No OTP found"},
                status=status.HTTP_400_BAD_REQUEST
            )
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        response = Response(
            {"message": "Login successful"},
            status=status.HTTP_200_OK
        )
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            max_age=int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds())
        )
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            max_age=int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
        )
        return response


class RefreshTokenView(APIView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]

    @extend_schema(
        request=RefreshTokenSerializer,
        responses={
            200: RefreshTokenResponseSerializer,
            401: RefreshTokenResponseSerializer,
            403: RefreshTokenResponseSerializer
        },
        description="رفرش توکن برای دریافت توکن دسترسی جدید"
    )
    def post(self, request):
        # (بقیه کد همونیه که فرستادی)
        api_key = request.headers.get('X-API-Key')
        if not api_key or not APIKey.objects.filter(key=api_key, is_active=True).exists():
            return Response(
                {"error": "Invalid API Key"},
                status=status.HTTP_403_FORBIDDEN
            )
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response(
                {"error": "No refresh token provided"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            response = Response(
                {"message": "Token refreshed successfully"},
                status=status.HTTP_200_OK
            )
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                max_age=3600
            )
            if hasattr(refresh, 'token'):
                response.set_cookie(
                    key='refresh_token',
                    value=str(refresh),
                    httponly=True,
                    secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                    max_age=432000
                )
            return response
        except TokenError as e:
            return Response(
                {"error": f"Invalid refresh token: {str(e)}"},
                status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(APIView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request):  # اضافه کردن متد GET
        return self.post(request)  # استفاده از منطق POST

    def post(self, request):
        api_key = request.headers.get('X-API-Key')
        if not api_key or not APIKey.objects.filter(key=api_key, is_active=True).exists():
            return Response(
                {"error": "Invalid API Key"},
                status=status.HTTP_403_FORBIDDEN
            )

        response = Response(
            {"message": "Logout successful"},
            status=status.HTTP_200_OK
        )
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        return response


class UserStatusView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"is_authenticated": False},
                status=200
            )

        user = request.user
        user_type = None
        user_pic = None
        employee_role = None
        user_name = None
        employee_permissions = {}

        if MainManager.objects.filter(user=user).exists():
            main_manager = get_object_or_404(MainManager, user=user)
            user_type = "main_manager"
            user_name = main_manager.name

        elif Employee.objects.filter(user=user).exists():
            user_type = "employee"
            employee = get_object_or_404(Employee, user=user)
            employee_role = employee.role
            if employee.profile_picture:
                user_pic = employee.profile_picture.url
            user_name = f"{employee.first_name} {employee.last_name}"

            permission_fields = [
                "has_access_to_organize_tasks",
                "has_access_to_game_orders",
                "has_access_to_product_order",
                "has_access_to_repair_order",
                "has_access_to_personal_account",
                "has_access_to_all_accounts",
                "has_access_to_add_accounts",
                "has_access_to_transactions",
                "has_access_to_customer_read",
                "has_access_to_customer_write",
                "has_access_to_employees_read",
                "has_access_to_employees_write",
                "has_access_to_repairmen_read",
                "has_access_to_repairmen_write",
                "has_access_to_docs_read",
                "has_access_to_docs_write",
                "has_access_to_assets_read",
                "has_access_to_assets_write",
                "has_access_to_products",
                "has_access_to_game_store",
                "has_access_to_blogs",
                "has_access_to_messenger",
                "has_access_to_reports",
                "has_access_to_requests"
            ]

            # پر کردن دیکشنری پرمیشن‌ها به صورت True/False
            for field in permission_fields:
                employee_permissions[field] = getattr(employee, field, False)

        elif Repairman.objects.filter(user=user).exists():
            user_type = "repairman"
            repairman = get_object_or_404(Repairman, user=user)
            user_name = f"{repairman.first_name} {repairman.last_name}"

        elif Customer.objects.filter(user=user).exists():
            user_type = "customer"
            customer = get_object_or_404(Customer, user=user)
            user_name = customer.full_name
            if user.customer.profile_pic:
                user_pic = user.customer.profile_pic.url
        else:
            user_type = "none"

        return Response(
            {
                "is_authenticated": True,
                "user_type": user_type,
                "employee_role": employee_role,
                "user_name": user_name,
                "user_id": user.id,
                "user_pic": user_pic,
                "employee_permissions": employee_permissions,
            },
            status=200
        )
