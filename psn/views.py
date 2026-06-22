from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, filters
from rest_framework.response import Response

from hr.filters import SonyAccountFilter, SonyAccountPersonalFilter
from hr.models import Employee
from hr.serializers import EmployeeSerializer

from inventory.models import SonyAccount, Game, SonyAccountStatus, SonyAccountBank
from psn.serializers import EmployeeSonyAccountSerializer, EmployeeSonyAccountStatusSerializer
from users.auth import CustomJWTAuthentication
from users.permissions import IsEmployee, IsMainManager
from website.serializers import EmployeeGameSerializer


# Create your views here.

# ==================== SonyAccounts Views ====================
class EmployeePanelGetNewSonyAccount(generics.GenericAPIView):
    serializer_class = EmployeeSonyAccountSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, *args, **kwargs):
        employee = request.user.employee

        # مرحله اول: بررسی اکانت‌های فعلی کارمند
        unchecked_account = SonyAccount.objects.filter(
            employee=employee,
            is_deleted=False,
            games__isnull=True
        ).filter(
            Q(status__is_available=True) | Q(status__isnull=True)
        ).first()

        if unchecked_account:
            return Response(
                {"error": "شمااکانت چک‌نشده دارید، لطفاً اول همان اکانت را بررسی کنید."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # مرحله دوم: گرفتن قدیمی‌ترین اکانت بدون کارمند
        oldest_account = SonyAccount.objects.filter(
            employee__isnull=True,
            is_deleted=False,
            is_owned=False
        ).order_by('created_at').first()

        if not oldest_account:
            return Response(
                {"error": "هیچ اکانت آزادی برای اختصاص یافتن موجود نیست."},
                status=status.HTTP_404_NOT_FOUND
            )

        # اساین به کارمند
        oldest_account.employee = employee
        oldest_account.save()

        serializer = self.get_serializer(oldest_account)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EmployeePanelSonyAccountList(generics.ListAPIView):
    queryset = SonyAccount.objects.filter(is_deleted=False)
    serializer_class = EmployeeSonyAccountSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SonyAccountFilter
    search_fields = ['employee__first_name', 'employee__last_name', 'status__title']
    ordering_fields = ['created_at', 'amount']


class EmployeePanelSonyAccountDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SonyAccount.objects.filter(is_deleted=False)
    serializer_class = EmployeeSonyAccountSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    lookup_field = 'pk'


class EmployeePanelSonyAccountChoices(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        games = Game.objects.all()
        statuses = SonyAccountStatus.objects.all()
        employees = Employee.objects.all()
        bank_accounts = SonyAccountBank.objects.all()
        response_data = {
            'games': EmployeeGameSerializer(games, many=True).data,
            'statuses': EmployeeSonyAccountStatusSerializer(statuses, many=True).data,
            'hr': EmployeeSerializer(employees, many=True).data,
            'banks': EmployeeSonyAccountBankSerializer(bank_accounts, many=True).data,
        }
        return Response(response_data)
# -------------------- sony-users --------------------
class EmployeePanelOwnedSonyAccountList(generics.ListAPIView):
    serializer_class = EmployeeSonyAccountSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SonyAccountPersonalFilter
    search_fields = ['username', 'status__title']

    def get_queryset(self):
        user = self.request.user
        try:
            employee = user.employee
            return SonyAccount.objects.filter(employee=employee)
        except AttributeError:
            return Response(status=404)


class EmployeePanelOwnedSonyAccountDetail(generics.RetrieveUpdateAPIView):
    serializer_class = EmployeeSonyAccountSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]

    def get_queryset(self):
        user = self.request.user
        try:
            employee = user.employee
            return SonyAccount.objects.filter(employee=employee)
        except AttributeError:
            return Response(status=404)