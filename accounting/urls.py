from django.urls import path

from accounting import views

urlpatterns = [
    # ==================== Personal Views ====================
    path('verify-payment', views.ZarinpalCallbackView.as_view(), name="zarinpal-callback"),

    # ==================== ProductOrder Views ====================
    path('orders/create/', views.OrderCreate.as_view(), name='make-order'),
    path('orders/<int:id>/', views.OrderDetail.as_view(), name='order-detail'),
    path('orders/request-payment/<int:order_id>/', views.RequestPaymentForOrder.as_view(),
         name='order-request-payment'),

    # ==================== GameOrder Views ====================
    path('game-orders/create/', views.GameOrderCreate.as_view(), name='make-game-order'),
    path('game-orders/<int:id>/', views.GameOrderDetail.as_view(), name='game-order-detail'),
    path('game-orders/<int:order_id>/assign-drgame-delivery/', views.AssignDeliveryToDrGameForGameOrder.as_view(),
         name='assign_game-order-delivery_to_drgame'),
    path('game-orders/request-payment/<int:game_order_id>/', views.RequestPaymentForGameOrder.as_view(),
         name='game-order-request-payment'),
    path('game-orders/<int:pk>/delivered-to-customer/', views.DeliveredGameOrderToCustomer.as_view(),
         name='delivered-game-order-to-customer'),

    # ==================== RepairOrder Views ====================
    path('repair-orders/create/', views.RepairOrderCreate.as_view(), name='make-repair-order'),
    path('repair-orders/<int:id>/', views.RepairOrderDetail.as_view(), name='repair-order-detail'),
    path('reapir-orders/<int:order_id>/assign-drgame-delivery/', views.AssignDeliveryToDrGameForRepairOrder.as_view(),
         name='assign-repair-order-delivery_to_drgame'),
    path('repair-orders/request-payment/<int:repair_order_id>/', views.RequestPaymentForRepairOrder.as_view(),
         name='repair-order-request-payment'),
    path('repair-orders/<int:pk>/delivered-to-customer/', views.DeliveredRepairOrderToCustomer.as_view(),
         name='delivered-repair-order-to-customer'),
    # ==================== CourseOrder Views ====================
    path('course-orders/create/', views.CourseOrderCreate.as_view(), name='course-make-order'),
    path('course-orders/<int:id>/', views.CourseOrderDetail.as_view(), name='course-order-detail'),
    path('course-orders/request-payment/<int:order_id>/', views.RequestPaymentForCourseOrder.as_view(),
         name='course-order-request-payment'),
    # -------------------- Transactions --------------------
    path('personal/transactions/balance/', views.EmployeePanelSelfBalance.as_view(),
         name='employee-balance'),
    path('personal/transactions/owned/out/', views.EmployeePanelOwnedOutTransactionList.as_view(),
         name='owned-transaction-list'),
    path('personal/transactions/owned/out/<int:pk>/', views.EmployeePanelOwnedOutTransactionDetail.as_view(),
         name='owned-transaction-detail'),
    path('personal/transactions/owned/in/', views.EmployeePanelOwnedInTransactionList.as_view(),
         name='owned-transaction-list'),
    path('personal/transactions/owned/in/<int:pk>/', views.EmployeePanelOwnedInTransactionDetail.as_view(),
         name='owned-transaction-detail'),
    # ==================== Transactions Views ====================
    path('transactions/in/', views.EmployeePanelInTransactionList.as_view(), name='transaction-in-list'),
    path('transactions/out/', views.EmployeePanelOutTransactionList.as_view(), name='transaction-out-list'),
    path('transactions/<int:pk>/', views.EmployeePanelTransactionDetail.as_view(), name='transaction-detail'),
    path('transactions/in/add/', views.EmployeePanelAddIncomingTransactionView.as_view(), name='in-transaction-add'),
    path('transactions/out/add/', views.EmployeePanelAddOutGoingTransaction.as_view(), name='out-transaction-add'),
    path('transactions/choices/users/', views.EmployeePanelTransactionPayerReceiverChoices.as_view(),
         name='user-choices'),
    path('transaction/choices/<int:customer_id>/<str:order_type>/',
         views.EmployeePanelTransactionOrderChoices.as_view(), name='order-choices'),
]
