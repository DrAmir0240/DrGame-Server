# ================= Global Search View =================
from django.db.models import Q
from rest_framework import generics
from rest_framework.response import Response

from accounting.models import Transaction
from accounting.serializers import TransactionSearchSerializer
from crm.models import Customer
from crm.serializers import CustomerSearchSerializer
from docs.serializers import DocumentSearchSerializer
from hr.models import Employee
from hr.serializers import EmployeeSearchSerializer

from inventory.models import Game, SonyAccount, Document, RealAssets
from inventory.serializers import RealAssetsSearchSerializer
from psn.serializers import SonyAccountSearchSerializer
from users.auth import CustomJWTAuthentication
from users.permissions import IsMainManager
from website.serializers import GameSearchSerializer


class GlobalSearchAPIView(generics.GenericAPIView):
    permission_classes = [IsMainManager]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request):
        q = request.query_params.get("q", "").strip()

        if not q or len(q) < 2:
            return Response({
                "crm": [],
                "hr": [],
                "games": [],
                "sony_accounts": [],
                "documents": [],
                "real_assets": [],
                "transactions": [],
            })

        customers = Customer.objects.filter(
            is_deleted=False,
            full_name__icontains=q
        )[:5]

        employees = Employee.objects.filter(
            is_deleted=False
        ).filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q)
        )[:5]

        games = Game.objects.filter(
            is_deleted=False,
            title__icontains=q
        )[:5]

        sony_accounts = SonyAccount.objects.filter(
            is_deleted=False,
            username__icontains=q
        )[:5]

        documents = Document.objects.filter(
            is_deleted=False,
            title__icontains=q
        )[:5]

        real_assets = RealAssets.objects.filter(
            is_deleted=False,
            title__icontains=q
        )[:5]

        transactions = Transaction.objects.filter(
            is_deleted=False
        ).filter(
            Q(payer_str__icontains=q) |
            Q(receiver_str__icontains=q) |
            Q(payer__phone__icontains=q) |
            Q(receiver__phone__icontains=q)
        )[:5]

        return Response({
            "crm": CustomerSearchSerializer(customers, many=True).data,
            "hr": EmployeeSearchSerializer(employees, many=True).data,
            "games": GameSearchSerializer(games, many=True).data,
            "sony_accounts": SonyAccountSearchSerializer(sony_accounts, many=True).data,
            "documents": DocumentSearchSerializer(documents, many=True).data,
            "real_assets": RealAssetsSearchSerializer(real_assets, many=True).data,
            "transactions": TransactionSearchSerializer(transactions, many=True).data,
        })

