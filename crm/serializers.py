from django.db import models
from rest_framework import serializers

from accounting.models import Transaction, Invoice, WalletTransaction
from crm.models import Customer, B2BProfile, CustomerWishlist


class CustomerListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    has_b2b = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            "id",
            "full_name",
            "phone",
            "address",
            "postal_code",
            "profile_pic",
            "has_b2b",
            "created_at",
        ]

    def get_full_name(self, obj):
        return obj.user.full_name()

    def get_phone(self, obj):
        return obj.user.phone  # or any field that CustomUser has

    def get_has_b2b(self, obj):
        return hasattr(obj, "b2b_profile") and not obj.b2b_profile.is_deleted


class CustomerCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["address", "postal_code", "profile_pic"]

    def destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=("is_deleted",))
        return instance


class B2BProfileSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(source="customer.id", read_only=True)

    class Meta:
        model = B2BProfile
        fields = [
            "id",
            "customer_id",
            "business_title",
            "debt_amount_max",
            "uni_id",
            "discount",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "customer_id", "created_at", "updated_at"]

    def destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=("is_deleted",))
        return instance


class CustomerTransactionListSerializer(serializers.ModelSerializer):
    direction_display = serializers.CharField(
        source="get_direction_display", read_only=True
    )
    bank_account_name = serializers.CharField(
        source="bank_account.__str__", read_only=True
    )
    invoice_id = serializers.IntegerField(
        source="invoice.id", read_only=True, allow_null=True
    )

    class Meta:
        model = Transaction
        fields = [
            "id",
            "amount",
            "direction",
            "direction_display",
            "bank_account_id",
            "bank_account_name",
            "invoice_id",
            "description",
            "created_at",
        ]


class CustomerInvoiceListSerializer(serializers.ModelSerializer):
    total_items_price = serializers.SerializerMethodField()
    paid_amount = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            "id",
            "total_items_price",
            "paid_amount",
            "created_at",
            "updated_at",
        ]

    def get_total_items_price(self, obj):
        return sum(item.total_price for item in obj.items.filter(is_deleted=False))

    def get_paid_amount(self, obj):
        return (
            obj.transactions.filter(is_deleted=False, direction="in").aggregate(
                total=models.Sum("amount")
            )["total"]
            or 0
        )


class CustomerSummarySerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    full_name = serializers.CharField()

    product_orders_count = serializers.IntegerField()
    repair_orders_count = serializers.IntegerField()
    sony_account_orders_count = serializers.IntegerField()
    total_orders_count = serializers.IntegerField()

    total_transactions_amount = serializers.IntegerField()
    total_invoices_amount = serializers.IntegerField()


class SendSmsSerializer(serializers.Serializer):
    message = serializers.CharField()
    customer_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False
    )
    send_time = serializers.DateTimeField(required=False)


# ==================== Customer Profile ====================


class CustomerProfileSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source="user.phone", read_only=True)
    first_name = serializers.CharField(source="user.first_name", allow_blank=True)
    last_name = serializers.CharField(source="user.last_name", allow_blank=True)
    wallet_balance = serializers.SerializerMethodField()
    is_b2b = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            "id",
            "phone",
            "first_name",
            "last_name",
            "address",
            "postal_code",
            "profile_pic",
            "wallet_balance",
            "is_b2b",
        ]

    def get_wallet_balance(self, obj):
        try:
            return obj.user.wallet.balance
        except Exception:
            return 0

    def get_is_b2b(self, obj):
        return hasattr(obj, "b2b_profile") and not obj.b2b_profile.is_deleted

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        if user_data.get("first_name") is not None:
            instance.user.first_name = user_data["first_name"]
        if user_data.get("last_name") is not None:
            instance.user.last_name = user_data["last_name"]
        instance.user.save()
        return super().update(instance, validated_data)


class CustomerProfilePicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["profile_pic"]


# ==================== Wishlist ====================


class CustomerWishlistSerializer(serializers.ModelSerializer):
    object_type = serializers.SerializerMethodField()
    object_detail = serializers.SerializerMethodField()

    class Meta:
        model = CustomerWishlist
        fields = ["id", "object_type", "object_id", "object_detail", "created_at"]

    def get_object_type(self, obj):
        model_name = obj.content_type.model
        if model_name == "product":
            return "product"
        if model_name == "game":
            return "game"
        return model_name

    def get_object_detail(self, obj):
        if not obj.content_object:
            return None
        model_name = obj.content_type.model
        if model_name == "product":
            from inventory.serializers import ProductSerializer

            return ProductSerializer(obj.content_object).data
        if model_name == "game":
            from inventory.serializers import GameSerializer

            return GameSerializer(obj.content_object).data
        return str(obj.content_object)


class CustomerWishlistWriteSerializer(serializers.ModelSerializer):
    object_type = serializers.ChoiceField(choices=["product", "game"])
    object_id = serializers.IntegerField()

    class Meta:
        model = CustomerWishlist
        fields = ["object_type", "object_id"]

    def validate(self, data):
        from django.contrib.contenttypes.models import ContentType

        content_type_map = {
            "product": ContentType.objects.get(app_label="inventory", model="product"),
            "game": ContentType.objects.get(app_label="website", model="game"),
        }
        ct = content_type_map[data["object_type"]]
        model_class = ct.model_class()
        if not model_class.objects.filter(
            pk=data["object_id"], is_deleted=False
        ).exists():
            raise serializers.ValidationError("Requested item not found")
        return data

    def create(self, validated_data):
        from django.contrib.contenttypes.models import ContentType

        content_type_map = {
            "product": ContentType.objects.get(app_label="inventory", model="product"),
            "game": ContentType.objects.get(app_label="website", model="game"),
        }
        ct = content_type_map[validated_data["object_type"]]
        customer = self.context["request"].user.customer
        obj, created = CustomerWishlist.objects.get_or_create(
            customer=customer,
            content_type=ct,
            object_id=validated_data["object_id"],
            defaults={"is_deleted": False},
        )
        if not created:
            obj.is_deleted = False
            obj.save()
        return obj


class WishlistToggleSerializer(serializers.Serializer):
    object_type = serializers.ChoiceField(choices=["product", "game"])
    object_id = serializers.IntegerField()


# ==================== Wallet ====================


class CustomerWalletTransactionSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = WalletTransaction
        fields = [
            "id",
            "type",
            "type_display",
            "amount",
            "status",
            "status_display",
            "description",
            "balance_before",
            "balance_after",
            "created_at",
        ]


class WalletChargeSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1000)
