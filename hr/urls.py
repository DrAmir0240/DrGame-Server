from django.urls import path
from hr import views

urlpatterns = [
    # ==================== Personal Views ====================
    # -------------------- Requests --------------------
    path('personal/requests/', views.EmployeePanelPersonalRequests.as_view(), name='personal-requests'),
    path('personal/requests/<int:pk>/', views.EmployeePanelPersonalRequestsDetail.as_view(),
         name='personal-requests-detail'),



    # -------------------- Orders --------------------
    path('personal/game-orders/owned/', views.EmployeePanelOwnedGameOrderList.as_view(), name='owned-game-order-list'),
    path('personal/game-orders/owned/<int:pk>/', views.EmployeePanelOwnedGameOrderDetail.as_view(),
         name='owned-game-order-detail'),
    path('personal/telegram-orders/', views.EmployeePanelPersonalTelegramOrderList.as_view(), name='telegram-orders'),




    # ==================== Employee Views ====================
    path('user/create/', views.UserCreat.as_view(), name='user-create'),
    path('', views.EmployeeListAdd.as_view(), name='list-add'),
    path('<int:pk>/', views.EmployeeDetail.as_view(), name='employee-detail'),
    path('<int:pk>/deposit/', views.EmployeeDeposit.as_view(), name='employee-deposit'),
    path('send-sms-service/', views.EmployeeSendSmsService.as_view(), name='employee-send-sms-service'),
    path('resume/', views.EmployeeResumeList.as_view(), name='resume-list'),
    path('resume/<int:pk>', views.EmployeeResumeDelete.as_view(), name='resume-delete'),




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



    # ==================== Requests Views ====================
    path('requests/', views.EmployeePanelRequests.as_view(), name='requests'),
    path('requests/<int:pk>/', views.EmployeePanelRequestsDetail.as_view(), name='requests-detail'),
    path('requests/choices/', views.EmployeePanelRequestChoices.as_view(), name='requests-choices'),
    # ==================== End Views ====================

]
