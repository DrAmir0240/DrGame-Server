from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, filters
from rest_framework.response import Response

from hr.models import Employee
from hr.serializers import EmployeeSerializer

from orders.models import SonyAccountOrderCategory
from psn.filters import (
    HrSonyAccountFilter,
    SonyAccountFilter,
    SonyAccountPersonalFilter,
)
from psn.models import SonyAccount, SonyAccountBank, SonyAccountGame, SonyAccountStatus
from psn.serializers import (
    EmployeeSonyAccountBankSerializer,
    EmployeeSonyAccountSerializer,
    EmployeeSonyAccountStatusSerializer,
    PSNGameListSerializer,
    PSNSonyAccountCategorySerializer,
    PSNSonyAccountStatusSerializer,
    SonyAccountCreateSerializer,
    SonyAccountDetailSerializer,
    SonyAccountGameCreateInputSerializer,
    SonyAccountGameListSerializer,
    SonyAccountListSerializer,
)
from psn.services import bulk_add_games_to_account
from users.auth import CustomJWTAuthentication
from users.permissions import IsEmployee, IsMainManager
from website.models import Game
from website.serializers import EmployeeGameSerializer


# Create your views here.


# ==================== SonyAccounts Views ====================
class EmployeePanelGetNewSonyAccount(generics.GenericAPIView):
    serializer_class = EmployeeSonyAccountSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, *args, **kwargs):
        employee = request.user.employee

        # Step 1: check the employee's current accounts
        unchecked_account = (
            SonyAccount.objects.filter(
                employee=employee, is_deleted=False, games__isnull=True
            )
            .filter(Q(status__is_available=True) | Q(status__isnull=True))
            .first()
        )

        if unchecked_account:
            return Response(
                {"error": "You have an unchecked account; please check that account first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Step 2: get the oldest account without an employee
        oldest_account = (
            SonyAccount.objects.filter(
                employee__isnull=True, is_deleted=False, is_owned=False
            )
            .order_by("created_at")
            .first()
        )

        if not oldest_account:
            return Response(
                {"error": "No free account is available for assignment."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # assign to the employee
        oldest_account.employee = employee
        oldest_account.save()

        serializer = self.get_serializer(oldest_account)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EmployeePanelSonyAccountList(generics.ListAPIView):
    queryset = SonyAccount.objects.filter(is_deleted=False)
    serializer_class = EmployeeSonyAccountSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = HrSonyAccountFilter
    search_fields = ["employee__first_name", "employee__last_name", "status__title"]
    ordering_fields = ["created_at", "amount"]


class EmployeePanelSonyAccountDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SonyAccount.objects.filter(is_deleted=False)
    serializer_class = EmployeeSonyAccountSerializer
    permission_classes = [IsEmployee | IsMainManager]
    authentication_classes = [CustomJWTAuthentication]
    lookup_field = "pk"


class EmployeePanelSonyAccountChoices(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        games = Game.objects.all()
        statuses = SonyAccountStatus.objects.all()
        employees = Employee.objects.all()
        bank_accounts = SonyAccountBank.objects.all()
        response_data = {
            "games": EmployeeGameSerializer(games, many=True).data,
            "statuses": EmployeeSonyAccountStatusSerializer(statuses, many=True).data,
            "hr": EmployeeSerializer(employees, many=True).data,
            "banks": EmployeeSonyAccountBankSerializer(bank_accounts, many=True).data,
        }
        return Response(response_data)


# -------------------- sony-users --------------------
class EmployeePanelOwnedSonyAccountList(generics.ListAPIView):
    serializer_class = EmployeeSonyAccountSerializer
    permission_classes = [IsEmployee]
    authentication_classes = [CustomJWTAuthentication]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = SonyAccountPersonalFilter
    search_fields = ["username", "status__title"]

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


# ============================================================
# PSN WEBSITE VIEWS (Phase 2)
# ============================================================


class PSNSonyAccountListCreateView(generics.ListCreateAPIView):
    queryset = SonyAccount.objects.all()
    permission_classes = [IsEmployee]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = SonyAccountFilter
    search_fields = ["username"]

    @extend_schema(
        summary="List or create Sony accounts",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="List or create Sony accounts",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SonyAccountCreateSerializer
        return SonyAccountListSerializer


class PSNSonyAccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SonyAccount.objects.all()
    serializer_class = SonyAccountDetailSerializer
    permission_classes = [IsEmployee]

    @extend_schema(
        summary="Retrieve, update or delete a Sony account",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve, update or delete a Sony account",
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve, update or delete a Sony account",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve, update or delete a Sony account",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_destroy(self, instance) -> None:
        instance.is_deleted = True
        instance.save()


class PSNSonyAccountGameListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsEmployee]

    @extend_schema(
        summary="List or bulk-add games to a Sony account",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="List or bulk-add games to a Sony account",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SonyAccountGameCreateInputSerializer
        return SonyAccountGameListSerializer

    def get_queryset(self):
        account_pk = self.kwargs["account_pk"]
        return SonyAccountGame.objects.filter(
            sony_account_id=account_pk, is_deleted=False
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account_pk = self.kwargs["account_pk"]
        game_ids = serializer.validated_data["game_ids"]
        created = bulk_add_games_to_account(account_pk, game_ids)
        output_serializer = SonyAccountGameListSerializer(created, many=True)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class PSNSonyAccountGameDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = SonyAccountGameListSerializer
    permission_classes = [IsEmployee]

    @extend_schema(
        summary="Retrieve or remove a game from a Sony account",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve or remove a game from a Sony account",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        account_pk = self.kwargs["account_pk"]
        return SonyAccountGame.objects.filter(sony_account_id=account_pk)

    def perform_destroy(self, instance) -> None:
        instance.is_deleted = True
        instance.save()


class PSNGameListView(generics.ListAPIView):
    queryset = Game.objects.filter(is_deleted=False)
    serializer_class = PSNGameListSerializer
    permission_classes = [IsEmployee]
    filter_backends = [filters.SearchFilter]
    search_fields = ["title"]

    @extend_schema(
        summary="List games (lightweight — id, title, image only)",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PSNSonyAccountStatusListCreateView(generics.ListCreateAPIView):
    queryset = SonyAccountStatus.objects.all()
    serializer_class = PSNSonyAccountStatusSerializer
    permission_classes = [IsEmployee]

    @extend_schema(
        summary="List or create Sony account statuses",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="List or create Sony account statuses",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PSNSonyAccountStatusDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SonyAccountStatus.objects.all()
    serializer_class = PSNSonyAccountStatusSerializer
    permission_classes = [IsEmployee]

    @extend_schema(
        summary="Retrieve, update or delete a Sony account status",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve, update or delete a Sony account status",
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve, update or delete a Sony account status",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve, update or delete a Sony account status",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class PSNSonyAccountCategoryListView(generics.ListAPIView):
    queryset = SonyAccountOrderCategory.objects.filter(is_deleted=False)
    serializer_class = PSNSonyAccountCategorySerializer
    permission_classes = [IsEmployee]

    @extend_schema(
        summary="List Sony account order categories",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
