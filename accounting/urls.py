from django.urls import path

from accounting import views

urlpatterns = [
    # choices for invoices and transaction and account sides
    path('choices/', views.InvoiceDropdownView.as_view(), name="choices-view"),

    # repair order report
    path('repair/report/', views.RepairOrderReportView.as_view()),
    path('repair/report/weekly/', views.RepairOrderWeeklyReportView.as_view()),

    # product order report
    path('product/report/', views.ProductOrderReportView.as_view()),
    path('product/report/weekly/', views.ProductOrderWeeklyReportView.as_view()),
    path('product/report/by-category/', views.ProductOrderByCategoryReportView.as_view()),

    # sony account report filtered by type and amount
    path('sony/report/', views.SonyAccountOrderReportView.as_view()),
    path('sony/report/weekly/', views.SonyAccountOrderWeeklyReportView.as_view()),

    # financial reports base on graph and pi chart
    path('report/income/', views.IncomeReportView.as_view()),
    path('report/income/weekly/', views.IncomeWeeklyReportView.as_view()),
    path('report/expense/', views.ExpenseReportView.as_view()),
    path('report/expense/weekly/', views.ExpenseWeeklyReportView.as_view()),
    path('report/net/', views.NetFinancialReportView.as_view()),

    # daily notebook : daily invoice and transaction and account side crud payable and receivable
    # دفتر روزانه
    path('daily/transactions/', views.DailyTransactionListView.as_view()),
    path('daily/transactions/<int:pk>/', views.DailyTransactionDetailView.as_view()),
    path('daily/transactions/<int:pk>/edit/', views.DailyTransactionUpdateView.as_view()),
    path('daily/transactions/<int:pk>/delete/', views.DailyTransactionDeleteView.as_view()),

    path('daily/invoices/', views.DailyInvoiceListView.as_view()),
    path('daily/invoices/<int:pk>/', views.DailyInvoiceDetailView.as_view()),
    path('daily/invoices/<int:pk>/edit/', views.DailyInvoiceUpdateView.as_view()),
    path('daily/invoices/<int:pk>/delete/', views.DailyInvoiceDeleteView.as_view()),


    # accounting : all incomes and all outcomes and salary part and invoice lists
    # درآمد
    path('income/', views.IncomeInvoiceListView.as_view()),
    path('income/<int:pk>/', views.IncomeInvoiceDetailView.as_view()),
    path('income/create/', views.IncomeInvoiceCreateView.as_view()),
    path('income/<int:pk>/edit/', views.IncomeInvoiceUpdateView.as_view()),
    path('income/<int:pk>/delete/', views.IncomeInvoiceDeleteView.as_view()),

    # هزینه
    path('expense/', views.ExpenseInvoiceListView.as_view()),
    path('expense/<int:pk>/', views.ExpenseInvoiceDetailView.as_view()),
    path('expense/create/', views.ExpenseInvoiceCreateView.as_view()),
    path('expense/<int:pk>/edit/', views.ExpenseInvoiceUpdateView.as_view()),
    path('expense/<int:pk>/delete/', views.ExpenseInvoiceDeleteView.as_view()),

    # فیش حقوقی
    path('payroll/', views.PayrollInvoiceListView.as_view()),
    path('payroll/<int:pk>/', views.PayrollInvoiceDetailView.as_view()),
    path('payroll/create/', views.PayrollInvoiceCreateView.as_view()),
    path('payroll/<int:pk>/edit/', views.PayrollInvoiceUpdateView.as_view()),
    path('payroll/<int:pk>/delete/', views.PayrollInvoiceDeleteView.as_view()),

    # فاکتور خرید
    path('purchase/', views.PurchaseInvoiceListView.as_view()),
    path('purchase/<int:pk>/', views.PurchaseInvoiceDetailView.as_view()),
    path('purchase/create/', views.PurchaseInvoiceCreateView.as_view()),
    path('purchase/<int:pk>/edit/', views.PurchaseInvoiceUpdateView.as_view()),
    path('purchase/<int:pk>/delete/', views.PurchaseInvoiceDeleteView.as_view()),

    # فاکتور فروش
    path('sales/', views.SalesInvoiceListView.as_view()),
    path('sales/<int:pk>/', views.SalesInvoiceDetailView.as_view()),
    path('sales/create/', views.SalesInvoiceCreateView.as_view()),
    path('sales/<int:pk>/edit/', views.SalesInvoiceUpdateView.as_view()),
    path('sales/<int:pk>/delete/', views.SalesInvoiceDeleteView.as_view()),

]
