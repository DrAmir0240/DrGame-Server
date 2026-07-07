from django.urls import path

from accounting import views

urlpatterns = [

    # ==================== Daily Ledger ====================
    path('daily-invoices/', views.DailyInvoiceListView.as_view(), name='daily-invoices'),
    path('daily-transactions/', views.DailyTransactionListView.as_view(), name='daily-transactions'),

    # ==================== Payments & Receipts ====================
    path('payments/', views.PaymentListView.as_view(), name='payments'),
    path('receipts/', views.ReceiptListView.as_view(), name='receipts'),

    # ==================== Payable & Receivable ====================
    path('payable/', views.PayableListView.as_view(), name='payable'),
    path('receivable/', views.ReceivableListView.as_view(), name='receivable'),

    # ==================== Invoice CRUD ====================
    path('invoices/issue-customer/', views.IssueCustomerInvoiceView.as_view(), name='issue-customer-invoice'),
    path('invoices/issue-supplier/', views.IssueSupplierInvoiceView.as_view(), name='issue-supplier-invoice'),
    path('invoices/', views.InvoiceListCreateView.as_view(), name='invoice-list-create'),
    path('invoices/<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice-detail'),

    # ==================== Transaction CRUD ====================
    path('transactions/pay-customer/', views.PayCustomerView.as_view(), name='pay-customer'),
    path('transactions/pay-supplier/', views.PaySupplierView.as_view(), name='pay-supplier'),
    path('transactions/', views.TransactionListCreateView.as_view(), name='transaction-list-create'),
    path('transactions/<int:pk>/', views.TransactionDetailView.as_view(), name='transaction-detail'),

    # ==================== Choices ====================
    path('choices/invoice-categories/', views.InvoiceCategoryChoicesView.as_view(), name='choices-invoice-categories'),
    path('choices/bank-accounts/', views.BankAccountChoicesView.as_view(), name='choices-bank-accounts'),
    path('choices/account-sides/', views.AccountSideChoicesView.as_view(), name='choices-account-sides'),
    path('choices/invoice-statuses/', views.InvoiceStatusChoicesView.as_view(), name='choices-invoice-statuses'),
    path('choices/payment-statuses/', views.PaymentStatusChoicesView.as_view(), name='choices-payment-statuses'),
    path('choices/transaction-directions/', views.TransactionDirectionChoicesView.as_view(), name='choices-transaction-directions'),
    path('choices/content-types/', views.ContentTypeChoicesView.as_view(), name='choices-content-types'),

]
