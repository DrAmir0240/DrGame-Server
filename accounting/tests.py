from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounting.models import (
    BankAccount, AccountSide, InvoiceCategory, Invoice, Transaction,
)
from users.models import CustomUser


class AccountingTestBase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(phone='09120000001')

        cls.bank_account = BankAccount.objects.create(title='بانک ملت')
        cls.bank_account_2 = BankAccount.objects.create(title='بانک ملی')

        cls.customer_side = AccountSide.objects.create(name='مشتری تست', type='customer')
        cls.supplier_side = AccountSide.objects.create(name='تامین‌کننده تست', type='supplier')
        cls.employee_side = AccountSide.objects.create(name='کارمند تست', type='employee')

        cls.category_in = InvoiceCategory.objects.create(title='خرید', direction='in')
        cls.category_out = InvoiceCategory.objects.create(title='فروش', direction='out')

    def auth(self):
        self.client.force_authenticate(user=self.user)

    def unauth(self):
        self.client.force_authenticate(user=None)

    def _create_invoice(self, **kwargs):
        defaults = {
            'account_side': self.customer_side,
            'category': self.category_out,
            'amount': 5000000,
        }
        defaults.update(kwargs)
        return Invoice.objects.create(**defaults)

    def _create_transaction(self, **kwargs):
        invoice = kwargs.pop('invoice', None) or self._create_invoice()
        defaults = {
            'invoice': invoice,
            'account_side': self.customer_side,
            'bank_account': self.bank_account,
            'amount': 2000000,
            'direction': 'out',
        }
        defaults.update(kwargs)
        return Transaction.objects.create(**defaults)


# ─── Invoice CRUD Tests ─────────────────────────────────────────────────────

class InvoiceCRUDTests(AccountingTestBase):

    def test_list_unauthenticated_returns_401(self):
        self.unauth()
        resp = self.client.get(reverse('invoice-list-create'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_invoice(self):
        self.auth()
        data = {
            'account_side_id': self.customer_side.pk,
            'category_id': self.category_out.pk,
            'amount': 3000000,
            'discount': 100000,
            'description': 'تست فاکتور',
        }
        resp = self.client.post(reverse('invoice-list-create'), data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['amount'], 3000000)
        self.assertEqual(resp.data['discount'], 100000)
        self.assertIn('account_side_detail', resp.data)
        self.assertIn('category_detail', resp.data)
        self.assertIn('remaining_amount', resp.data)

    def test_list_invoices(self):
        self.auth()
        self._create_invoice()
        self._create_invoice(amount=1000000)
        resp = self.client.get(reverse('invoice-list-create'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 2)

    def test_retrieve_invoice(self):
        self.auth()
        inv = self._create_invoice()
        resp = self.client.get(reverse('invoice-detail', args=[inv.pk]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['id'], inv.pk)

    def test_update_invoice(self):
        self.auth()
        inv = self._create_invoice()
        resp = self.client.patch(
            reverse('invoice-detail', args=[inv.pk]),
            {'description': 'ویرایش‌شده'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        inv.refresh_from_db()
        self.assertEqual(inv.description, 'ویرایش‌شده')

    def test_soft_delete_invoice(self):
        self.auth()
        inv = self._create_invoice()
        resp = self.client.delete(reverse('invoice-detail', args=[inv.pk]))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        inv.refresh_from_db()
        self.assertTrue(inv.is_deleted)
        self.assertTrue(Invoice.objects.filter(pk=inv.pk).exists())

    def test_soft_deleted_not_in_list(self):
        self.auth()
        inv = self._create_invoice()
        inv.is_deleted = True
        inv.save()
        resp = self.client.get(reverse('invoice-list-create'))
        self.assertEqual(resp.data['count'], 0)

    def test_filter_invoices_by_status(self):
        self.auth()
        self._create_invoice(status='draft')
        self._create_invoice(status='primary')
        self._create_invoice(status='primary')
        resp = self.client.get(reverse('invoice-list-create'), {'status': 'primary'})
        self.assertEqual(resp.data['count'], 2)

    def test_filter_invoices_by_direction(self):
        self.auth()
        self._create_invoice(category=self.category_in)
        self._create_invoice(category=self.category_out)
        resp = self.client.get(reverse('invoice-list-create'), {'direction': 'in'})
        self.assertEqual(resp.data['count'], 1)

    def test_filter_invoices_by_amount_range(self):
        self.auth()
        self._create_invoice(amount=1000)
        self._create_invoice(amount=5000)
        self._create_invoice(amount=10000)
        resp = self.client.get(reverse('invoice-list-create'), {
            'amount_min': 2000,
            'amount_max': 8000,
        })
        self.assertEqual(resp.data['count'], 1)

    def test_remaining_amount(self):
        self.auth()
        inv = self._create_invoice(amount=5000000, discount=500000, paid_amount=1000000)
        resp = self.client.get(reverse('invoice-detail', args=[inv.pk]))
        self.assertEqual(resp.data['remaining_amount'], 3500000)


# ─── Transaction CRUD Tests ─────────────────────────────────────────────────

class TransactionCRUDTests(AccountingTestBase):

    def test_list_unauthenticated_returns_401(self):
        self.unauth()
        resp = self.client.get(reverse('transaction-list-create'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_transaction(self):
        self.auth()
        inv = self._create_invoice()
        data = {
            'invoice_id': inv.pk,
            'account_side_id': self.customer_side.pk,
            'bank_account_id': self.bank_account.pk,
            'amount': 2000000,
            'direction': 'out',
            'description': 'پرداخت تست',
        }
        resp = self.client.post(reverse('transaction-list-create'), data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['amount'], 2000000)
        self.assertIn('account_side_detail', resp.data)
        self.assertIn('bank_account_detail', resp.data)

    def test_soft_delete_transaction(self):
        self.auth()
        txn = self._create_transaction()
        resp = self.client.delete(reverse('transaction-detail', args=[txn.pk]))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        txn.refresh_from_db()
        self.assertTrue(txn.is_deleted)
        self.assertTrue(Transaction.objects.filter(pk=txn.pk).exists())

    def test_filter_transactions_by_bank_account(self):
        self.auth()
        self._create_transaction(bank_account=self.bank_account)
        self._create_transaction(bank_account=self.bank_account_2)
        resp = self.client.get(
            reverse('transaction-list-create'),
            {'bank_account': self.bank_account.pk},
        )
        self.assertEqual(resp.data['count'], 1)


# ─── Daily Ledger Tests ─────────────────────────────────────────────────────

class DailyLedgerTests(AccountingTestBase):

    def test_daily_invoices_unauthenticated(self):
        self.unauth()
        resp = self.client.get(reverse('daily-invoices'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_daily_invoices_default_today(self):
        self.auth()
        self._create_invoice()
        resp = self.client.get(reverse('daily-invoices'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_daily_invoices_with_date_filter(self):
        self.auth()
        self._create_invoice()
        resp = self.client.get(reverse('daily-invoices'), {'date': '2025-01-01'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 0)

    def test_daily_transactions_default_today(self):
        self.auth()
        self._create_transaction()
        resp = self.client.get(reverse('daily-transactions'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_daily_transactions_with_date_filter(self):
        self.auth()
        self._create_transaction()
        resp = self.client.get(reverse('daily-transactions'), {'date': '2025-01-01'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 0)


# ─── Payments / Receipts Tests ───────────────────────────────────────────────

class PaymentReceiptTests(AccountingTestBase):

    def test_payments_only_direction_out(self):
        self.auth()
        self._create_transaction(direction='out')
        self._create_transaction(direction='in')
        resp = self.client.get(reverse('payments'))
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['direction'], 'out')

    def test_receipts_only_direction_in(self):
        self.auth()
        self._create_transaction(direction='out')
        self._create_transaction(direction='in')
        resp = self.client.get(reverse('receipts'))
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['direction'], 'in')

    def test_payments_filter_by_date_range(self):
        self.auth()
        self._create_transaction(direction='out')
        yesterday = (timezone.localdate() - timedelta(days=1)).isoformat()
        tomorrow = (timezone.localdate() + timedelta(days=1)).isoformat()
        resp = self.client.get(reverse('payments'), {
            'date_from': yesterday,
            'date_to': tomorrow,
        })
        self.assertEqual(resp.data['count'], 1)

    def test_payments_filter_by_amount_range(self):
        self.auth()
        self._create_transaction(direction='out', amount=1000)
        self._create_transaction(direction='out', amount=5000)
        resp = self.client.get(reverse('payments'), {
            'amount_min': 3000,
        })
        self.assertEqual(resp.data['count'], 1)


# ─── Payable / Receivable Tests ──────────────────────────────────────────────

class PayableReceivableTests(AccountingTestBase):

    def test_payable_list(self):
        self.auth()
        self._create_invoice(category=self.category_out, payment_status='unpaid')
        self._create_invoice(category=self.category_out, payment_status='partial')
        self._create_invoice(category=self.category_out, payment_status='paid')
        self._create_invoice(category=self.category_in, payment_status='unpaid')
        resp = self.client.get(reverse('payable'))
        self.assertEqual(resp.data['count'], 2)

    def test_receivable_list(self):
        self.auth()
        self._create_invoice(category=self.category_in, payment_status='unpaid')
        self._create_invoice(category=self.category_in, payment_status='partial')
        self._create_invoice(category=self.category_in, payment_status='paid')
        self._create_invoice(category=self.category_out, payment_status='unpaid')
        resp = self.client.get(reverse('receivable'))
        self.assertEqual(resp.data['count'], 2)

    def test_payable_filter_by_account_side(self):
        self.auth()
        self._create_invoice(
            category=self.category_out,
            payment_status='unpaid',
            account_side=self.customer_side,
        )
        self._create_invoice(
            category=self.category_out,
            payment_status='unpaid',
            account_side=self.supplier_side,
        )
        resp = self.client.get(reverse('payable'), {
            'account_side': self.customer_side.pk,
        })
        self.assertEqual(resp.data['count'], 1)


# ─── Issue Customer Invoice Tests ────────────────────────────────────────────

class IssueCustomerInvoiceTests(AccountingTestBase):

    def test_issue_customer_invoice_success(self):
        self.auth()
        data = {
            'account_side_id': self.customer_side.pk,
            'category_id': self.category_out.pk,
            'amount': 5000000,
            'discount': 0,
            'items': [
                {
                    'title': 'اکانت سونی',
                    'quantity': 1,
                    'unit_price': 5000000,
                    'discount': 0,
                },
            ],
        }
        resp = self.client.post(reverse('issue-customer-invoice'), data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['status'], 'primary')
        self.assertEqual(len(resp.data['items']), 1)

    def test_issue_customer_wrong_direction_returns_400(self):
        self.auth()
        data = {
            'account_side_id': self.customer_side.pk,
            'category_id': self.category_in.pk,
            'amount': 5000000,
            'items': [
                {
                    'title': 'آیتم تست',
                    'quantity': 1,
                    'unit_price': 5000000,
                },
            ],
        }
        resp = self.client.post(reverse('issue-customer-invoice'), data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('category_id', resp.data)

    def test_issue_customer_unauthenticated(self):
        self.unauth()
        resp = self.client.post(reverse('issue-customer-invoice'), {}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_issue_customer_missing_items_returns_400(self):
        self.auth()
        data = {
            'account_side_id': self.customer_side.pk,
            'category_id': self.category_out.pk,
            'amount': 5000000,
        }
        resp = self.client.post(reverse('issue-customer-invoice'), data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


# ─── Issue Supplier Invoice Tests ────────────────────────────────────────────

class IssueSupplierInvoiceTests(AccountingTestBase):

    def test_issue_supplier_invoice_success(self):
        self.auth()
        data = {
            'account_side_id': self.supplier_side.pk,
            'category_id': self.category_in.pk,
            'amount': 3000000,
            'items': [
                {
                    'title': 'قطعه یدکی',
                    'quantity': 2,
                    'unit_price': 1500000,
                },
            ],
        }
        resp = self.client.post(reverse('issue-supplier-invoice'), data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['status'], 'primary')

    def test_issue_supplier_non_supplier_account_returns_400(self):
        self.auth()
        data = {
            'account_side_id': self.customer_side.pk,
            'category_id': self.category_in.pk,
            'amount': 3000000,
            'items': [
                {
                    'title': 'آیتم',
                    'quantity': 1,
                    'unit_price': 3000000,
                },
            ],
        }
        resp = self.client.post(reverse('issue-supplier-invoice'), data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('account_side_id', resp.data)

    def test_issue_supplier_wrong_direction_returns_400(self):
        self.auth()
        data = {
            'account_side_id': self.supplier_side.pk,
            'category_id': self.category_out.pk,
            'amount': 3000000,
            'items': [
                {
                    'title': 'آیتم',
                    'quantity': 1,
                    'unit_price': 3000000,
                },
            ],
        }
        resp = self.client.post(reverse('issue-supplier-invoice'), data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('category_id', resp.data)


# ─── Pay Customer / Supplier Tests ──────────────────────────────────────────

class PayCustomerTests(AccountingTestBase):

    def test_pay_customer_success(self):
        self.auth()
        inv = self._create_invoice()
        data = {
            'invoice_id': inv.pk,
            'account_side_id': self.customer_side.pk,
            'bank_account_id': self.bank_account.pk,
            'amount': 2000000,
            'description': 'پرداخت به مشتری',
        }
        resp = self.client.post(reverse('pay-customer'), data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['direction'], 'out')

    def test_pay_customer_with_supplier_returns_400(self):
        self.auth()
        inv = self._create_invoice()
        data = {
            'invoice_id': inv.pk,
            'account_side_id': self.supplier_side.pk,
            'bank_account_id': self.bank_account.pk,
            'amount': 2000000,
        }
        resp = self.client.post(reverse('pay-customer'), data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('account_side_id', resp.data)

    def test_pay_customer_unauthenticated(self):
        self.unauth()
        resp = self.client.post(reverse('pay-customer'), {}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class PaySupplierTests(AccountingTestBase):

    def test_pay_supplier_success(self):
        self.auth()
        inv = self._create_invoice()
        data = {
            'invoice_id': inv.pk,
            'account_side_id': self.supplier_side.pk,
            'bank_account_id': self.bank_account.pk,
            'amount': 3000000,
        }
        resp = self.client.post(reverse('pay-supplier'), data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['direction'], 'out')

    def test_pay_supplier_with_customer_returns_400(self):
        self.auth()
        inv = self._create_invoice()
        data = {
            'invoice_id': inv.pk,
            'account_side_id': self.customer_side.pk,
            'bank_account_id': self.bank_account.pk,
            'amount': 3000000,
        }
        resp = self.client.post(reverse('pay-supplier'), data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('account_side_id', resp.data)


# ─── Choices Tests ───────────────────────────────────────────────────────────

class ChoicesTests(AccountingTestBase):

    def test_invoice_categories_choices(self):
        self.auth()
        resp = self.client.get(reverse('choices-invoice-categories'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data), 2)
        self.assertIn('title', resp.data[0])
        self.assertIn('direction', resp.data[0])

    def test_bank_accounts_choices(self):
        self.auth()
        resp = self.client.get(reverse('choices-bank-accounts'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data), 1)
        self.assertIn('title', resp.data[0])

    def test_account_sides_choices(self):
        self.auth()
        resp = self.client.get(reverse('choices-account-sides'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data), 3)
        self.assertIn('display_name', resp.data[0])
        self.assertIn('type', resp.data[0])

    def test_invoice_statuses_choices(self):
        self.auth()
        resp = self.client.get(reverse('choices-invoice-statuses'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        values = [c['value'] for c in resp.data]
        self.assertIn('draft', values)
        self.assertIn('primary', values)
        self.assertIn('finalize', values)

    def test_payment_statuses_choices(self):
        self.auth()
        resp = self.client.get(reverse('choices-payment-statuses'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        values = [c['value'] for c in resp.data]
        self.assertIn('unpaid', values)
        self.assertIn('partial', values)
        self.assertIn('paid', values)

    def test_transaction_directions_choices(self):
        self.auth()
        resp = self.client.get(reverse('choices-transaction-directions'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        values = [c['value'] for c in resp.data]
        self.assertIn('in', values)
        self.assertIn('out', values)

    def test_content_types_choices(self):
        self.auth()
        resp = self.client.get(reverse('choices-content-types'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp.data, list)

    def test_choices_unauthenticated(self):
        self.unauth()
        resp = self.client.get(reverse('choices-invoice-statuses'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_choices_no_pagination(self):
        self.auth()
        resp = self.client.get(reverse('choices-invoice-categories'))
        self.assertNotIn('count', resp.data)
        self.assertIsInstance(resp.data, list)
