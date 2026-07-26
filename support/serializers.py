from rest_framework import serializers

from support.models import Ticket, TicketMessage


class TicketMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketMessage
        fields = [
            "id",
            "sender_type",
            "body",
            "attachment",
            "created_at",
        ]
        read_only_fields = ["id", "sender_type", "created_at"]


class TicketListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            "id",
            "title",
            "category",
            "status",
            "priority",
            "created_at",
            "closed_at",
        ]


class TicketDetailSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            "id",
            "title",
            "category",
            "status",
            "priority",
            "created_at",
            "updated_at",
            "closed_at",
            "messages",
        ]

    def get_messages(self, obj):
        qs = obj.messages.filter(is_deleted=False, is_internal=False).order_by(
            "created_at"
        )
        return TicketMessageSerializer(qs, many=True).data


class TicketCreateSerializer(serializers.ModelSerializer):
    body = serializers.CharField(write_only=True)

    class Meta:
        model = Ticket
        fields = ["title", "category", "priority", "body"]

    def create(self, validated_data):
        body = validated_data.pop("body")
        ticket = Ticket.objects.create(**validated_data)
        TicketMessage.objects.create(
            ticket=ticket,
            sender_type="customer",
            sender_customer=ticket.customer,
            body=body,
        )
        return ticket


class TicketReplySerializer(serializers.Serializer):
    body = serializers.CharField()

    def create(self, validated_data):
        ticket = self.context["ticket"]
        customer = self.context["customer"]
        return TicketMessage.objects.create(
            ticket=ticket,
            sender_type="customer",
            sender_customer=customer,
            body=validated_data["body"],
        )


class TicketAssignSerializer(serializers.Serializer):
    assigned_to_id = serializers.IntegerField()


class TicketStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Ticket.STATUS_CHOICES)


class TicketInternalNoteSerializer(serializers.Serializer):
    body = serializers.CharField()


class EmployeeTicketListSerializer(serializers.ModelSerializer):
    customer_phone = serializers.CharField(source="customer.user.phone", read_only=True)
    customer_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            "id",
            "title",
            "category",
            "status",
            "priority",
            "customer_phone",
            "customer_name",
            "assigned_to",
            "assigned_to_name",
            "created_at",
            "updated_at",
        ]

    def get_customer_name(self, obj):
        return obj.customer.full_name()

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}"
        return None


class EmployeeTicketDetailSerializer(serializers.ModelSerializer):
    messages = TicketMessageSerializer(many=True, read_only=True)
    customer_phone = serializers.CharField(source="customer.user.phone", read_only=True)
    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            "id",
            "title",
            "category",
            "status",
            "priority",
            "customer_phone",
            "customer_name",
            "assigned_to",
            "created_at",
            "updated_at",
            "closed_at",
            "messages",
        ]

    def get_customer_name(self, obj):
        return obj.customer.full_name()


class EmployeeInternalNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketMessage
        fields = [
            "id",
            "body",
            "sender_type",
            "is_internal",
            "created_at",
        ]
        read_only_fields = ["id", "sender_type", "is_internal", "created_at"]
