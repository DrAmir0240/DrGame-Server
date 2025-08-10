from django.urls import path
from employees import views
from employees.views import EmployeeListAdd, EmployeeDetail

urlpatterns = [
    # ==================== Personal Views ====================
    # -------------------- Sony Accounts --------------------
    path('personal/sony-accounts/', views.EmployeePanelOwnedSonyAccountList.as_view(), name='owned-sony-account-list'),
    path('personal/sony-accounts/<int:pk>/', views.EmployeePanelSonyAccountDetail.as_view(),
         name='sony-account-detail'),
    path('personal/sony-accounts/choices', views.EmployeePanelSonyAccountChoices.as_view(),
         name='sony-accounts-choices'),
    path('personal/sony-accounts/order/<int:order_id>/', views.EmployeePanelSonyAccountByOrderGamesView.as_view(),
         name='sony-account-by-order-games'),

    # -------------------- Orders --------------------
    path('personal/game-orders/owned/', views.EmployeePanelOwnedGameOrderList.as_view(), name='owned-game-order-list'),

    # -------------------- Tasks --------------------
    path('personal/tasks/', views.EmployeePanelTaskList.as_view(), name='task-list'),
    path('personal/tasks/<int:pk>/', views.EmployeePanelTaskDetail.as_view(), name='task-detail'),
    path('personal/tasks/add/', views.EmployeePanelAddTask.as_view(), name='task-add'),

    # -------------------- Transactions --------------------
    path('personal/transactions/owned/', views.EmployeePanelOwnedTransactionList.as_view(),
         name='owned-transaction-list'),
    path('personal/transactions/owned/<int:pk>/', views.EmployeePanelOwnedTransactionDetail.as_view(),
         name='owned-transaction-detail'),

    # ==================== Product Views ====================
    path('products/', views.EmployeePanelProductList.as_view(), name='product-list'),
    path('products/<int:pk>/', views.EmployeePanelProductDetail.as_view(), name='product-detail'),
    path('products/add/', views.EmployeePanelAddProduct.as_view(), name='product-add'),
    path('products/choices', views.EmployeePanelProductChoices.as_view(), name='product-choices'),

    # ==================== SonyAccounts Views ====================
    path('sony-accounts/new/', views.EmployeePanelGetNewSonyAccount.as_view(), name='sony-account-new'),
    path('sony-accounts/', views.EmployeePanelSonyAccountList.as_view(), name='sony-account-list'),

    # ==================== ProductOrders Views ====================
    path('product-orders/', views.EmployeePanelProductOrderList.as_view(), name='product-order-list'),
    path('product-orders/<int:pk>/', views.EmployeePanelProductOrderDetail.as_view(), name='product-order-detail'),
    path('product-orders/add/', views.EmployeePanelAddOrder.as_view(), name='product-order-add'),
    path('product-orders/choices/', views.EmployeePanelProductOrderChoices.as_view(), name='product-order-choices'),
    # ==================== GameOrders Views ====================
    path('game-orders/', views.EmployeePanelGameOrder.as_view(), name='accepted-game-order-list'),
    path('game-orders/<int:pk>/', views.EmployeePanelGameOrderDetail.as_view(), name='game-order-detail'),
    path('game-orders/choices/', views.EmployeePanelGameOrderChoices.as_view(), name='product-order-choices'),

    # ==================== RepairOrders Views ====================
    path('repair-orders/', views.EmployeePanelRepairOrderList.as_view(), name='repair-order-list'),
    path('repair-orders/<int:pk>/', views.EmployeePanelRepairOrderDetail.as_view(), name='repair-order-detail'),

    # ==================== Transactions Views ====================
    path('transactions/', views.EmployeePanelTransactionList.as_view(), name='transaction-list'),
    path('transactions/<int:pk>/', views.EmployeePanelTransactionDetail.as_view(), name='transaction-detail'),
    path('transactions/in/add/', views.EmployeePanelAddIncomingTransactionView.as_view(), name='in-transaction-add'),
    path('transactions/out/add/', views.EmployeePanelAddOutGoingTransaction.as_view(), name='out-transaction-add'),
    path('transactions/choices/users/', views.EmployeePanelTransactionPayerReceiverChoices.as_view(), name='user-choices'),
    path('transaction/choices/<int:customer_id>/<str:order_type>/', views.EmployeePanelTransactionOrderChoices.as_view(), name='order-choices'),

    # ==================== Employee Views ====================
    path('user/create/', views.UserCreat.as_view(), name='user-create'),
    path('', views.EmployeeListAdd.as_view(), name='list-add'),
    path('<int:pk>/', views.EmployeeDetail.as_view(), name='employee-detail'),

    # ==================== Customer Views ====================
    path('customer/list-add/', views.CustomerListCreate.as_view(), name='customer-list-add'),
    path('customer/<int:pk>/', views.CustomerDetail.as_view(), name='customer-detail'),

    # ==================== GameStore Views ====================
    path('game/list-add/', views.EmployeeGameListCreate.as_view(), name='game-list-add'),
    path('game/<int:pk>/', views.EmployeeGameDetail.as_view(), name='game-detail'),

    # ==================== Blog Views ====================
    path('blog/list-add/', views.EmployeeBlogListCreate.as_view(), name='blog-list-add'),
    path('blog/<str:slug>/', views.EmployeeBlogDetail.as_view(), name='blog-detail'),

    # ==================== Docs Views ====================
    path('docs/', views.EmployeePanelDocument.as_view(), name='docs-list-add'),
    path('docs/<int:pk>', views.EmployeePanelDetail.as_view(), name='docs-detail'),
    path('docs/category/', views.EmployeePanelDocCategory.as_view(), name='docs-category-list-add'),

    # ==================== RepairMan Views ====================

    # ==================== RepairManPanel Views ====================

]
