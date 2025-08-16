from django.urls import path

from payments import views

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
    path('game-orders/<int:order_id>/delivered-to-customer/', views.DeliveredGameOrderToCustomer.as_view(),
         name='delivered-game-order-to-customer'),

    # ==================== RepairOrder Views ====================
    path('repair-orders/create/', views.RepairOrderCreate.as_view(), name='make-repair-order'),
    path('repair-orders/<int:id>/', views.RepairOrderDetail.as_view(), name='repair-order-detail'),
    path('reapir-orders/<int:order_id>/assign-drgame-delivery/', views.AssignDeliveryToDrGameForRepairOrder.as_view(),
         name='assign-repair-order-delivery_to_drgame'),
    path('repair-orders/request-payment/<int:repair_order_id>/', views.RequestPaymentForRepairOrder.as_view(),
         name='repair-order-request-payment'),
    path('repair-orders/<int:order_id>/delivered-to-customer/', views.DeliveredRepairOrderToCustomer.as_view(),
         name='delivered-repair-order-to-customer'),
    # ==================== RepairOrder Views ====================
    path('course-orders/create/', views.CourseOrderCreate.as_view(), name='course-make-order'),
    path('course-orders/<int:id>/', views.CourseOrderDetail.as_view(), name='course-order-detail'),
    path('course-orders/request-payment/<int:order_id>/', views.RequestPaymentForCourseOrder.as_view(),
         name='course-order-request-payment'),
]
