from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from support.models import Ticket, TicketMessage
from support.serializers import (
    TicketListSerializer,
    TicketDetailSerializer,
    TicketCreateSerializer,
    TicketReplySerializer,
    TicketMessageSerializer,
    EmployeeTicketListSerializer,
    EmployeeTicketDetailSerializer,
    TicketAssignSerializer,
    TicketStatusSerializer,
    TicketInternalNoteSerializer,
    EmployeeInternalNoteSerializer,
)
from users.permissions import IsCustomer, IsTicketOwner, IsEmployee, IsMainManager


class CustomerTicketListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = TicketListSerializer

    def get_queryset(self):
        return Ticket.objects.filter(
            customer=self.request.user.customer, is_deleted=False
        ).order_by("-created_at")


class CustomerTicketDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsCustomer, IsTicketOwner]
    serializer_class = TicketDetailSerializer

    def get_queryset(self):
        return Ticket.objects.filter(is_deleted=False)


class CustomerTicketCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = TicketCreateSerializer

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer)


class CustomerTicketReplyView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsCustomer, IsTicketOwner]
    serializer_class = TicketReplySerializer

    def get_serializer_context(self):
        ticket = self.get_object()
        return {
            "ticket": ticket,
            "customer": self.request.user.customer,
        }

    def get_queryset(self):
        return Ticket.objects.filter(is_deleted=False)

    def get_object(self):
        obj = generics.get_object_or_404(
            Ticket.objects.filter(is_deleted=False), pk=self.kwargs["pk"]
        )
        self.check_object_permissions(self.request, obj)
        return obj

    def create(self, request, *args, **kwargs):
        ticket = self.get_object()
        if ticket.status == "closed":
            return Response(
                {"detail": "Ticket is closed and you cannot reply"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        msg = serializer.save()
        return Response(
            TicketMessageSerializer(msg).data, status=status.HTTP_201_CREATED
        )


class CustomerTicketMessagesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsCustomer, IsTicketOwner]
    serializer_class = TicketMessageSerializer

    def get_queryset(self):
        ticket = generics.get_object_or_404(
            Ticket.objects.filter(is_deleted=False), pk=self.kwargs["pk"]
        )
        self.check_object_permissions(self.request, ticket)
        return TicketMessage.objects.filter(
            ticket=ticket, is_deleted=False, is_internal=False
        ).order_by("created_at")


class EmployeeTicketListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsEmployee | IsMainManager]
    serializer_class = EmployeeTicketListSerializer
    filterset_fields = ["status", "priority", "category", "assigned_to"]

    def get_queryset(self):
        return Ticket.objects.filter(is_deleted=False).select_related(
            "customer__user", "assigned_to"
        )


class EmployeeTicketDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsEmployee | IsMainManager]
    serializer_class = EmployeeTicketDetailSerializer

    def get_queryset(self):
        return Ticket.objects.filter(is_deleted=False).select_related(
            "customer__user", "assigned_to"
        )


class EmployeeTicketAssignView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsEmployee | IsMainManager]
    serializer_class = TicketAssignSerializer

    def get_queryset(self):
        return Ticket.objects.filter(is_deleted=False)

    def update(self, request, *args, **kwargs):
        ticket = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        from hr.models import Employee

        try:
            emp = Employee.objects.get(pk=serializer.validated_data["assigned_to_id"])
        except Employee.DoesNotExist:
            return Response(
                {"detail": "Invalid employee"}, status=status.HTTP_400_BAD_REQUEST
            )
        ticket.assigned_to = emp
        ticket.status = "in_progress"
        ticket.save(update_fields=["assigned_to", "status"])
        TicketMessage.objects.create(
            ticket=ticket,
            sender_type="system",
            body=f"Ticket assigned to {emp.first_name} {emp.last_name}",
        )
        return Response({"detail": "Ticket assigned"})


class EmployeeTicketStatusView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsEmployee | IsMainManager]
    serializer_class = TicketStatusSerializer

    def get_queryset(self):
        return Ticket.objects.filter(is_deleted=False)

    def update(self, request, *args, **kwargs):
        ticket = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data["status"]
        old_status = ticket.status
        ticket.status = new_status
        if new_status == "closed":
            from django.utils import timezone

            ticket.closed_at = timezone.now()
        ticket.save()
        TicketMessage.objects.create(
            ticket=ticket,
            sender_type="system",
            body=f"Ticket status changed from {dict(Ticket.STATUS_CHOICES).get(old_status, old_status)} to {dict(Ticket.STATUS_CHOICES).get(new_status, new_status)}",
        )
        return Response({"detail": "Ticket status changed"})


class EmployeeTicketInternalNoteView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsEmployee | IsMainManager]
    serializer_class = EmployeeInternalNoteSerializer

    def get_queryset(self):
        return Ticket.objects.filter(is_deleted=False)

    def create(self, request, *args, **kwargs):
        ticket = generics.get_object_or_404(
            Ticket.objects.filter(is_deleted=False), pk=self.kwargs["pk"]
        )
        body = request.data.get("body", "")
        if not body:
            return Response(
                {"detail": "Note text is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        msg = TicketMessage.objects.create(
            ticket=ticket,
            sender_type="employee",
            sender_employee=request.user.employee,
            body=body,
            is_internal=True,
        )
        return Response(
            EmployeeInternalNoteSerializer(msg).data, status=status.HTTP_201_CREATED
        )
