from django.db import transaction as db_transaction

from accounting.models import Wallet, WalletTransaction


class WalletService:
    @staticmethod
    @db_transaction.atomic
    def charge(wallet, amount, type_="charge_admin", **kwargs):
        wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)
        balance_before = wallet.balance
        wallet.balance += amount
        wallet.save(update_fields=["balance", "updated_at"])

        return WalletTransaction.objects.create(
            wallet=wallet,
            type=type_,
            amount=amount,
            status="success",
            balance_before=balance_before,
            balance_after=wallet.balance,
            **kwargs,
        )

    @staticmethod
    @db_transaction.atomic
    def debit(wallet, amount, description="", order_ct=None, order_id=None):
        wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)
        if wallet.balance < amount:
            raise ValueError("موجودی کافی نیست")
        balance_before = wallet.balance
        wallet.balance -= amount
        wallet.save(update_fields=["balance", "updated_at"])

        return WalletTransaction.objects.create(
            wallet=wallet,
            type="debit_order",
            amount=amount,
            status="success",
            balance_before=balance_before,
            balance_after=wallet.balance,
            description=description,
            order_content_type=order_ct,
            order_object_id=order_id,
        )
