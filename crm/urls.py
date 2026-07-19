from django.urls import path

from crm import views

urlpatterns = [
    path('customers/', views.CustomerListView.as_view(), name='customer-list'),
    path('customers/b2b/', views.B2BCustomerListView.as_view(), name='b2b-customer-list'),
    # Customer CRUD
    path('customers/create/', views.CustomerCreateView.as_view(), name='customer-create'),
    path('customers/<int:pk>/', views.CustomerRetrieveUpdateDestroyView.as_view(), name='customer-detail'),
    path('customers/<int:customer_id>/b2b/', views.B2BProfileCreateView.as_view(), name='b2b-create'),
    path('customers/<int:customer_id>/b2b/detail/', views.B2BProfileRetrieveUpdateDestroyView.as_view(),
         name='b2b-detail'),
    path('customers/<int:customer_id>/transactions/', views.CustomerTransactionListView.as_view(),
         name='customer-transactions'),
    path('customers/<int:customer_id>/invoices/', views.CustomerInvoiceListView.as_view(), name='customer-invoices'),
    path('customers/<int:customer_id>/summary/', views.CustomerSummaryView.as_view(), name='customer-summary'),
    path('customer/send-sms-service/', views.CustomerSendSmsService.as_view(), name='customer-send-sms-service'),

    # discount logic
    # tbc

]
