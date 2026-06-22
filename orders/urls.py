from django.urls import path

from orders import views

urlpatterns = [
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
         views.AssignDeliveryToCustomerForRepairOrder.as_view(),
         name='assign-delivery-to-customer-for-repair-orders'),
    path("repair-orders/<int:repair_order_id>/create-transaction/",
         views.EmployeePanelCreateRepairOrderTransactionView.as_view(),
         name="create-repair-order-transaction"),
    # ==================== RepairOrders Views ====================
    path('telegram-orders/', views.EmployeePanelTelegramOrderList.as_view(), name='telegram-orders'),

    # ==================== CourseOrders Views ====================
    path('course-orders/', views.EmployeePanelCourseOrdersList.as_view(), name='course-order-list'),
    path('course-orders/<int:pk>/', views.EmployeePanelCourseOrdersDetail.as_view(), name='course-order-detail'),

]
