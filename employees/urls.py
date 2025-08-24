from django.urls import path
from employees import views
from employees.views import EmployeeListAdd, EmployeeDetail

urlpatterns = [
    # ==================== Personal Views ====================
    # -------------------- Requests --------------------
    path('personal/requests/', views.EmployeePanelPersonalRequests.as_view(), name='personal-requests'),
    path('personal/requests/<int:pk>/', views.EmployeePanelPersonalRequestsDetail.as_view(),
         name='personal-requests-detail'),

    # -------------------- Sony Accounts --------------------
    path('personal/sony-accounts/', views.EmployeePanelOwnedSonyAccountList.as_view(), name='owned-sony-account-list'),
    path('personal/sony-accounts/<int:pk>/', views.EmployeePanelSonyAccountDetail.as_view(),
         name='sony-account-detail'),
    path('personal/sony-accounts/choices/', views.EmployeePanelSonyAccountChoices.as_view(),
         name='sony-accounts-choices'),

    # -------------------- Orders --------------------
    path('personal/game-orders/owned/', views.EmployeePanelOwnedGameOrderList.as_view(), name='owned-game-order-list'),
    path('personal/game-orders/owned/<int:pk>/', views.EmployeePanelOwnedGameOrderDetail.as_view(),
         name='owned-game-order-detail'),

    # -------------------- Tasks --------------------
    path('personal/tasks/', views.EmployeePanelTaskList.as_view(), name='personal-task-list'),
    path('personal/tasks/<int:pk>/', views.EmployeePanelTaskDetail.as_view(), name='personal-task-detail'),
    path('personal/tasks/add/', views.EmployeePanelAddTask.as_view(), name='personal-task-add'),

    # -------------------- Transactions --------------------
    path('personal/transactions/owned/out/', views.EmployeePanelOwnedOutTransactionList.as_view(),
         name='owned-transaction-list'),
    path('personal/transactions/owned/out/<int:pk>/', views.EmployeePanelOwnedOutTransactionDetail.as_view(),
         name='owned-transaction-detail'),
    path('personal/transactions/owned/in/', views.EmployeePanelOwnedInTransactionList.as_view(),
         name='owned-transaction-list'),
    path('personal/transactions/owned/in/<int:pk>/', views.EmployeePanelOwnedInTransactionDetail.as_view(),
         name='owned-transaction-detail'),
    # ==================== TaskManager Views ====================
    path('tasks/', views.EmployeePanelOrganizeTaskListCreateView.as_view(), name='task-list-add'),
    path('tasks/<int:pk>/', views.EmployeePanelOrganizeTaskDetailView.as_view(), name='task-detail'),
    path('tasks/employees/', views.EmployeePanelOrganizeTaskChoices.as_view(), name='task-employee-list'),

    # ==================== Product Views ====================
    path('products/', views.EmployeePanelProductList.as_view(), name='product-list'),
    path('products/<int:pk>/', views.EmployeePanelProductDetail.as_view(), name='product-detail'),
    path('products/add/', views.EmployeePanelAddProduct.as_view(), name='product-add'),
    path('products/choices', views.EmployeePanelProductChoices.as_view(), name='product-choices'),

    # ==================== SonyAccounts Views ====================
    path('sony-accounts/new/', views.EmployeePanelGetNewSonyAccount.as_view(), name='sony-account-new'),
    path('sony-accounts/', views.EmployeePanelSonyAccountList.as_view(), name='sony-account-list'),
    path('sony-accounts/<int:pk>/', views.EmployeePanelSonyAccountDetail.as_view(), name='sony-account-detail'),

    # ==================== ProductOrders Views ====================
    path('product-orders/', views.EmployeePanelProductOrderList.as_view(), name='product-order-list'),
    path('product-orders/<int:pk>/', views.EmployeePanelProductOrderDetail.as_view(), name='product-order-detail'),
    path('product-orders/add/', views.EmployeePanelAddOrder.as_view(), name='product-order-add'),
    path("product-orders/<int:product_order_id>/create-transaction/",
         views.EmployeePanelCreateOrderTransactionView.as_view(),
         name="create-product-order-transaction"),
    path('product-orders/choices/', views.EmployeePanelProductOrderChoices.as_view(), name='product-order-choices'),
    # ==================== GameOrders Views ====================
    path('game-orders/', views.EmployeePanelGameOrder.as_view(), name='accepted-game-order-list'),
    path('game-orders/<int:pk>/', views.EmployeePanelGameOrderDetail.as_view(), name='game-order-detail'),
    path('game-orders/<int:order_id>/assign-delivery-to-customer/',
         views.AssignDeliveryToCustomerForGamedOrder.as_view(),
         name='assign-delivery-to-customer-for-game-orders'),
    path("game-orders/<int:game_order_id>/create-transaction/",
         views.EmployeePanelCreateGameOrderTransactionView.as_view(),
         name="create-game-order-transaction"),

    path('game-orders/choices/', views.EmployeePanelGameOrderChoices.as_view(), name='product-order-choices'),

    # ==================== RepairOrders Views ====================
    path('repair-orders/', views.EmployeePanelRepairOrderList.as_view(), name='repair-order-list-add'),
    path('repair-orders/<int:pk>/', views.EmployeePanelRepairOrderDetail.as_view(), name='repair-order-detail'),
    path('repair-orders/<int:order_id>/assign-delivery-to-customer/',
         views.AssignDeliveryToCustomerForGamedOrder.as_view(),
         name='assign-delivery-to-customer-for-repair-orders'),
    path("repair-orders/<int:repair_order_id>/create-transaction/",
         views.EmployeePanelCreateRepairOrderTransactionView.as_view(),
         name="create-repair-order-transaction"),

    # ==================== CourseOrders Views ====================
    path('course-orders/', views.EmployeePanelCourseOrdersList.as_view(), name='course-order-list'),
    path('course-orders/<int:pk>/', views.EmployeePanelCourseOrdersDetail.as_view(), name='course-order-detail'),

    # ==================== Transactions Views ====================
    path('transactions/', views.EmployeePanelTransactionList.as_view(), name='transaction-list'),
    path('transactions/<int:pk>/', views.EmployeePanelTransactionDetail.as_view(), name='transaction-detail'),
    path('transactions/in/add/', views.EmployeePanelAddIncomingTransactionView.as_view(), name='in-transaction-add'),
    path('transactions/out/add/', views.EmployeePanelAddOutGoingTransaction.as_view(), name='out-transaction-add'),
    path('transactions/choices/users/', views.EmployeePanelTransactionPayerReceiverChoices.as_view(),
         name='user-choices'),
    path('transaction/choices/<int:customer_id>/<str:order_type>/',
         views.EmployeePanelTransactionOrderChoices.as_view(), name='order-choices'),

    # ==================== Employee Views ====================
    path('user/create/', views.UserCreat.as_view(), name='user-create'),
    path('', views.EmployeeListAdd.as_view(), name='list-add'),
    path('<int:pk>/', views.EmployeeDetail.as_view(), name='employee-detail'),
    path('<int:pk>/deposit/', views.EmployeeDeposit.as_view(), name='employee-deposit'),
    path('send-sms-service/', views.EmployeeSendSmsService.as_view(), name='employee-send-sms-service'),
    path('resume/', views.EmployeeResumeList.as_view(), name='resume-list'),
    path('resume/<int:pk>', views.EmployeeResumeDelete.as_view(), name='resume-delete'),

    # ==================== Customer Views ====================
    path('customer/list-add/', views.CustomerListCreate.as_view(), name='customer-list-add'),
    path('customer/<int:pk>/', views.CustomerDetail.as_view(), name='customer-detail'),
    path('customer/<int:pk>/deposit/', views.CustomerDeposit.as_view(), name='customer-deposit'),
    path('customer/send-sms-service/', views.CustomerSendSmsService.as_view(), name='customer-send-sms-service'),

    # ==================== GameStore Views ====================
    path('game/list-add/', views.EmployeeGameListCreate.as_view(), name='game-list-add'),
    path('game/<int:pk>/', views.EmployeeGameDetail.as_view(), name='game-detail'),
    path('game/bulk-price-update/', views.GameBulkPriceUpdateView.as_view(), name='game-bulk-price-update'),

    # ==================== Blog Views ====================
    path('blog/list-add/', views.EmployeeBlogListCreate.as_view(), name='blog-list-add'),
    path('blog/<str:slug>/', views.EmployeeBlogDetail.as_view(), name='blog-detail'),

    # ==================== Docs Views ====================
    path('docs/', views.EmployeePanelDocument.as_view(), name='docs-list-add'),
    path('docs/<int:pk>', views.EmployeePanelDocumentDetail.as_view(), name='docs-detail'),
    path('docs/category/', views.EmployeePanelDocCategory.as_view(), name='docs-category-list-add'),

    # ==================== RealAssets Views ====================
    path('real-assets/', views.EmployeePanelRealAssets.as_view(), name='real-assets-list-add'),
    path('real-assets/<int:pk>', views.EmployeePanelRealAssetsDetail.as_view(), name='real-assets-detail'),
    path('real-assets/category/', views.EmployeePanelRealAssetsCategory.as_view(),
         name='real-assets-category-list-add'),

    # ==================== RepairMan Views ====================
    path('repairmans/', views.RepairManList.as_view(), name="repairman's-list-add"),
    path('repairmans/<int:pk>/', views.RepairmanDetail.as_view(), name="repairman's-detail"),
    path('repairmans/<int:pk>/deposit/', views.RepairmanDeposit.as_view(), name='repairman-deposit'),

    # ==================== RepairManPanel Views ====================
    path('repairman-panel/orders/', views.RepairManRepairOrderList.as_view(), name="repairman-panel-orders"),
    path('repairman-panel/orders/<int:pk>/', views.RepairManPanelRepairOrderDetail.as_view(),
         name="repairman-panel-order-detail"),
    path('repairman-panel/status/', views.RepairManPanelStatusChoices.as_view(), name="repairman-panel-status-choices"),
    path('repairman-panel/transactions/in/', views.RepairManPanelInTransactionList.as_view(),
         name="repairman-panel-in-transaction-list"),
    path('repairman-panel/transaction/out/', views.RepairManPanelOutTransactionList.as_view(),
         name="repairman-panel-out-transaction-list"),
    # ==================== Stats Views ====================
    path('stats/employee-tasks/', views.TaskStatsAPIView.as_view(), name="employee-task-stats"),
    path('stats/game-orders/', views.GameOrderStatsAPIView.as_view(), name="game-order-stats"),
    path('stats/game-orders/personal/', views.PersonalGameOrderStatsAPIView.as_view(),
         name="personal-game-order-stats"),
    path('stats/product-orders/', views.ProductOrderStatsAPIView.as_view(), name="product-order-stats"),
    path('stats/repair-orders/', views.RepairOrderStatsAPIView.as_view(), name="repair-order-stats"),
    path('stats/finance/', views.FinanceSummaryAPIView.as_view(), name="finance-stats"),
    path('stats/employees/', views.EmployeeStatsAPIView.as_view(), name="employees-stats"),
    path('stats/customers/', views.CustomerStatsAPIView.as_view(), name="customers-stats"),
    # ==================== Reports Views ====================
    path('reports/sell/', views.SellReportsAPIView.as_view(), name="sell-reports"),
    path('reports/finance/', views.FinanceReportsAPIView.as_view(), name="finance-reports"),
    path('reports/employee/', views.PerFormanceReportAPIView.as_view(), name="employee-reports"),
    path('reports/customer/', views.CustomerReportAPIView.as_view(), name="customer-reports"),
    path('requests/', views.EmployeePanelRequests.as_view(), name='requests'),
    path('requests/<int:pk>/', views.EmployeePanelRequestsDetail.as_view(), name='requests-detail'),
    path('requests/choices/', views.EmployeePanelRequestChoices.as_view(), name='requests-choices'),

]
